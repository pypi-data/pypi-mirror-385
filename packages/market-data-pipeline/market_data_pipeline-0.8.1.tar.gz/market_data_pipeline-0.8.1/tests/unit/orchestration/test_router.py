"""Unit tests for SourceRouter."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from market_data_pipeline.errors import SourceError
from market_data_pipeline.orchestration.router import RetryableError, SourceRouter
from market_data_pipeline.source.base import SourceStatus
from market_data_pipeline.types import Quote


class MockSource:
    """Mock source for testing."""
    
    def __init__(self, quotes: list[Quote], should_fail: bool = False):
        self.quotes = quotes
        self.should_fail = should_fail
        self.started = False
        self.closed = False
    
    async def stream(self):
        if self.should_fail:
            raise RetryableError("Mock failure")
        for quote in self.quotes:
            yield quote
    
    async def start(self):
        self.started = True
    
    async def close(self):
        self.closed = True
    
    async def status(self):
        return SourceStatus(connected=True, detail="Mock source")
    
    @property
    def symbols(self):
        return ["MOCK"]


def create_quote(symbol: str = "AAPL", price: float = 100.0) -> Quote:
    """Helper to create a test quote."""
    return Quote(
        symbol=symbol,
        timestamp=datetime.now(timezone.utc),
        price=Decimal(str(price)),
        size=Decimal("100"),
        source="mock",
    )


class TestSourceRouter:
    """Test SourceRouter functionality."""
    
    @pytest.mark.asyncio
    async def test_single_source(self):
        """Test router with single source."""
        quotes = [create_quote("AAPL", 100.0), create_quote("AAPL", 101.0)]
        source = MockSource(quotes)
        
        router = SourceRouter(sources=[source])
        
        collected = []
        async for quote in router.stream():
            collected.append(quote)
        
        assert len(collected) == 2
        assert collected[0].price == Decimal("100.0")
        assert collected[1].price == Decimal("101.0")
    
    @pytest.mark.asyncio
    async def test_fallback_to_second_source(self):
        """Test fallback when first source fails."""
        source1 = MockSource([], should_fail=True)
        quotes2 = [create_quote("AAPL", 100.0)]
        source2 = MockSource(quotes2)
        
        router = SourceRouter(sources=[source1, source2])
        
        collected = []
        async for quote in router.stream():
            collected.append(quote)
        
        # Should get quotes from second source
        assert len(collected) == 1
        assert collected[0].price == Decimal("100.0")
    
    @pytest.mark.asyncio
    async def test_all_sources_fail(self):
        """Test error when all sources fail."""
        source1 = MockSource([], should_fail=True)
        source2 = MockSource([], should_fail=True)
        
        router = SourceRouter(sources=[source1, source2])
        
        with pytest.raises(SourceError, match="All sources failed"):
            async for _ in router.stream():
                pass
    
    @pytest.mark.asyncio
    async def test_close_all_sources(self):
        """Test closing router closes all sources."""
        source1 = MockSource([])
        source2 = MockSource([])
        
        router = SourceRouter(sources=[source1, source2])
        
        await router.close()
        
        assert source1.closed
        assert source2.closed
    
    @pytest.mark.asyncio
    async def test_status(self):
        """Test getting router status."""
        quotes = [create_quote()]
        source = MockSource(quotes)
        
        router = SourceRouter(sources=[source])
        
        # Before streaming
        status = await router.status()
        assert not status.connected
        
        # Stream one quote to activate source
        async for _ in router.stream():
            break
        
        # After streaming
        status = await router.status()
        assert status.connected
    
    def test_add_source(self):
        """Test adding source to router."""
        source1 = MockSource([])
        router = SourceRouter(sources=[source1])
        
        assert len(router.sources) == 1
        
        source2 = MockSource([])
        router.add_source(source2)
        
        assert len(router.sources) == 2
    
    def test_remove_source(self):
        """Test removing source from router."""
        source1 = MockSource([])
        source2 = MockSource([])
        router = SourceRouter(sources=[source1, source2])
        
        assert len(router.sources) == 2
        
        router.remove_source(source1)
        
        assert len(router.sources) == 1
        assert source2 in router.sources

