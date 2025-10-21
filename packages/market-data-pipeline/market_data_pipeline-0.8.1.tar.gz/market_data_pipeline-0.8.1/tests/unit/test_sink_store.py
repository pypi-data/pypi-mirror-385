# tests/unit/test_sink_store.py
import asyncio
import pytest
from decimal import Decimal
from datetime import datetime, timezone
from market_data_pipeline.sink.store import StoreSink
from market_data_pipeline.types import Bar


class FakeBatchProcessor:
    def __init__(self):
        self.writes = []

    def upsert_bars(self, rows):
        # Simulate minimal AMDS behavior (sync version - this is the real issue)
        self.writes.extend(rows)


def mkbar(sym: str, i: int) -> Bar:
    return Bar(
        symbol=sym,
        timestamp=datetime.now(timezone.utc),
        open=Decimal(i),
        high=Decimal(i),
        low=Decimal(i),
        close=Decimal(i),
        volume=Decimal(1),
        vwap=None,
        trade_count=1,
        source="test",
        metadata={},
    )


@pytest.mark.asyncio
async def test_store_sink_writes_and_drains():
    sink = StoreSink(
        FakeBatchProcessor(), workers=1, queue_max=2, backpressure_policy="block"
    )
    await sink.start()
    await sink.write([mkbar("NVDA", 1), mkbar("NVDA", 2)])
    await sink.write([mkbar("SPY", 3)])
    await sink.flush()
    await sink.close(drain=True)
    assert len(sink.batch_processor.writes) == 3


@pytest.mark.asyncio
async def test_store_sink_backpressure_drop_oldest():
    sink = StoreSink(
        FakeBatchProcessor(), workers=1, queue_max=1, backpressure_policy="drop_oldest"
    )
    await sink.start()
    await sink.write([mkbar("NVDA", 1)])
    await sink.write([mkbar("NVDA", 2)])  # should drop the oldest batch in queue
    await sink.close(drain=True)
    # Depending on timing, we should at least have the last batch
    assert any(
        b["symbol"] == "NVDA" and b["open"] == 2.0 for b in sink.batch_processor.writes
    )


@pytest.mark.asyncio
async def test_store_sink_handles_sync_upsert_bars():
    """Test that StoreSink properly handles sync upsert_bars method."""
    sink = StoreSink(FakeBatchProcessor(), workers=1, queue_max=2, backpressure_policy="block")
    await sink.start()
    await sink.write([mkbar("TEST", 1), mkbar("TEST", 2)])
    await sink.flush()
    await sink.close(drain=True)
    # Verify that the sync method was called and data was written
    assert len(sink.batch_processor.writes) == 2
    assert all(b["symbol"] == "TEST" for b in sink.batch_processor.writes)
