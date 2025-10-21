"""
Phase 5.0.4 — IBKR → DAG → WriteCoordinator → BarsSink

Full end-to-end backpressure: IBKR → DAG → Coordinator → Store

Requirements:
- market-data-core==1.0.0
- market-data-ibkr==1.0.0
- market-data-pipeline>=0.9.0 (with Phase 5.0.4)
- market-data-store>=0.9.0 (with coordinator + sinks)
- IBKR Gateway/TWS running
- Postgres reachable by AMDS

Run:
  python examples/run_dag_ibkr_to_coordinator.py
"""

import asyncio
from datetime import timedelta

from loguru import logger

# Check optional dependencies
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
    logger.warning("market-data-store not installed - cannot run this example")

# DAG runtime
from market_data_pipeline.orchestration.runtime_orchestrator import RuntimeOrchestrator


def map_core_bar_to_store(b: CoreBar) -> StoreBar:  # type: ignore[valid-type]
    """Minimal adapter; tweak if schemas diverge."""
    payload = b.model_dump()
    return StoreBar(**payload)


async def build_pipeline(
    symbols: list[str],
    ibkr_resolution: str = "5s",
    duration_sec: float = 30.0,
) -> None:
    """
    1) IBKR bars → Channel
    2) Submit to WriteCoordinator (BarsSink)
    """
    if not HAS_STORE:
        logger.error("Please install market-data-store to run this example")
        return

    logger.info("Starting IBKR→DAG→Coordinator (bars)…")

    # 1) Source (IBKR → Channel[Bar])
    rt = RuntimeOrchestrator()
    bars_ch = await rt.bars_to_channel(
        symbols=symbols,
        resolution=ibkr_resolution,
        max_buffer=8192
    )

    # 2) Coordinator with BarsSink
    settings = CoordinatorRuntimeSettings(
        coordinator_capacity=20_000,
        coordinator_workers=4,
        coordinator_batch_size=500,
        coordinator_flush_interval=0.25,
        retry_max_attempts=5,
        retry_initial_backoff_ms=50,
        retry_max_backoff_ms=2_000,
    )
    retry = RetryPolicy(
        max_attempts=settings.retry_max_attempts,
        initial_backoff_ms=settings.retry_initial_backoff_ms,
        max_backoff_ms=settings.retry_max_backoff_ms,
        backoff_multiplier=2.0,
        jitter=True,
    )

    count = 0

    async with AMDS() as amds, BarsSink(amds) as sink:
        async with WriteCoordinator(
            sink=sink,
            settings=settings,
            retry_policy=retry,
        ) as coord:
            logger.info("Coordinator started, pumping bars…")

            try:
                async def pump_bars():
                    nonlocal count
                    try:
                        async for core_bar in bars_ch.iter():
                            store_bar = map_core_bar_to_store(core_bar)
                            await coord.submit(store_bar)  # backpressure if queue saturated
                            count += 1
                            
                            if count % 100 == 0:
                                logger.info(f"Submitted {count} bars to coordinator")
                            
                            # Demo: stop after 200 bars
                            if count >= 200:
                                break
                    except Exception as e:
                        logger.error(f"Error in pump: {e}")
                        raise

                # Run with timeout
                await asyncio.wait_for(pump_bars(), timeout=duration_sec)

            except asyncio.TimeoutError:
                logger.info(f"Demo timeout reached ({duration_sec}s)")
            except Exception as e:
                logger.error(f"Pipeline error: {e}", exc_info=True)

            # Ensure drain on normal completion
            logger.info("Draining coordinator…")
            await coord.drain()

    logger.info(f"Pipeline completed (normal shutdown). Total bars: {count}")


async def main():
    try:
        await build_pipeline(
            symbols=["AAPL", "MSFT"],
            ibkr_resolution="5s",
            duration_sec=30.0
        )
    except KeyboardInterrupt:
        logger.warning("CTRL+C received, exiting…")


if __name__ == "__main__":
    asyncio.run(main())

