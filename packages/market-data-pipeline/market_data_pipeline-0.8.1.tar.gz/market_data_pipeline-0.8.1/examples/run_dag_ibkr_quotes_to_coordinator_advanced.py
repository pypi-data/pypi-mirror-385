"""
Phase 5.0.4 — IBKR → DAG → WriteCoordinator → QuotesSink (Advanced)

Advanced quote ingestion with:
- DLQ for failed writes
- Health monitoring
- Higher throughput tuning
- Full error handling

Requirements:
- market-data-core==1.0.0
- market-data-ibkr==1.0.0
- market-data-pipeline>=0.9.0 (Phase 5.0.4)
- market-data-store>=0.9.0 (with QuotesSink + DLQ)
- IBKR Gateway/TWS running
- Postgres reachable by AMDS

Run:
  python examples/run_dag_ibkr_quotes_to_coordinator_advanced.py
"""

import asyncio
import contextlib
from datetime import timedelta

from loguru import logger

# Check dependencies
try:
    from market_data_core import Quote as CoreQuote
    from market_data_store.coordinator.policy import RetryPolicy
    from market_data_store.coordinator.settings import CoordinatorRuntimeSettings
    from market_data_store.coordinator.write_coordinator import WriteCoordinator
    from market_data_store.sinks import QuotesSink
    from mds_client import AMDS
    from mds_client.models import Quote as StoreQuote
    HAS_STORE = True
    
    # Optional DLQ
    try:
        from market_data_store.coordinator.dlq import DeadLetterQueue
        HAS_DLQ = True
    except ImportError:
        HAS_DLQ = False
        logger.warning("DLQ not available")
except ImportError:
    HAS_STORE = False
    HAS_DLQ = False
    logger.warning("market-data-store not installed")

# DAG runtime + operators
from market_data_pipeline.orchestration.dag import deduplicate, throttle
from market_data_pipeline.orchestration.runtime_orchestrator import RuntimeOrchestrator


def to_store(q: CoreQuote) -> StoreQuote:  # type: ignore[valid-type]
    return StoreQuote(**q.model_dump())


async def probe_health(coord: WriteCoordinator) -> None:  # type: ignore[valid-type]
    """Background health monitoring task."""
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


async def main():
    if not HAS_STORE:
        logger.error("Please install market-data-store to run this example")
        return

    logger.info("Starting IBKR→DAG→Coordinator (advanced quotes)…")

    try:
        # 1) Source
        orchestrator = RuntimeOrchestrator()
        ch = await orchestrator.quotes_to_channel(
            symbols=["AAPL", "MSFT", "NVDA"],
            max_buffer=4096
        )

        # 2) Operators (higher throughput settings)
        stream = throttle(ch.iter(), rate_limit=800)
        stream = deduplicate(
            stream,
            key_fn=lambda q: (q.symbol, q.ts),
            ttl=5.0
        )

        # 3) Coordinator settings (optimized for quotes)
        settings = CoordinatorRuntimeSettings(
            coordinator_capacity=25_000,
            coordinator_workers=6,
            coordinator_batch_size=1000,
            coordinator_flush_interval=0.15,
            retry_max_attempts=5,
            retry_initial_backoff_ms=50,
            retry_max_backoff_ms=2000,
        )
        retry = RetryPolicy(
            max_attempts=settings.retry_max_attempts,
            initial_backoff_ms=settings.retry_initial_backoff_ms,
            max_backoff_ms=settings.retry_max_backoff_ms,
            backoff_multiplier=2.0,
            jitter=True,
        )

        # Optional DLQ
        dlq = None
        if HAS_DLQ:
            from market_data_store.coordinator.dlq import DeadLetterQueue
            dlq = DeadLetterQueue(path="dlq/quotes.ndjson")

        count = 0

        # 4) Coordinator with QuotesSink
        async with AMDS() as amds, QuotesSink(amds) as sink:
            kwargs = {
                "sink": sink,
                "settings": settings,
                "retry_policy": retry,
            }
            if dlq:
                kwargs["dlq"] = dlq

            async with WriteCoordinator(**kwargs) as coord:
                # Background health monitoring
                monitor = asyncio.create_task(probe_health(coord))

                try:
                    logger.info("Coordinator started, consuming quotes…")
                    
                    async def consume():
                        nonlocal count
                        async for q in stream:
                            await coord.submit(to_store(q))
                            count += 1
                            
                            if count % 500 == 0:
                                logger.info(f"Processed {count} quotes")
                            
                            # Demo: stop after 2000 quotes
                            if count >= 2000:
                                break

                    # Run with timeout
                    await asyncio.wait_for(consume(), timeout=60.0)

                except asyncio.TimeoutError:
                    logger.info("Demo timeout reached")
                finally:
                    logger.info("Draining coordinator…")
                    await coord.drain()
                    
                    monitor.cancel()
                    with contextlib.suppress(Exception):
                        await monitor

        logger.info(f"Quote ingestion completed. Total quotes: {count}")

    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("CTRL+C received, exiting…")

