"""Simplified DatabaseSink tests that bypass the worker queue complexity."""

import asyncio
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock

from market_data_pipeline.sink.database import DatabaseSink, DatabaseSinkSettings
from market_data_pipeline.context import PipelineContext
from market_data_pipeline.types import Bar


class TestDatabaseSinkSimple:
    """Simplified tests that avoid the worker queue complexity."""
    
    @pytest.fixture
    def sample_bars(self):
        """Create sample Bar objects for testing."""
        return [
            Bar(
                symbol="AAPL",
                timestamp=datetime.now(),
                open=Decimal("150.00"),
                high=Decimal("151.00"),
                low=Decimal("149.50"),
                close=Decimal("150.75"),
                volume=Decimal("1000"),
                vwap=Decimal("150.25"),
                trade_count=50,
                source="test",
                metadata={"test": True}
            )
        ]
    
    @pytest.mark.asyncio
    async def test_direct_commit(self, sample_bars):
        """Test _commit directly without worker queue."""
        # Create a simple mock processor
        mock_processor = AsyncMock()
        mock_processor.upsert_bars = AsyncMock(return_value=1)
        
        # Create sink with 0 workers to avoid queue complexity
        settings = DatabaseSinkSettings(workers=0, queue_max=1)
        sink = DatabaseSink(
            tenant_id="test_tenant",
            settings=settings,
            processor=mock_processor
        )
        
        try:
            await sink.start()
            
            # Test _commit directly
            result = await sink._commit(sample_bars)
            assert result == 1
            mock_processor.upsert_bars.assert_called_once()
            
        finally:
            await sink.close()
    
    @pytest.mark.asyncio
    async def test_to_records_mapping(self, sample_bars):
        """Test Bar to record mapping."""
        sink = DatabaseSink(tenant_id="test_tenant")
        records = list(sink._to_records(sample_bars))
        
        assert len(records) == 1
        record = records[0]
        assert record["tenant_id"] == "test_tenant"
        assert record["symbol"] == "AAPL"
        assert record["open_price"] == 150.0
        assert record["high_price"] == 151.0
        assert record["low_price"] == 149.5
        assert record["close_price"] == 150.75
        assert record["volume"] == 1000
        assert record["trade_count"] == 50
        assert record["vwap"] == 150.25
        assert record["metadata"] == {"test": True}
    
    @pytest.mark.asyncio
    async def test_write_with_zero_workers(self, sample_bars):
        """Test write with 0 workers (should process immediately)."""
        mock_processor = AsyncMock()
        mock_processor.upsert_bars = AsyncMock(return_value=1)
        
        settings = DatabaseSinkSettings(workers=0, queue_max=1)
        sink = DatabaseSink(
            tenant_id="test_tenant",
            settings=settings,
            processor=mock_processor
        )
        
        try:
            await sink.start()
            await sink.write(sample_bars)
            
            # With 0 workers, should process immediately
            await asyncio.sleep(0.01)  # Small delay for processing
            
            metrics = sink.get_metrics()
            assert metrics["batches_in"] == 1
            # Note: with 0 workers, batches_written might be 0 since no worker processed it
            
        finally:
            await sink.close()
    
    def test_settings_defaults(self):
        """Test DatabaseSinkSettings defaults."""
        settings = DatabaseSinkSettings()
        assert settings.vendor == "market_data_pipeline"
        assert settings.timeframe == "1s"
        assert settings.workers == 2
        assert settings.queue_max == 200
        assert settings.backpressure_policy == "block"
        assert settings.retry_max_attempts == 5
        assert settings.retry_backoff_ms == 50
    
    def test_transient_error_detection(self):
        """Test transient error detection."""
        # Transient errors
        assert DatabaseSink._is_transient(Exception("Connection timeout"))
        assert DatabaseSink._is_transient(Exception("Temporarily unavailable"))
        assert DatabaseSink._is_transient(Exception("Deadlock detected"))
        assert DatabaseSink._is_transient(Exception("Connection reset"))
        
        # Non-transient errors
        assert not DatabaseSink._is_transient(Exception("Invalid data"))
        assert not DatabaseSink._is_transient(Exception("Permission denied"))
        assert not DatabaseSink._is_transient(Exception("Syntax error"))
    
    @pytest.mark.asyncio
    async def test_retry_logic_direct(self, sample_bars):
        """Test retry logic directly without worker queue."""
        call_count = 0
        
        async def flaky_upsert(bars):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Connection timeout")
            return len(bars)
        
        mock_processor = AsyncMock()
        mock_processor.upsert_bars = flaky_upsert
        
        settings = DatabaseSinkSettings(workers=0, retry_max_attempts=3)
        sink = DatabaseSink(
            tenant_id="test_tenant",
            settings=settings,
            processor=mock_processor
        )
        
        try:
            await sink.start()
            
            # Test _process_with_retry directly
            await sink._process_with_retry(sample_bars, "test_worker")
            
            assert call_count == 2  # Should have retried once
            metrics = sink.get_metrics()
            assert metrics["retries"] == 1
            assert metrics["batches_written"] == 1
            
        finally:
            await sink.close()
