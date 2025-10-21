"""Production-grade pipeline builder for market data pipelines."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

# ---- Local config & errors ---------------------------------------------------
from .config import get_pipeline_config
from .errors import ConfigurationError

# ---- Pipeline primitives (soft imports for optional extras) ------------------
from .context import PipelineContext
from .pipeline import StreamingPipeline
from .operator.bars import SecondBarAggregator
from .operator.options import OptionsChainOperator
from .batcher.hybrid import HybridBatcher

# Sources
from .source.synthetic import SyntheticSource
try:
    from .source.replay import ReplaySource  # optional
except Exception:
    ReplaySource = None
try:
    from .source.ibkr import IBKRSource  # optional
except Exception:
    IBKRSource = None

# Sinks
from .sink.store import StoreSink
try:
    from .sink.kafka import KafkaSink  # optional
except Exception:
    KafkaSink = None
try:
    from .sink.database import DatabaseSink, DatabaseSinkSettings  # optional
except Exception:
    DatabaseSink = None
    DatabaseSinkSettings = None

# market_data_store async client (optional)
try:
    from market_data_store.async_client import AsyncBatchProcessor
except Exception:
    AsyncBatchProcessor = None

log = logging.getLogger("market_data_pipeline.pipeline_builder")


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------

def _map_backpressure(v: Optional[str]) -> str:
    """Map backpressure policy names to DatabaseSink expected values."""
    if not v:
        return "block"
    v = v.lower()
    return {"oldest": "drop_oldest", "newest": "drop_newest", "block": "block"}.get(v, v)


# ------------------------------------------------------------------------------
# Spec & overrides
# ------------------------------------------------------------------------------

@dataclass
class PipelineOverrides:
    """Override configuration for pipeline components."""
    
    # Source
    ticks_per_sec: Optional[int] = None       # synthetic/ibkr cap (aggregate)
    pacing_max_per_sec: Optional[int] = None  # token bucket rate
    pacing_burst: Optional[int] = None        # token bucket burst
    replay_path: Optional[str] = None         # replay file
    replay_speed: Optional[float] = None      # 1.0 = realtime, 0=as-fast-as-possible

    # Operator
    bar_window_sec: Optional[int] = None
    bar_allowed_lateness_sec: Optional[int] = None

    # Batcher
    batch_size: Optional[int] = None
    max_bytes: Optional[int] = None
    flush_ms: Optional[int] = None
    op_queue_max: Optional[int] = None
    drop_policy: Optional[str] = None         # "oldest" | "newest" | "block"

    # Sink
    sink_workers: Optional[int] = None
    sink_queue_max: Optional[int] = None
    kafka_bootstrap: Optional[str] = None
    kafka_topic: Optional[str] = None
    
    # Database-specific parameters
    database_vendor: Optional[str] = None
    database_timeframe: Optional[str] = None
    database_retry_max_attempts: Optional[int] = None
    database_retry_backoff_ms: Optional[int] = None
    database_url: Optional[str] = None
    
    # NEW: let CORE pass typed settings or a processor instance
    database_settings: Optional["DatabaseSinkSettings"] = None
    database_processor: Optional[Any] = None


@dataclass
class PipelineSpec:
    """Pipeline specification defining source, operator, and sink."""
    
    tenant_id: str
    pipeline_id: str

    source: str                 # "synthetic" | "replay" | "ibkr"
    symbols: List[str] = field(default_factory=list)  # synthetic/ibkr
    duration_sec: Optional[float] = None

    operator: str = "bars"      # "bars" | "options" (future)
    sink: str = "store"         # "store" | "kafka"

    overrides: PipelineOverrides = field(default_factory=PipelineOverrides)


# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------

def _cfg(config: Any, key: str, fallback: Any = None) -> Any:
    """Get config value from object or dict with a default."""
    if isinstance(config, dict):
        return config.get(key, fallback)
    return getattr(config, key, fallback)


def ensure_windows_selector_event_loop() -> None:
    """Force SelectorEventLoop on Windows to keep psycopg happy."""
    if sys.platform.startswith("win"):
        try:
            loop = asyncio.get_event_loop()
            if isinstance(loop, asyncio.ProactorEventLoop):  # type: ignore[attr-defined]
                loop.close()
                asyncio.set_event_loop(asyncio.SelectorEventLoop())
                log.info("Switched to SelectorEventLoop on Windows")
        except Exception:
            asyncio.set_event_loop(asyncio.SelectorEventLoop())
            log.info("Installed SelectorEventLoop on Windows")


# ------------------------------------------------------------------------------
# Builder
# ------------------------------------------------------------------------------

class PipelineBuilder:
    """
    Production-grade builder for StreamingPipeline.

    - Centralizes all knobs from config (and allows per-call overrides).
    - Validates optional dependencies (IBKR, Kafka, AMDS).
    - Returns a fully-wired StreamingPipeline with PipelineContext.
    """

    def __init__(self, config: Optional[Any] = None) -> None:
        self.cfg = config or get_pipeline_config()
        self._validate_config()

    # ------------------------- public API -------------------------------------

    def build(self, spec: PipelineSpec) -> StreamingPipeline:
        """Create a StreamingPipeline according to the spec + config."""
        self._validate_spec(spec)
        ctx = PipelineContext(tenant_id=spec.tenant_id, pipeline_id=spec.pipeline_id)

        # Source
        source = self._build_source(spec, ctx)

        # Operator
        operator = self._build_operator(spec)

        # Batcher
        batcher = self._build_batcher(spec)

        # Sink
        sink = self._build_sink(spec, ctx)

        pipe = StreamingPipeline(source=source, operator=operator, batcher=batcher, sink=sink, ctx=ctx)
        return pipe

    async def build_and_run(self, spec: PipelineSpec) -> None:
        """Convenience: build and run to completion (respects duration_sec)."""
        ensure_windows_selector_event_loop()
        pipeline = self.build(spec)
        try:
            await pipeline.run(duration_sec=spec.duration_sec)
        finally:
            # StreamingPipeline should close gracefully itself; this is belt & suspenders
            with contextlib.suppress(Exception):
                await pipeline.close()

    # ------------------------- internal builders ------------------------------

    def _build_source(self, spec: PipelineSpec, ctx: PipelineContext):
        src = spec.source.lower()
        ovr = spec.overrides

        pacing_rate = ovr.pacing_max_per_sec or _cfg(self.cfg, "pacing_max_per_sec", 1000)
        pacing_burst = ovr.pacing_burst or _cfg(self.cfg, "pacing_burst", pacing_rate)

        if src == "synthetic":
            rate = ovr.ticks_per_sec or _cfg(self.cfg, "ticks_per_sec", 100)
            if not spec.symbols:
                raise ConfigurationError("synthetic source requires symbols")
            return SyntheticSource(
                symbols=spec.symbols,
                ticks_per_sec=rate,
                pacing_budget=(pacing_rate, pacing_burst),
                ctx=ctx,
            )

        if src == "replay":
            if ReplaySource is None:
                raise ConfigurationError("ReplaySource not available (not installed)")
            path = ovr.replay_path or _cfg(self.cfg, "replay_path", None)
            if not path:
                raise ConfigurationError("replay source requires overrides.replay_path or config.replay_path")
            speed = ovr.replay_speed if ovr.replay_speed is not None else _cfg(self.cfg, "replay_speed", 1.0)
            return ReplaySource(path=path, speed=speed, ctx=ctx)  # type: ignore[arg-type]

        if src == "ibkr":
            if IBKRSource is None:
                raise ConfigurationError("IBKRSource not available (not installed)")
            if not spec.symbols:
                raise ConfigurationError("ibkr source requires symbols")
            # For IBKR we still cap aggregate messages/sec; IBKRSource should enforce per-connection limits.
            rate = ovr.ticks_per_sec or _cfg(self.cfg, "ticks_per_sec", 100)
            return IBKRSource(
                symbols=spec.symbols,
                ticks_per_sec=rate,
                pacing_budget=(pacing_rate, pacing_burst),
                ctx=ctx,
            )

        raise ConfigurationError(f"Unknown source type: {spec.source}")

    def _build_operator(self, spec: PipelineSpec):
        op = spec.operator.lower()
        ovr = spec.overrides

        win = ovr.bar_window_sec or _cfg(self.cfg, "bar_window_sec", 1)
        late = ovr.bar_allowed_lateness_sec if ovr.bar_allowed_lateness_sec is not None \
            else _cfg(self.cfg, "bar_allowed_lateness_sec", 0)

        if op == "bars":
            return SecondBarAggregator(window_sec=win, allowed_lateness_sec=late)
        if op == "options":
            # Phase-1 snapshots; greeks/pricers can be threaded later via overrides.
            return OptionsChainOperator(window_sec=win, allowed_lateness_sec=late)
        raise ConfigurationError(f"Unknown operator: {spec.operator}")

    def _build_batcher(self, spec: PipelineSpec):
        ovr = spec.overrides
        return HybridBatcher(
            max_rows=ovr.batch_size or _cfg(self.cfg, "batch_size", 500),
            max_bytes=ovr.max_bytes or _cfg(self.cfg, "max_bytes", 512_000),
            flush_ms=ovr.flush_ms or _cfg(self.cfg, "flush_ms", 100),
            op_queue_max=ovr.op_queue_max or _cfg(self.cfg, "op_queue_max", 8),
            drop_policy=(ovr.drop_policy or _cfg(self.cfg, "drop_policy", "oldest")).lower(),
        )

    def _build_sink(self, spec: PipelineSpec, ctx: PipelineContext):
        snk = spec.sink.lower()
        ovr = spec.overrides

        if snk == "store":
            if AsyncBatchProcessor is None:
                raise ConfigurationError("market_data_store AsyncBatchProcessor not installed")
            # Prefer async factory when available
            if hasattr(AsyncBatchProcessor, "from_env_async"):
                # Lazily create in a task to avoid blocking here; StoreSink will call into it,
                # but if your AMDS requires immediate construction, switch to await in a builder coroutine.
                bp = asyncio.get_event_loop().run_until_complete(AsyncBatchProcessor.from_env_async())  # type: ignore
            else:
                bp = AsyncBatchProcessor.from_env()  # type: ignore

            return StoreSink(
                bp,
                workers=ovr.sink_workers or _cfg(self.cfg, "sink_workers", 2),
                queue_max=ovr.sink_queue_max or _cfg(self.cfg, "sink_queue_max", 100),
                backpressure_policy=(ovr.drop_policy or _cfg(self.cfg, "drop_policy", "oldest")).lower(),
                ctx=ctx,
            )

        if snk == "kafka":
            if KafkaSink is None:
                raise ConfigurationError("KafkaSink not available (not installed)")
            bootstrap = ovr.kafka_bootstrap or _cfg(self.cfg, "kafka_bootstrap_servers", None)
            topic = ovr.kafka_topic or _cfg(self.cfg, "kafka_topic", None)
            if not bootstrap or not topic:
                raise ConfigurationError("kafka sink requires kafka_bootstrap and kafka_topic")
            return KafkaSink(
                bootstrap_servers=bootstrap,
                topic=topic,
                queue_max=ovr.sink_queue_max or _cfg(self.cfg, "sink_queue_max", 100),
                backpressure_policy=(ovr.drop_policy or _cfg(self.cfg, "drop_policy", "oldest")).lower(),
                ctx=ctx,
            )

        if snk == "database":
            if DatabaseSink is None:
                raise ConfigurationError("DatabaseSink not available (not installed)")

            bp = _map_backpressure(ovr.drop_policy or _cfg(self.cfg, "drop_policy", "block"))

            settings = ovr.database_settings or DatabaseSinkSettings(
                vendor=ovr.database_vendor or _cfg(self.cfg, "database_vendor", "market_data_pipeline"),
                timeframe=ovr.database_timeframe or _cfg(self.cfg, "database_timeframe", "1s"),
                workers=ovr.sink_workers or _cfg(self.cfg, "sink_workers", 2),
                queue_max=ovr.sink_queue_max or _cfg(self.cfg, "sink_queue_max", 200),
                backpressure_policy=bp,
                retry_max_attempts=ovr.database_retry_max_attempts or _cfg(self.cfg, "database_retry_max_attempts", 5),
                retry_backoff_ms=ovr.database_retry_backoff_ms or _cfg(self.cfg, "database_retry_backoff_ms", 50),
            )

            # If CORE passed settings, let overrides tweak a couple fields
            if ovr.sink_workers:
                settings.workers = ovr.sink_workers
            if ovr.sink_queue_max:
                settings.queue_max = ovr.sink_queue_max
            settings.backpressure_policy = bp  # ensure mapped value wins

            return DatabaseSink(
                tenant_id=spec.tenant_id,
                settings=settings,
                ctx=ctx,
                processor=ovr.database_processor,
                database_url=ovr.database_url or _cfg(self.cfg, "database_url", None),
            )

        raise ConfigurationError(f"Unknown sink: {spec.sink}")

    # ------------------------- validation -------------------------------------

    def _validate_config(self) -> None:
        # Gentle validation to catch obvious misconfig
        bs = _cfg(self.cfg, "batch_size", 500)
        if bs <= 0:
            raise ConfigurationError("batch_size must be > 0")
        flush = _cfg(self.cfg, "flush_ms", 100)
        if flush <= 0:
            raise ConfigurationError("flush_ms must be > 0")
        dq = _cfg(self.cfg, "sink_queue_max", 100)
        if dq <= 0:
            raise ConfigurationError("sink_queue_max must be > 0")

    def _validate_spec(self, spec: PipelineSpec) -> None:
        if not spec.tenant_id or not spec.pipeline_id:
            raise ConfigurationError("tenant_id and pipeline_id are required")
        if spec.source.lower() not in {"synthetic", "replay", "ibkr"}:
            raise ConfigurationError("source must be one of: synthetic, replay, ibkr")
        if spec.operator.lower() not in {"bars", "options"}:
            raise ConfigurationError("operator must be one of: bars, options")
        if spec.sink.lower() not in {"store", "kafka", "database"}:
            raise ConfigurationError("sink must be one of: store, kafka, database")


# ------------------------------------------------------------------------------
# Convenience API
# ------------------------------------------------------------------------------

def create_pipeline(
    tenant_id: str,
    pipeline_id: str,
    *,
    source: str,
    symbols: Optional[List[str]] = None,
    duration_sec: Optional[float] = None,
    operator: str = "bars",
    sink: str = "store",
    overrides: Optional[Union[Dict[str, Any], PipelineOverrides]] = None,
    config: Optional[Any] = None,
) -> StreamingPipeline:
    """
    Convenience function for one-off creation without touching dataclasses.
    """
    builder = PipelineBuilder(config=config)
    ov = overrides if isinstance(overrides, PipelineOverrides) else PipelineOverrides(**(overrides or {}))
    spec = PipelineSpec(
        tenant_id=tenant_id,
        pipeline_id=pipeline_id,
        source=source,
        symbols=symbols or [],
        duration_sec=duration_sec,
        operator=operator,
        sink=sink,
        overrides=ov,
    )
    return builder.build(spec)
