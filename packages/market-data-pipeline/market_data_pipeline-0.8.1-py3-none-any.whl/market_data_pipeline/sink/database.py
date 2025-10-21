"""Production-grade database sink for market data persistence."""

from __future__ import annotations

import asyncio
import inspect
import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Iterable, Optional, Sequence

from .base import Sink
from .capabilities import SinkCapabilities
from ..context import PipelineContext
from ..types import Bar

log = logging.getLogger("market_data_pipeline.sink.database")

# --- Optional deps -------------------------------------------------------------
_AMDS = None
_AMDS_Bar = None
try:
    # mds_client (compat path)
    from mds_client import AMDS as _AMDS  # type: ignore
    from mds_client import Bar as _AMDS_Bar  # type: ignore
except Exception:
    pass

_ABP = None
try:
    # market_data_store.async_client (preferred)
    from market_data_store.async_client import AsyncBatchProcessor as _ABP  # type: ignore
except Exception:
    pass

# --- Metrics (optional Prometheus) --------------------------------------------
try:
    from prometheus_client import Counter, Histogram, Gauge

    _METRIC_ENABLED = True
    DB_BATCHES_IN = Counter("mdp_sink_db_batches_in_total", "Batches accepted by DatabaseSink")
    DB_BATCHES_WRITTEN = Counter("mdp_sink_db_batches_written_total", "Batches successfully written")
    DB_BATCHES_FAILED = Counter("mdp_sink_db_batches_failed_total", "Batches failed")
    DB_ITEMS_WRITTEN = Counter("mdp_sink_db_items_written_total", "Items persisted")
    DB_RETRIES = Counter("mdp_sink_db_retries_total", "Retry attempts")
    DB_QUEUE_DEPTH = Gauge("mdp_sink_db_queue_depth", "Pending batches in sink queue")
    DB_COMMIT_LATENCY = Histogram("mdp_sink_db_commit_seconds", "DB commit latency (seconds)")
except Exception:  # Prometheus not installed
    _METRIC_ENABLED = False


@dataclass
class DatabaseSinkSettings:
    vendor: str = "market_data_pipeline"
    timeframe: str = "1s"                # persisted timeframe label
    workers: int = 2
    queue_max: int = 200
    backpressure_policy: str = "block"   # "block" | "drop_oldest" | "drop_newest"
    retry_max_attempts: int = 5
    retry_backoff_ms: int = 50           # starting backoff, doubles on each retry


class DatabaseSink(Sink):
    """
    Production-grade sink that writes Bars into market_data_store using either:
      - AsyncBatchProcessor (preferred), or
      - AMDS (compat).

    Features:
      - Worker pool + bounded queue with configurable backpressure policy
      - True OHLCV mapping (no "close for all" hacks)
      - Idempotent upserts (delegated to store)
      - Retries with exp backoff on transient failures
      - Prometheus metrics (optional)
    """

    def __init__(
        self,
        *,
        tenant_id: str,
        settings: Optional[DatabaseSinkSettings] = None,
        ctx: Optional[PipelineContext] = None,
        # One of the following must be provided or resolvable:
        processor: Any = None,               # AsyncBatchProcessor or AMDS instance
        database_url: Optional[str] = None,  # used for AMDS if processor is None
    ) -> None:
        if not tenant_id:
            raise ValueError("tenant_id is required")
        self.tenant_id = tenant_id
        self.settings = settings or DatabaseSinkSettings()
        self.ctx = ctx
        self._processor = processor
        self._database_url = database_url

        self._queue: Optional[asyncio.Queue[list[Bar]]] = None
        self._workers: list[asyncio.Task] = []
        self._closed = False
        
        # Robust flush mechanism
        self._inflight = 0
        self._idle = asyncio.Event()
        self._idle.set()  # idle at start

        # local counters (returned via get_metrics)
        self._batches_in = 0
        self._batches_written = 0
        self._batches_failed = 0
        self._items_written = 0
        self._retries = 0

    # --- Sink interface --------------------------------------------------------

    @property
    def capabilities(self) -> SinkCapabilities:
        return SinkCapabilities.BATCH_WRITES

    async def start(self) -> None:
        if self._queue is not None:
            return
        self._queue = asyncio.Queue(maxsize=max(1, self.settings.queue_max))
        self._ensure_processor()
        # spin workers
        for i in range(max(1, self.settings.workers)):
            self._workers.append(asyncio.create_task(self._worker(f"db-sink-{i}")))
        log.info("DatabaseSink started (workers=%d, queue_max=%d, backpressure=%s)",
                 self.settings.workers, self.settings.queue_max, self.settings.backpressure_policy)

    async def write(self, batch: list[Bar]) -> None:
        if self._closed:
            raise RuntimeError("DatabaseSink is closed")
        if not batch:
            return
        if self._queue is None:
            await self.start()

        self._batches_in += 1
        if _METRIC_ENABLED:
            DB_BATCHES_IN.inc()

        q = self._queue  # type: ignore
        policy = self.settings.backpressure_policy
        while True:
            try:
                q.put_nowait(batch)
                # Clear idle signal since we have work to do
                self._idle.clear()
                break
            except asyncio.QueueFull:
                if policy == "block":
                    await q.put(batch)
                    break
                elif policy == "drop_oldest":
                    try:
                        q.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                    # loop back to try put_nowait again
                elif policy == "drop_newest":
                    # drop incoming batch
                    return
                else:
                    # default to block
                    await q.put(batch)
                    break
            finally:
                if _METRIC_ENABLED:
                    DB_QUEUE_DEPTH.set(q.qsize())

    async def flush(self) -> None:
        q = self._queue
        if not q:
            return
        # Wait for idle signal instead of polling
        self._maybe_set_idle()
        await self._idle.wait()

    async def close(self, drain: bool = True) -> None:
        if self._closed:
            return
        self._closed = True

        if self._workers:
            if drain:
                # graceful shutdown
                if self._queue:
                    for _ in range(len(self._workers)):
                        await self._queue.put(None)  # type: ignore[arg-type]
                    self._maybe_set_idle()
                    try:
                        await asyncio.wait_for(self._idle.wait(), timeout=2.0)
                    except asyncio.TimeoutError:
                        log.warning("Timed out waiting for sink to drain; closing anyway")
                await asyncio.gather(*self._workers, return_exceptions=True)
            else:
                # immediate shutdown
                for worker in self._workers:
                    worker.cancel()
                await asyncio.gather(*self._workers, return_exceptions=True)

        try:
            await self._close_processor()
        except Exception as e:
            log.warning("Error closing processor: %s", e)

    def get_metrics(self) -> dict[str, int]:
        return {
            "batches_in": self._batches_in,
            "batches_written": self._batches_written,
            "batches_failed": self._batches_failed,
            "items_written": self._items_written,
            "retries": self._retries,
        }

    # --- Workers & commit path -------------------------------------------------

    def _maybe_set_idle(self) -> None:
        """Update idle signal when queue is empty and no workers are processing."""
        q = self._queue
        if q and q.empty() and self._inflight == 0:
            self._idle.set()

    async def _worker(self, worker_id: str) -> None:
        q = self._queue
        assert q is not None
        while True:
            try:
                item = await q.get()
                if item is None:
                    return
                # Track in-flight work
                self._inflight += 1
                self._idle.clear()
                try:
                    await self._process_with_retry(item, worker_id)
                finally:
                    self._inflight -= 1
                    self._maybe_set_idle()
            except asyncio.CancelledError:
                return
            except Exception as e:
                self._batches_failed += 1
                if _METRIC_ENABLED:
                    DB_BATCHES_FAILED.inc()
                log.error("DatabaseSink worker %s error: %s", worker_id, e)

    async def _process_with_retry(self, batch: list[Bar], worker_id: str) -> None:
        attempts = 0
        delay = max(1, self.settings.retry_backoff_ms) / 1000.0
        while True:
            try:
                if _METRIC_ENABLED:
                    with DB_COMMIT_LATENCY.time():
                        rows = await self._commit(batch)
                else:
                    rows = await self._commit(batch)
                self._batches_written += 1
                self._items_written += rows
                if _METRIC_ENABLED:
                    DB_BATCHES_WRITTEN.inc()
                    DB_ITEMS_WRITTEN.inc(rows)
                return
            except Exception as e:
                attempts += 1
                self._batches_failed += 1
                if _METRIC_ENABLED:
                    DB_BATCHES_FAILED.inc()
                if self._is_transient(e) and attempts < self.settings.retry_max_attempts:
                    self._retries += 1
                    if _METRIC_ENABLED:
                        DB_RETRIES.inc()
                    log.warning("Transient DB error (attempt %d/%d): %s; backing off %.3fs",
                                attempts, self.settings.retry_max_attempts, e, delay)
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                log.error("DB commit failed after %d attempts: %s", attempts, e)
                raise

    async def _commit(self, batch: list[Bar]) -> int:
        proc = self._processor
        if proc is None:
            raise RuntimeError("Database processor not initialized")

        records = list(self._to_records(batch))
        if not records:
            return 0

        # AsyncBatchProcessor path
        if _ABP and isinstance(proc, _ABP):
            # expects list[dict]
            await proc.upsert_bars(records)  # type: ignore
            return len(records)

        # AMDS path
        if _AMDS and isinstance(proc, _AMDS):
            # expects list[AMDS_Bar]
            amds_records = [self._to_amds_bar(d) for d in records]
            await proc.upsert_bars(amds_records)  # type: ignore
            return len(amds_records)

        # Generic duck-typing fallback
        if hasattr(proc, "upsert_bars"):
            res = proc.upsert_bars(records)
            if inspect.isawaitable(res):
                await res
            return len(records)

        raise RuntimeError("Processor does not support upsert_bars()")

    # --- Mapping ---------------------------------------------------------------

    def _to_records(self, batch: Sequence[Bar]) -> Iterable[dict[str, Any]]:
        """Map pipeline Bar -> store row dict; keep true OHLCV."""
        for b in batch:
            # Defensive: ensure types are JSON/DB friendly
            def D(x: Optional[Decimal]) -> Optional[float]:
                return float(x) if x is not None else None

            row = {
                "tenant_id": self.tenant_id,
                "vendor": self.settings.vendor,
                "symbol": b.symbol,
                "timeframe": self.settings.timeframe,
                "ts": b.timestamp if isinstance(b.timestamp, datetime) else b.timestamp,
                "open_price": D(b.open),
                "high_price": D(b.high),
                "low_price": D(b.low),
                "close_price": D(b.close),
                "volume": int(b.volume) if b.volume is not None else 0,
                # Optional fields if your store schema supports them:
                "trade_count": int(b.trade_count) if b.trade_count is not None else None,
                "vwap": D(b.vwap),
                # free-form metadata passthrough (store side may ignore/JSONB it)
                "metadata": b.metadata or {},
            }
            yield row

    def _to_amds_bar(self, row: dict[str, Any]):
        if not _AMDS_Bar:
            raise RuntimeError("mds_client.Bar not available")
        return _AMDS_Bar(
            tenant_id=row["tenant_id"],
            vendor=row["vendor"],
            symbol=row["symbol"],
            timeframe=row["timeframe"],
            ts=row["ts"],
            open_price=row["open_price"],
            high_price=row["high_price"],
            low_price=row["low_price"],
            close_price=row["close_price"],
            volume=row["volume"],
            # Conditionally set optional fields if Bar dataclass supports them
            **({k: v for k, v in {
                "trade_count": row.get("trade_count"),
                "vwap": row.get("vwap"),
                "metadata": row.get("metadata"),
            }.items() if v is not None})
        )

    # --- Processor lifecycle ---------------------------------------------------

    def _ensure_processor(self) -> None:
        """Create a processor if one wasn't provided."""
        if self._processor is not None:
            return

        # Preferred: AsyncBatchProcessor (market_data_store)
        if _ABP:
            if hasattr(_ABP, "from_env_async"):
                # Construct synchronously via run_until_complete to keep start() sync pattern
                loop = asyncio.get_event_loop()
                self._processor = loop.run_until_complete(_ABP.from_env_async())  # type: ignore
            else:
                self._processor = _ABP.from_env()  # type: ignore
            log.info("DatabaseSink using AsyncBatchProcessor")
            return

        # Compat: AMDS (mds_client)
        if _AMDS:
            if not self._database_url:
                raise RuntimeError("DATABASE_URL is required for AMDS processor")
            self._processor = _AMDS({"dsn": self._database_url, "tenant_id": self.tenant_id})
            log.info("DatabaseSink using AMDS client")
            return

        raise RuntimeError("No database client available (install market_data_store or mds_client)")

    async def _close_processor(self) -> None:
        proc = self._processor
        if proc is None:
            return
        # prefer async close
        close = getattr(proc, "close", None)
        aclose = getattr(proc, "aclose", None)
        if callable(aclose):
            await aclose()
        elif callable(close):
            res = close()
            if asyncio.iscoroutine(res):
                await res
        self._processor = None

    # --- Retry classification --------------------------------------------------

    @staticmethod
    def _is_transient(err: Exception) -> bool:
        # Heuristic: treat common transient database/network issues as retryable
        msg = f"{type(err).__name__}: {err}".lower()
        retryable_substrings = (
            "timeout", "temporarily", "deadlock", "could not serialize",
            "connection reset", "connection refused", "too many connections",
            "broken pipe", "server closed the connection", "network is unreachable",
        )
        return any(s in msg for s in retryable_substrings)


# --- helpers ------------------------------------------------------------------
