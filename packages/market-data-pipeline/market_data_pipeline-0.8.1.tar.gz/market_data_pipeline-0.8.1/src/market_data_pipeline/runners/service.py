"""Service runner for the market data pipeline."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..batcher import HybridBatcher
from ..config import get_config
from ..context import PipelineContext
from ..errors import ConfigurationError
from ..operator import SecondBarAggregator, Operator
from ..pipeline import StreamingPipeline
from ..sink import StoreSink
try:
    from ..sink import DatabaseSink, DatabaseSinkSettings  # type: ignore
except Exception:  # pragma: no cover
    DatabaseSink = None  # type: ignore
    DatabaseSinkSettings = None  # type: ignore
from ..source import SyntheticSource

# Optional imports (tolerate missing extras)
try:
    from ..source import ReplaySource, IBKRSource  # type: ignore
except Exception:  # pragma: no cover
    ReplaySource = None  # type: ignore
    IBKRSource = None  # type: ignore

try:
    # market_data_store async client
    from market_data_store.async_client import AsyncBatchProcessor  # type: ignore
except Exception:  # pragma: no cover
    AsyncBatchProcessor = None  # type: ignore


@dataclass
class PipelineSpec:
    tenant_id: str
    pipeline_id: str
    source_type: str
    symbols: List[str]
    rate: Optional[int] = None  # synthetic/ibkr
    replay_path: Optional[str] = None  # replay
    duration_sec: Optional[float] = None
    operator_type: str = "bars"  # "bars" | "options" (future)
    sink_type: str = "store"  # "store" | "kafka" | "database"
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineHandle:
    spec: PipelineSpec
    pipeline: StreamingPipeline
    task: asyncio.Task
    started: float


class PipelineService:
    """Service for managing multiple pipelines."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or get_config()
        self.pipelines: Dict[str, PipelineHandle] = {}
        self.running = False

        logging.basicConfig(
            level=getattr(logging, getattr(self.config, "log_level", "INFO")),
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
        self.logger = logging.getLogger("market_data_pipeline.service")

    async def start(self) -> None:
        if self.running:
            raise ConfigurationError("Service is already running")
        self.running = True
        self.logger.info("PipelineService started")

    async def stop(self) -> None:
        if not self.running:
            return
        self.logger.info("Stopping PipelineService (drain pipelines)")
        await asyncio.gather(
            *(self._stop_pipeline(pid) for pid in list(self.pipelines.keys())),
            return_exceptions=True,
        )
        self.running = False
        self.logger.info("PipelineService stopped")

    # --------- Public API ---------

    async def create_pipeline(self, spec: PipelineSpec) -> str:
        if not self.running:
            raise ConfigurationError("Service is not running")

        key = f"{spec.tenant_id}:{spec.pipeline_id}"
        if key in self.pipelines:
            raise ConfigurationError(f"Pipeline {key} already exists")

        pipeline = await self._build_pipeline(spec)
        task = asyncio.create_task(self._run_pipeline(key, pipeline, spec.duration_sec))
        self.pipelines[key] = PipelineHandle(
            spec=spec,
            pipeline=pipeline,
            task=task,
            started=asyncio.get_event_loop().time(),
        )
        self.logger.info(
            "Created pipeline %s (source=%s operator=%s sink=%s symbols=%d)",
            key,
            spec.source_type,
            spec.operator_type,
            spec.sink_type,
            len(spec.symbols),
        )
        return key

    async def delete_pipeline(self, key: str) -> None:
        if key not in self.pipelines:
            raise ConfigurationError(f"Pipeline {key} not found")
        await self._stop_pipeline(key)
        self.logger.info("Deleted pipeline %s", key)

    async def list_pipelines(self) -> List[str]:
        return list(self.pipelines.keys())

    async def get_pipeline_status(self, key: str) -> Dict[str, Any]:
        h = self.pipelines.get(key)
        if not h:
            raise ConfigurationError(f"Pipeline {key} not found")
        # Minimal, extend with operator/sink status() if implemented
        return {
            "pipeline_id": key,
            "tenant_id": h.spec.tenant_id,
            "source": h.spec.source_type,
            "operator": h.spec.operator_type,
            "sink": h.spec.sink_type,
            "symbols": h.spec.symbols,
            "running": not h.task.done(),
            "duration_sec": h.spec.duration_sec,
        }

    # --------- Internals ---------

    async def _stop_pipeline(self, key: str) -> None:
        h = self.pipelines.get(key)
        if not h:
            return
        try:
            await h.pipeline.close()
        except Exception as e:  # pragma: no cover
            self.logger.warning("Error closing pipeline %s: %s", key, e)
        try:
            h.task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await h.task
        except Exception:
            pass
        self.pipelines.pop(key, None)

    async def _run_pipeline(
        self, key: str, pipeline: StreamingPipeline, duration: Optional[float]
    ) -> None:
        try:
            await pipeline.run(duration_sec=duration)
            self.logger.info("Pipeline %s completed", key)
        except Exception as e:
            self.logger.error("Pipeline %s error: %s", key, e)
        finally:
            # Auto-remove on finish
            self.pipelines.pop(key, None)

    async def _build_pipeline(self, spec: PipelineSpec) -> StreamingPipeline:
        # Context
        ctx = PipelineContext(tenant_id=spec.tenant_id, pipeline_id=spec.pipeline_id)

        # Source
        source_type = spec.source_type.lower()
        if source_type == "synthetic":
            if spec.rate is None:
                raise ConfigurationError("Synthetic source requires 'rate'")
            source = SyntheticSource(
                symbols=spec.symbols,
                ticks_per_sec=spec.rate,
                pacing_budget=(spec.rate, spec.rate),
                ctx=ctx,
            )
        elif source_type == "replay":
            if ReplaySource is None:
                raise ConfigurationError("ReplaySource not available")
            if not spec.replay_path:
                raise ConfigurationError("Replay source requires 'replay_path'")
            source = ReplaySource(path=spec.replay_path, ctx=ctx)  # type: ignore
        elif source_type == "ibkr":
            if IBKRSource is None:
                raise ConfigurationError("IBKRSource not available")
            if spec.rate is None:
                # you may use rate to cap ms/s if desired; optional
                spec.rate = 100
            source = IBKRSource(symbols=spec.symbols, ctx=ctx)  # type: ignore
        else:
            raise ConfigurationError(f"Unknown source_type '{spec.source_type}'")

        # Operator
        op_type = spec.operator_type.lower()
        if op_type == "bars":
            operator: Operator = SecondBarAggregator(window_sec=1)
        else:
            # plug options/greeks operator when ready
            operator = SecondBarAggregator(window_sec=1)

        # Batcher
        cfg = self.config
        batcher = HybridBatcher(
            max_rows=getattr(cfg, "batch_size", 500),
            max_bytes=getattr(cfg, "max_bytes", 512_000),
            flush_ms=getattr(cfg, "flush_ms", 100),
            op_queue_max=getattr(cfg, "op_queue_max", 8),
            drop_policy=getattr(cfg, "drop_policy", "oldest"),
        )

        # Sink
        sink_type = spec.sink_type.lower()
        if sink_type == "store":
            if AsyncBatchProcessor is None:
                raise ConfigurationError(
                    "market_data_store AsyncBatchProcessor not installed"
                )
            bp = (
                await AsyncBatchProcessor.from_env_async()
                if hasattr(AsyncBatchProcessor, "from_env_async")
                else AsyncBatchProcessor.from_env()
            )  # type: ignore
            sink = StoreSink(
                bp,
                workers=getattr(cfg, "sink_workers", 2),
                queue_max=getattr(cfg, "sink_queue_max", 100),
                backpressure_policy=getattr(cfg, "drop_policy", "oldest"),
                ctx=ctx,
            )
        elif sink_type == "database":
            if DatabaseSink is None:
                raise ConfigurationError("DatabaseSink not available (not installed)")
            
            # Create settings with configuration overrides
            settings = DatabaseSinkSettings(
                vendor=getattr(cfg, "database_vendor", "market_data_pipeline"),
                timeframe=getattr(cfg, "database_timeframe", "1s"),
                workers=getattr(cfg, "sink_workers", 2),
                queue_max=getattr(cfg, "sink_queue_max", 200),
                backpressure_policy=getattr(cfg, "drop_policy", "block"),
                retry_max_attempts=getattr(cfg, "database_retry_max_attempts", 5),
                retry_backoff_ms=getattr(cfg, "database_retry_backoff_ms", 50),
            )
            
            sink = DatabaseSink(
                tenant_id=spec.tenant_id,
                settings=settings,
                ctx=ctx,
                database_url=getattr(cfg, "database_url", None),
            )
        else:
            raise ConfigurationError(f"Unknown sink_type '{spec.sink_type}'")

        from ..pipeline import StreamingPipeline  # local import to avoid cycles

        return StreamingPipeline(
            source=source, operator=operator, batcher=batcher, sink=sink, ctx=ctx
        )


# utility
import contextlib  # at bottom to keep the import list tidy
