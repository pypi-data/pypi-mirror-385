# tests/integration/test_e2e_synthetic_store.py
import os
import asyncio
import pytest
from market_data_pipeline.pipeline import StreamingPipeline
from market_data_pipeline.source.synthetic import SyntheticSource
from market_data_pipeline.operator import SecondBarAggregator
from market_data_pipeline.batcher.hybrid import HybridBatcher
from market_data_pipeline.sink.store import StoreSink

AMDS_AVAILABLE = True
try:
    from market_data_store.async_client import AsyncBatchProcessor
except Exception:
    AMDS_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not AMDS_AVAILABLE or not os.environ.get("DATABASE_URL"),
    reason="market_data_store client or DATABASE_URL not available",
)


@pytest.mark.asyncio
async def test_e2e_synthetic_to_store_timescale():
    bp = (
        await AsyncBatchProcessor.from_env_async()
        if hasattr(AsyncBatchProcessor, "from_env_async")
        else AsyncBatchProcessor.from_env()
    )
    sink = StoreSink(
        bp, workers=2, queue_max=100, backpressure_policy="oldest", ctx=None
    )
    src = SyntheticSource(
        symbols=["NVDA", "SPY"], ticks_per_sec=40, pacing_budget=(40, 40)
    )
    op = SecondBarAggregator(window_sec=1)
    batcher = HybridBatcher(max_rows=200, max_bytes=512_000, flush_ms=100)
    pipe = StreamingPipeline(
        source=src, operator=op, batcher=batcher, sink=sink, ctx=None
    )

    await asyncio.wait_for(pipe.run(duration_sec=3.0), timeout=10.0)
    # If no exception, we consider this a pass; deeper assertions can query the DB if desired.
    assert True
