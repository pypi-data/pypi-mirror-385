"""Tests for the DatabaseSink implementation."""

import asyncio
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from market_data_pipeline.sink.database import DatabaseSink, DatabaseSinkSettings
from market_data_pipeline.context import PipelineContext
from market_data_pipeline.types import Bar


class AsyncCallRecorder:
    """Records calls to async functions for testing."""
    def __init__(self, ret_fn):
        self.count = 0
        self._ret_fn = ret_fn
    
    async def __call__(self, *args, **kwargs):
        self.count += 1
        return await self._ret_fn(*args, **kwargs)


class TestDatabaseSinkSettings:
    """Test DatabaseSinkSettings dataclass."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = DatabaseSinkSettings()
        assert settings.vendor == "market_data_pipeline"
        assert settings.timeframe == "1s"
        assert settings.workers == 2
        assert settings.queue_max == 200
        assert settings.backpressure_policy == "block"
        assert settings.retry_max_attempts == 5
        assert settings.retry_backoff_ms == 50
    
    def test_custom_settings(self):
        """Test custom settings values."""
        settings = DatabaseSinkSettings(
            vendor="test_vendor",
            timeframe="5m",
            workers=4,
            queue_max=500,
            backpressure_policy="drop_oldest",
            retry_max_attempts=3,
            retry_backoff_ms=100,
        )
        assert settings.vendor == "test_vendor"
        assert settings.timeframe == "5m"
        assert settings.workers == 4
        assert settings.queue_max == 500
        assert settings.backpressure_policy == "drop_oldest"
        assert settings.retry_max_attempts == 3
        assert settings.retry_backoff_ms == 100


class TestDatabaseSink:
    """Test DatabaseSink functionality."""
    
    @pytest.fixture
    def mock_processor(self):
        """Create a mock processor for testing."""
        async def fake_upsert(bars):
            # bars will be list[dict] after _to_records conversion
            return len(bars)
        
        processor = AsyncMock()
        processor.upsert_bars = AsyncCallRecorder(fake_upsert)
        return processor
    
    @pytest.fixture
    def sink(self, mock_processor):
        """Create a DatabaseSink instance for testing."""
        ctx = PipelineContext(tenant_id="test_tenant", pipeline_id="test_pipeline")
        settings = DatabaseSinkSettings(workers=1, queue_max=10)
        return DatabaseSink(
            tenant_id="test_tenant",
            settings=settings,
            ctx=ctx,
            processor=mock_processor,
        )
    
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
            ),
            Bar(
                symbol="MSFT",
                timestamp=datetime.now(),
                open=Decimal("300.00"),
                high=Decimal("301.50"),
                low=Decimal("299.00"),
                close=Decimal("300.50"),
                volume=Decimal("2000"),
                vwap=Decimal("300.25"),
                trade_count=75,
                source="test",
                metadata={"test": True}
            )
        ]
    
    def test_init(self):
        """Test DatabaseSink initialization."""
        ctx = PipelineContext(tenant_id="test_tenant", pipeline_id="test_pipeline")
        settings = DatabaseSinkSettings()
        sink = DatabaseSink(
            tenant_id="test_tenant",
            settings=settings,
            ctx=ctx,
        )
        
        assert sink.tenant_id == "test_tenant"
        assert sink.settings == settings
        assert sink.ctx == ctx
        assert sink._processor is None
        assert sink._queue is None
        assert sink._workers == []
        assert sink._closed is False
        
        # Test metrics initialization
        metrics = sink.get_metrics()
        assert metrics["batches_in"] == 0
        assert metrics["batches_written"] == 0
        assert metrics["batches_failed"] == 0
        assert metrics["items_written"] == 0
        assert metrics["retries"] == 0
    
    def test_init_requires_tenant_id(self):
        """Test that tenant_id is required."""
        with pytest.raises(ValueError, match="tenant_id is required"):
            DatabaseSink(tenant_id="")
    
    def test_capabilities(self, sink):
        """Test sink capabilities."""
        from market_data_pipeline.sink.capabilities import SinkCapabilities
        assert sink.capabilities == SinkCapabilities.BATCH_WRITES
    
    @pytest.mark.asyncio
    async def test_start(self, sink, mock_processor):
        """Test sink start functionality."""
        await sink.start()
        
        assert sink._queue is not None
        assert len(sink._workers) == 1  # workers=1 in fixture
        assert not sink._closed
    
    @pytest.mark.asyncio
    async def test_write_empty_batch(self, sink):
        """Test writing empty batch."""
        try:
            await sink.start()
            await sink.write([])  # Should not raise and should not process
        finally:
            await sink.close(drain=True)
    
    @pytest.mark.asyncio
    async def test_write_success(self, sink, sample_bars, mock_processor):
        """Test successful write operation."""
        try:
            await sink.start()
            await sink.write(sample_bars)
            
            # Yield so worker consumes the batch
            await asyncio.sleep(0)
            
            # Wait for processing to complete
            await asyncio.wait_for(sink.flush(), timeout=1.0)
            
            # Check that processor was called
            assert mock_processor.upsert_bars.count == 1
            
            # Check metrics
            metrics = sink.get_metrics()
            assert metrics["batches_in"] == 1
            assert metrics["batches_written"] == 1
            assert metrics["items_written"] == 2  # 2 bars
        finally:
            await sink.close(drain=True)
    
    @pytest.mark.asyncio
    async def test_write_closed_sink(self, sink, sample_bars):
        """Test writing to closed sink raises error."""
        sink._closed = True
        with pytest.raises(RuntimeError, match="DatabaseSink is closed"):
            await sink.write(sample_bars)
    
    @pytest.mark.asyncio
    async def test_flush(self, sink):
        """Test flush functionality."""
        try:
            await sink.start()
            await sink.flush()  # Should not raise
        finally:
            await sink.close(drain=True)
    
    @pytest.mark.asyncio
    async def test_close_with_drain(self, sink, mock_processor):
        """Test close with drain."""
        await sink.start()
        await sink.close(drain=True)
        
        assert sink._closed is True
        # Workers should be stopped
        for worker in sink._workers:
            assert worker.done()
    
    @pytest.mark.asyncio
    async def test_close_without_drain(self, sink):
        """Test close without drain."""
        await sink.start()
        await sink.close(drain=False)
        
        assert sink._closed is True
        # Workers should be cancelled when drain=False
        for worker in sink._workers:
            assert worker.cancelled() or worker.done()
    
    @pytest.mark.asyncio
    async def test_retry_logic(self, sink, sample_bars):
        """Test retry logic on transient failures."""
        try:
            # Mock processor to fail first time, succeed second time
            mock_processor = AsyncMock()
            call_count = 0
            
            call_state = {"n": 0}
            async def flaky(bars):
                call_state["n"] += 1
                if call_state["n"] == 1:
                    raise Exception("Connection timeout")
                return len(bars)
            
            mock_processor.upsert_bars = AsyncCallRecorder(flaky)
            sink._processor = mock_processor
            
            await sink.start()
            await sink.write(sample_bars)
            
            # Yield so worker consumes the batch
            await asyncio.sleep(0)
            
            # Wait for processing to complete
            await asyncio.wait_for(sink.flush(), timeout=1.0)
            
            # Should have retried and eventually succeeded
            assert mock_processor.upsert_bars.count == 2
            metrics = sink.get_metrics()
            assert metrics["retries"] == 1
            assert metrics["batches_written"] == 1
        finally:
            await sink.close(drain=True)
    
    @pytest.mark.asyncio
    async def test_backpressure_drop_oldest(self, sample_bars):
        """Test backpressure policy 'drop_oldest'."""
        settings = DatabaseSinkSettings(
            workers=1,
            queue_max=1,  # Very small queue
            backpressure_policy="drop_oldest"
        )
        mock_processor = AsyncMock()
        async def fake_upsert(bars):
            return len(bars)
        mock_processor.upsert_bars = AsyncCallRecorder(fake_upsert)
        sink = DatabaseSink(
            tenant_id="test_tenant",
            settings=settings,
            processor=mock_processor
        )
        
        try:
            await sink.start()
            
            # Fill the queue
            await sink.write(sample_bars)
            
            # This should drop the previous batch
            await sink.write(sample_bars)
            
            # Yield so worker consumes the batches
            await asyncio.sleep(0)
            
            # Wait for processing to complete
            await asyncio.wait_for(sink.flush(), timeout=1.0)
            
            # Should have processed at least one batch
            metrics = sink.get_metrics()
            assert metrics["batches_in"] == 2
            assert metrics["batches_written"] >= 1
        finally:
            await sink.close(drain=True)
    
    @pytest.mark.asyncio
    async def test_backpressure_drop_newest(self, sample_bars):
        """Test backpressure policy 'drop_newest'."""
        settings = DatabaseSinkSettings(
            workers=1,
            queue_max=1,  # Very small queue
            backpressure_policy="drop_newest"
        )
        mock_processor = AsyncMock()
        async def fake_upsert(bars):
            return len(bars)
        mock_processor.upsert_bars = AsyncCallRecorder(fake_upsert)
        sink = DatabaseSink(
            tenant_id="test_tenant",
            settings=settings,
            processor=mock_processor
        )
        
        try:
            await sink.start()
            
            # Fill the queue
            await sink.write(sample_bars)
            
            # This should be dropped
            await sink.write(sample_bars)
            
            # Yield so worker consumes the batches
            await asyncio.sleep(0)
            
            # Wait for processing to complete
            await asyncio.wait_for(sink.flush(), timeout=1.0)
            
            # Should have processed only the first batch
            metrics = sink.get_metrics()
            assert metrics["batches_in"] == 2
            assert metrics["batches_written"] == 1
        finally:
            await sink.close(drain=True)
    
    def test_to_records_mapping(self, sink, sample_bars):
        """Test Bar to record mapping."""
        records = list(sink._to_records(sample_bars))
        
        assert len(records) == 2
        
        # Check first record
        record = records[0]
        assert record["tenant_id"] == "test_tenant"
        assert record["vendor"] == "market_data_pipeline"
        assert record["symbol"] == "AAPL"
        assert record["timeframe"] == "1s"
        assert record["open_price"] == 150.0
        assert record["high_price"] == 151.0
        assert record["low_price"] == 149.5
        assert record["close_price"] == 150.75
        assert record["volume"] == 1000
        assert record["trade_count"] == 50
        assert record["vwap"] == 150.25
        assert record["metadata"] == {"test": True}
    
    def test_is_transient_error_detection(self):
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


class TestDatabaseSinkIntegration:
    """Integration tests for DatabaseSink."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow from start to close."""
        mock_processor = AsyncMock()
        async def fake_upsert(bars):
            return len(bars)
        mock_processor.upsert_bars = AsyncCallRecorder(fake_upsert)
        ctx = PipelineContext(tenant_id="test_tenant", pipeline_id="test_pipeline")
        settings = DatabaseSinkSettings(workers=1, queue_max=10)
        
        sink = DatabaseSink(
            tenant_id="test_tenant",
            settings=settings,
            ctx=ctx,
            processor=mock_processor,
        )
        
        # Create test data
        bars = [
            Bar(
                symbol="TEST",
                timestamp=datetime.now(),
                open=Decimal("100.00"),
                high=Decimal("101.00"),
                low=Decimal("99.00"),
                close=Decimal("100.50"),
                volume=Decimal("500"),
                source="test"
            )
        ]
        
        try:
            # Start sink
            await sink.start()
            
            # Write data
            await sink.write(bars)
            
            # Yield so worker consumes the batch
            await asyncio.sleep(0)
            
            # Flush to ensure processing completes
            await asyncio.wait_for(sink.flush(), timeout=1.0)
            
            # Check metrics
            metrics = sink.get_metrics()
            assert metrics["batches_in"] == 1
            assert metrics["batches_written"] == 1
            assert metrics["items_written"] == 1
            
            # Verify processor was called
            assert mock_processor.upsert_bars.count == 1
            
        finally:
            # Close sink
            await sink.close()
            
            # Verify closed state
            assert sink._closed is True
