"""
Phase 5.0.4 — IBKR → DAG → WriteCoordinator → QuotesSink

End-to-end live quote ingestion with full backpressure and retry handling.

Requirements:
- market-data-core==1.0.0
- market-data-ibkr==1.0.0
- market-data-pipeline>=0.9.0 (Phase 5.0.4)
- market-data-store>=0.9.0 (with QuotesSink)
- IBKR Gateway/TWS running
- Postgres reachable by AMDS

Run:
  python examples/run_dag_ibkr_quotes_to_coordinator.py
"""

import asyncio
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
except ImportError:
    HAS_STORE = False
    logger.warning("market-data-store not installed")

# DAG runtime + operators
from market_data_pipeline.orchestration.dag import deduplicate, throttle
from market_data_pipeline.orchestration.runtime_orchestrator import RuntimeOrchestrator


def map_core_quote_to_store(q: CoreQuote) -> StoreQuote:  # type: ignore[valid-type]
    """Adapt Core→Store DTOs (if schema matches, pass through)."""
    payload = q.model_dump()
    # Normalize fields if needed
    # e.g., payload["timestamp"] = q.ts.isoformat()
    return StoreQuote(**payload)


async def run_quote_pipeline(symbols: list[str], duration_sec: float = 30.0):
    if not HAS_STORE:
        logger.error("Please install market-data-store to run this example")
        return

    logger.info(f"Starting IBKR→DAG→Coordinator pipeline (quotes) for {symbols}")

    # 1) Source (IBKR → Channel[Quote])
    orchestrator = RuntimeOrchestrator()
    quotes_ch = await orchestrator.quotes_to_channel(symbols=symbols, max_buffer=8192)

    # 2) Operators (dedupe + throttle)
    stream = throttle(quotes_ch.iter(), rate_limit=1000)
    stream = deduplicate(stream, key_fn=lambda q: (q.symbol, q.ts), ttl=5.0)

    # 3) Coordinator setup
    settings = CoordinatorRuntimeSettings(
        coordinator_capacity=20_000,
        coordinator_workers=4,
        coordinator_batch_size=800,
        coordinator_flush_interval=0.2,
        retry_max_attempts=4,
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

    count = 0

    # 4) Coordinator with QuotesSink
    async with AMDS() as amds, QuotesSink(amds) as sink:
        async with WriteCoordinator(
            sink=sink,
            settings=settings,
            retry_policy=retry,
        ) as coord:
            logger.info("Coordinator started, consuming quotes…")

            try:
                async def consume():
                    nonlocal count
                    async for q in stream:
                        store_q = map_core_quote_to_store(q)
                        await coord.submit(store_q)
                        count += 1
                        
                        if count % 500 == 0:
                            logger.info(f"Processed {count} quotes")
                        
                        # Demo: stop after 1000 quotes
                        if count >= 1000:
                            break

                # Run with timeout
                await asyncio.wait_for(consume(), timeout=duration_sec)

            except asyncio.TimeoutError:
                logger.info(f"Demo timeout reached ({duration_sec}s)")
            except Exception as e:
                logger.error(f"Pipeline error: {e}", exc_info=True)
            finally:
                logger.info("Draining coordinator…")
                await coord.drain()

    logger.info(f"Quote ingestion completed cleanly. Total quotes: {count}")


async def main():
    try:
        await run_quote_pipeline(["AAPL", "MSFT", "NVDA"], duration_sec=30.0)
    except KeyboardInterrupt:
        logger.warning("CTRL+C — shutting down gracefully…")
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")


if __name__ == "__main__":
    asyncio.run(main())

