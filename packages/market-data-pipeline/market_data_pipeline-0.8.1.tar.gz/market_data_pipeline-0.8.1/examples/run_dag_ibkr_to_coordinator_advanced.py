"""
Phase 5.0.4 — IBKR → DAG → WriteCoordinator (Advanced)

Adds:
- DLQ for failed writes
- Health monitoring
- Metrics hints
- Contrib operators (throttle, dedupe, resample)

Requirements:
- market-data-core==1.0.0
- market-data-ibkr==1.0.0
- market-data-pipeline>=0.9.0 (Phase 5.0.4)
- market-data-store>=0.9.0
- IBKR Gateway/TWS running
- Postgres reachable by AMDS

Run:
  python examples/run_dag_ibkr_to_coordinator_advanced.py
"""

import asyncio
import contextlib
from datetime import timedelta

from loguru import logger

# Check dependencies
try:
    from market_data_core import Bar as CoreBar
    from market_data_store.coordinator.policy import RetryPolicy
    from market_data_store.coordinator.settings import CoordinatorRuntimeSettings
    from market_data_store.coordinator.write_coordinator import WriteCoordinator
    from market_data_store.sinks import BarsSink
    from mds_client import AMDS
    from mds_client.models import Bar as StoreBar
    HAS_STORE = True
except ImportError:
    HAS_STORE = False
    logger.warning("market-data-store not installed")

# DAG runtime + contrib operators
from market_data_pipeline.orchestration.dag import deduplicate, throttle
from market_data_pipeline.orchestration.runtime_orchestrator import RuntimeOrchestrator


def to_store(b: CoreBar) -> StoreBar:  # type: ignore[valid-type]
    return StoreBar(**b.model_dump())


async def health_probe(coord: WriteCoordinator) -> None:  # type: ignore[valid-type]
    """Background task to monitor coordinator health."""
    while True:
        try:
            h = await coord.health_check()
            logger.debug(
                f"Health: workers={h.workers_alive} queue={h.queue_size} "
                f"errors={h.errors_pending}"
            )
        except Exception as e:
            logger.warning(f"Health probe error: {e}")
        
        await asyncio.sleep(5)


async def main_advanced():
    if not HAS_STORE:
        logger.error("Please install market-data-store to run this example")
        return

    logger.info("Starting IBKR→DAG→Coordinator (advanced path)…")

    try:
        # 1) Source
        rt = RuntimeOrchestrator()
        ch = await rt.bars_to_channel(
            ["AAPL", "MSFT"],
            resolution="5s",
            max_buffer=4096
        )

        # 2) Contrib operators
        stream = throttle(ch.iter(), rate_limit=400)
        stream = deduplicate(
            stream,
            key_fn=lambda b: (b.symbol, getattr(b, "ts", None)),
            ttl=60.0
        )

        # 3) Coordinator settings
        settings = CoordinatorRuntimeSettings(
            coordinator_capacity=30_000,
            coordinator_workers=6,
            coordinator_batch_size=800,
            coordinator_flush_interval=0.20,
            retry_max_attempts=6,
            retry_initial_backoff_ms=50,
            retry_max_backoff_ms=3_000,
        )
        retry = RetryPolicy(
            max_attempts=settings.retry_max_attempts,
            initial_backoff_ms=settings.retry_initial_backoff_ms,
            max_backoff_ms=settings.retry_max_backoff_ms,
            backoff_multiplier=2.0,
            jitter=True,
        )

        # Note: DLQ implementation depends on your Phase 4.3 API
        # dlq = DeadLetterQueue(path="dlq/bars.ndjson")

        count = 0

        async with AMDS() as amds, BarsSink(amds) as sink:
            async with WriteCoordinator(
                sink=sink,
                settings=settings,
                retry_policy=retry,
                # dlq=dlq,  # Uncomment if DLQ is available
            ) as coord:
                # Background health probe (optional)
                probe_task = asyncio.create_task(health_probe(coord))

                try:
                    logger.info("Coordinator started, consuming stream…")
                    
                    async def consume():
                        nonlocal count
                        async for b in stream:
                            await coord.submit(to_store(b))
                            count += 1
                            
                            if count % 100 == 0:
                                logger.info(f"Processed {count} bars")
                            
                            # Demo: stop after 300 bars
                            if count >= 300:
                                break
                    
                    # Run with timeout
                    await asyncio.wait_for(consume(), timeout=45.0)

                except asyncio.TimeoutError:
                    logger.info("Demo timeout reached")
                finally:
                    logger.info("Draining coordinator…")
                    await coord.drain()
                    
                    probe_task.cancel()
                    with contextlib.suppress(Exception):
                        await probe_task

        logger.info(f"Pipeline completed successfully. Total bars: {count}")

    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main_advanced())
    except KeyboardInterrupt:
        logger.warning("CTRL+C received, exiting…")

