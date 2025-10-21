"""
Phase 5.0.4 — IBKR → DAG → Store (Simple Path)

Demonstrates basic integration of IBKR provider → DAG operators → BarsSink

Requirements:
- market-data-core==1.0.0
- market-data-ibkr==1.0.0
- market-data-pipeline>=0.9.0 (with Phase 5.0.4)
- market-data-store>=0.9.0
- IBKR Gateway/TWS running
- Postgres reachable by AMDS

Run:
  python examples/run_dag_ibkr_to_store_simple.py
"""

import asyncio
from datetime import timedelta

from loguru import logger

# Check if optional dependencies are available
try:
    from market_data_core import Bar as CoreBar
    from market_data_store.sinks import BarsSink
    from mds_client import AMDS
    from mds_client.models import Bar as StoreBar
    HAS_STORE = True
except ImportError:
    HAS_STORE = False
    logger.warning("market-data-store or mds_client not installed - cannot run this example")

# DAG runtime
from market_data_pipeline.orchestration.runtime_orchestrator import RuntimeOrchestrator


def map_core_bar_to_store(b: CoreBar) -> StoreBar:  # type: ignore[valid-type]
    """Map Core Bar DTO to Store Bar DTO."""
    return StoreBar(**b.model_dump())


async def main_simple():
    if not HAS_STORE:
        logger.error("Please install market-data-store and mds_client to run this example")
        return

    logger.info("Starting IBKR→DAG→Store pipeline (simple bars path)…")

    try:
        # 1) Source (IBKR → Channel of Bars)
        rt = RuntimeOrchestrator()
        bars_ch = await rt.bars_to_channel(
            symbols=["AAPL", "MSFT"],
            resolution="5s",
            max_buffer=4096
        )

        logger.info("Channel created, starting consumption…")

        # 2) Write to store (direct sink)
        async with AMDS() as amds, BarsSink(amds) as sink:
            batch = []
            count = 0
            
            try:
                # Consume for 30 seconds (demo duration)
                async def consume_bars():
                    nonlocal count
                    try:
                        async for bar in bars_ch.iter():
                            count += 1
                            batch.append(map_core_bar_to_store(bar))
                            
                            if len(batch) >= 100:
                                await sink.write(batch)
                                logger.info(f"Wrote batch of {len(batch)} bars (total: {count})")
                                batch.clear()
                            
                            # Demo: stop after 50 bars
                            if count >= 50:
                                break
                    except Exception as e:
                        logger.error(f"Error consuming bars: {e}")
                        raise

                # Run with timeout
                await asyncio.wait_for(consume_bars(), timeout=30.0)
                
            except asyncio.TimeoutError:
                logger.info("Demo timeout reached (30s)")
            
            # Flush remaining
            if batch:
                await sink.write(batch)
                logger.info(f"Flushed final batch of {len(batch)} bars")

        logger.info(f"Pipeline completed successfully. Total bars: {count}")

    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Please install: pip install market-data-ibkr market-data-core market-data-store")
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main_simple())
    except KeyboardInterrupt:
        logger.warning("CTRL+C received, exiting…")

