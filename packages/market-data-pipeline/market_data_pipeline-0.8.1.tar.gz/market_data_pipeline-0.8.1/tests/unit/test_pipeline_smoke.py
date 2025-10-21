# tests/unit/test_pipeline_smoke.py
import asyncio
import pytest
from market_data_pipeline.pipeline import StreamingPipeline
from market_data_pipeline.source.synthetic import SyntheticSource
from market_data_pipeline.operator.bars import SecondBarAggregator
from market_data_pipeline.batcher.hybrid import HybridBatcher
from market_data_pipeline.context import PipelineContext


class MemorySink:
    def __init__(self):
        self.batches = []

    async def write(self, batch):
        self.batches.append(batch)

    async def close(self, drain: bool = True):
        pass


@pytest.mark.asyncio
async def test_pipeline_end_to_end_in_memory():
    ctx = PipelineContext(tenant_id="test", pipeline_id="smoke_test")
    src = SyntheticSource(symbols=["NVDA"], ticks_per_sec=30, pacing_budget=(30, 30))
    op = SecondBarAggregator(window_sec=1)
    batcher = HybridBatcher(max_rows=20, max_bytes=1_000_000, flush_ms=100)
    sink = MemorySink()
    pipe = StreamingPipeline(
        source=src, operator=op, batcher=batcher, sink=sink, ctx=ctx
    )

    await asyncio.wait_for(pipe.run(duration_sec=1.5), timeout=5.0)
    # At least one batch should have been written
    assert len(sink.batches) >= 1
    assert sum(len(b) for b in sink.batches) >= 1
