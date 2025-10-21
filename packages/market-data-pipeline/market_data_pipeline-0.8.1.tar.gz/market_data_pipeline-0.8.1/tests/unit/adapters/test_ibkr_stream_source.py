"""Tests for IBKR stream source adapter."""
import asyncio

import pytest

# Test with mock provider
pytest.importorskip("market_data_core")
pytest.importorskip("market_data_ibkr")

from market_data_core import Quote
from market_data_ibkr import IBKRProvider

from market_data_pipeline.adapters.providers.ibkr_stream_source import IBKRStreamSource


class FakeIBKRProvider(IBKRProvider):  # type: ignore[misc]
    """Fake provider for testing."""
    
    def __init__(self):
        # Don't call super().__init__() to avoid TWS connection
        pass
    
    async def stream_quotes(self, instruments):
        """Emit a few quotes then stop."""
        for i in range(5):
            yield Quote(symbol="AAPL", last=100.0 + i, bid=99.0 + i, ask=101.0 + i)
            await asyncio.sleep(0)
    
    async def stream_bars(self, resolution, instruments):
        """Not used in quotes test."""
        while False:
            yield
    
    async def close(self):
        """No-op close."""
        pass


@pytest.mark.asyncio
async def test_ibkr_quotes_stream_basic():
    """Test basic quotes streaming."""
    src = IBKRStreamSource(
        symbols=["AAPL"],
        provider=FakeIBKRProvider(),
        mode="quotes"
    )
    await src.start()
    
    got = []
    async for q in src.stream():
        got.append(q)
    
    await src.stop()
    
    assert len(got) == 5
    assert got[0].symbol == "AAPL"
    assert got[0].last == 100.0
    assert got[4].last == 104.0


@pytest.mark.asyncio
async def test_ibkr_stream_can_be_cancelled():
    """Test that stream respects cancellation event."""
    
    class InfiniteProvider(IBKRProvider):  # type: ignore[misc]
        def __init__(self):
            pass
        
        async def stream_quotes(self, instruments):
            for i in range(1000):
                yield Quote(symbol="AAPL", last=100.0 + i, bid=99.0, ask=101.0)
                await asyncio.sleep(0.01)
        
        async def stream_bars(self, resolution, instruments):
            while False:
                yield
        
        async def close(self):
            pass
    
    src = IBKRStreamSource(
        symbols=["AAPL"],
        provider=InfiniteProvider(),
        mode="quotes"
    )
    await src.start()
    
    got = []
    
    async def consume():
        async for q in src.stream():
            got.append(q)
            if len(got) >= 5:
                await src.stop()  # trigger cancellation
                break
    
    await consume()
    
    # Should have stopped early
    assert len(got) == 5

