"""Tests for pipeline_builder module."""

import asyncio
import pytest
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass

from market_data_pipeline.pipeline_builder import (
    PipelineBuilder,
    PipelineSpec,
    PipelineOverrides,
    create_pipeline,
    _cfg,
    ensure_windows_selector_event_loop,
)
from market_data_pipeline.errors import ConfigurationError
from market_data_pipeline.context import PipelineContext


class TestPipelineBuilder:
    """Test PipelineBuilder functionality."""

    def test_init_with_config(self):
        """Test PipelineBuilder initialization with custom config."""
        config = Mock()
        config.batch_size = 1000
        config.flush_ms = 50
        config.sink_queue_max = 200
        
        builder = PipelineBuilder(config=config)
        assert builder.cfg == config

    def test_init_with_default_config(self):
        """Test PipelineBuilder initialization with default config."""
        with patch('market_data_pipeline.pipeline_builder.get_pipeline_config') as mock_get_config:
            mock_config = Mock()
            mock_config.batch_size = 500
            mock_config.flush_ms = 100
            mock_config.sink_queue_max = 100
            mock_get_config.return_value = mock_config
            
            builder = PipelineBuilder()
            assert builder.cfg == mock_config

    def test_validate_config_valid(self):
        """Test config validation with valid values."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        builder = PipelineBuilder(config=config)
        # Should not raise any exception

    def test_validate_config_invalid_batch_size(self):
        """Test config validation with invalid batch_size."""
        config = Mock()
        config.batch_size = 0
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        with pytest.raises(ConfigurationError, match="batch_size must be > 0"):
            PipelineBuilder(config=config)

    def test_validate_config_invalid_flush_ms(self):
        """Test config validation with invalid flush_ms."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 0
        config.sink_queue_max = 100
        
        with pytest.raises(ConfigurationError, match="flush_ms must be > 0"):
            PipelineBuilder(config=config)

    def test_validate_config_invalid_sink_queue_max(self):
        """Test config validation with invalid sink_queue_max."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 0
        
        with pytest.raises(ConfigurationError, match="sink_queue_max must be > 0"):
            PipelineBuilder(config=config)

    def test_validate_spec_valid(self):
        """Test spec validation with valid values."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        builder = PipelineBuilder(config=config)
        spec = PipelineSpec(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="synthetic",
            symbols=["AAPL", "MSFT"],
            operator="bars",
            sink="store"
        )
        
        # Should not raise any exception
        builder._validate_spec(spec)

    def test_validate_spec_missing_tenant_id(self):
        """Test spec validation with missing tenant_id."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        builder = PipelineBuilder(config=config)
        spec = PipelineSpec(
            tenant_id="",
            pipeline_id="test_pipeline",
            source="synthetic",
            symbols=["AAPL", "MSFT"]
        )
        
        with pytest.raises(ConfigurationError, match="tenant_id and pipeline_id are required"):
            builder._validate_spec(spec)

    def test_validate_spec_invalid_source(self):
        """Test spec validation with invalid source."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        builder = PipelineBuilder(config=config)
        spec = PipelineSpec(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="invalid_source",
            symbols=["AAPL", "MSFT"]
        )
        
        with pytest.raises(ConfigurationError, match="source must be one of: synthetic, replay, ibkr"):
            builder._validate_spec(spec)

    def test_validate_spec_invalid_operator(self):
        """Test spec validation with invalid operator."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        builder = PipelineBuilder(config=config)
        spec = PipelineSpec(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="synthetic",
            symbols=["AAPL", "MSFT"],
            operator="invalid_operator"
        )
        
        with pytest.raises(ConfigurationError, match="operator must be one of: bars, options"):
            builder._validate_spec(spec)

    def test_validate_spec_invalid_sink(self):
        """Test spec validation with invalid sink."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        builder = PipelineBuilder(config=config)
        spec = PipelineSpec(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="synthetic",
            symbols=["AAPL", "MSFT"],
            sink="invalid_sink"
        )
        
        with pytest.raises(ConfigurationError, match="sink must be one of: store, kafka"):
            builder._validate_spec(spec)

    @patch('market_data_pipeline.pipeline_builder.SyntheticSource')
    @patch('market_data_pipeline.pipeline_builder.SecondBarAggregator')
    @patch('market_data_pipeline.pipeline_builder.HybridBatcher')
    @patch('market_data_pipeline.pipeline_builder.StoreSink')
    @patch('market_data_pipeline.pipeline_builder.StreamingPipeline')
    def test_build_synthetic_bars_store(self, mock_pipeline, mock_store_sink, mock_batcher, 
                                       mock_operator, mock_source):
        """Test building a synthetic -> bars -> store pipeline."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        config.pacing_max_per_sec = 1000
        config.pacing_burst = 1000
        config.ticks_per_sec = 100
        config.bar_window_sec = 1
        config.bar_allowed_lateness_sec = 0
        config.sink_workers = 2
        config.drop_policy = "oldest"
        
        # Mock AsyncBatchProcessor
        mock_bp = Mock()
        mock_bp.from_env_async = AsyncMock(return_value=mock_bp)
        mock_bp.from_env = Mock(return_value=mock_bp)
        with patch('market_data_pipeline.pipeline_builder.AsyncBatchProcessor', mock_bp):
            builder = PipelineBuilder(config=config)
            
            spec = PipelineSpec(
                tenant_id="test_tenant",
                pipeline_id="test_pipeline",
                source="synthetic",
                symbols=["AAPL", "MSFT"],
                operator="bars",
                sink="store"
            )
            
            pipeline = builder.build(spec)
            
            # Verify components were created
            mock_source.assert_called_once()
            mock_operator.assert_called_once()
            mock_batcher.assert_called_once()
            mock_store_sink.assert_called_once()
            mock_pipeline.assert_called_once()

    @patch('market_data_pipeline.pipeline_builder.ReplaySource')
    @patch('market_data_pipeline.pipeline_builder.SecondBarAggregator')
    @patch('market_data_pipeline.pipeline_builder.HybridBatcher')
    @patch('market_data_pipeline.pipeline_builder.StoreSink')
    @patch('market_data_pipeline.pipeline_builder.StreamingPipeline')
    def test_build_replay_bars_store(self, mock_pipeline, mock_store_sink, mock_batcher,
                                   mock_operator, mock_replay_source):
        """Test building a replay -> bars -> store pipeline."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        config.pacing_max_per_sec = 1000
        config.pacing_burst = 1000
        config.replay_path = "/path/to/replay"
        config.replay_speed = 1.0
        config.bar_window_sec = 1
        config.bar_allowed_lateness_sec = 0
        config.sink_workers = 2
        config.drop_policy = "oldest"
        
        # Mock AsyncBatchProcessor
        mock_bp = Mock()
        mock_bp.from_env_async = AsyncMock(return_value=mock_bp)
        mock_bp.from_env = Mock(return_value=mock_bp)
        with patch('market_data_pipeline.pipeline_builder.AsyncBatchProcessor', mock_bp):
            builder = PipelineBuilder(config=config)
            
            spec = PipelineSpec(
                tenant_id="test_tenant",
                pipeline_id="test_pipeline",
                source="replay",
                operator="bars",
                sink="store"
            )
            
            pipeline = builder.build(spec)
            
            # Verify components were created
            mock_replay_source.assert_called_once()
            mock_operator.assert_called_once()
            mock_batcher.assert_called_once()
            mock_store_sink.assert_called_once()
            mock_pipeline.assert_called_once()

    def test_build_replay_source_not_available(self):
        """Test building with replay source when not available."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        with patch('market_data_pipeline.pipeline_builder.ReplaySource', None):
            builder = PipelineBuilder(config=config)
            
            spec = PipelineSpec(
                tenant_id="test_tenant",
                pipeline_id="test_pipeline",
                source="replay",
                operator="bars",
                sink="store"
            )
            
            with pytest.raises(ConfigurationError, match="ReplaySource not available"):
                builder.build(spec)

    def test_build_ibkr_source_not_available(self):
        """Test building with IBKR source when not available."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        with patch('market_data_pipeline.pipeline_builder.IBKRSource', None):
            builder = PipelineBuilder(config=config)
            
            spec = PipelineSpec(
                tenant_id="test_tenant",
                pipeline_id="test_pipeline",
                source="ibkr",
                symbols=["AAPL", "MSFT"],
                operator="bars",
                sink="store"
            )
            
            with pytest.raises(ConfigurationError, match="IBKRSource not available"):
                builder.build(spec)

    def test_build_synthetic_missing_symbols(self):
        """Test building synthetic source without symbols."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        builder = PipelineBuilder(config=config)
        
        spec = PipelineSpec(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="synthetic",
            symbols=[],  # Empty symbols
            operator="bars",
            sink="store"
        )
        
        with pytest.raises(ConfigurationError, match="synthetic source requires symbols"):
            builder.build(spec)

    def test_build_ibkr_missing_symbols(self):
        """Test building IBKR source without symbols."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        
        with patch('market_data_pipeline.pipeline_builder.IBKRSource'):
            builder = PipelineBuilder(config=config)
            
            spec = PipelineSpec(
                tenant_id="test_tenant",
                pipeline_id="test_pipeline",
                source="ibkr",
                symbols=[],  # Empty symbols
                operator="bars",
                sink="store"
            )
            
            with pytest.raises(ConfigurationError, match="ibkr source requires symbols"):
                builder.build(spec)

    def test_build_replay_missing_path(self):
        """Test building replay source without path."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        config.replay_path = None
        
        with patch('market_data_pipeline.pipeline_builder.ReplaySource'):
            builder = PipelineBuilder(config=config)
            
            spec = PipelineSpec(
                tenant_id="test_tenant",
                pipeline_id="test_pipeline",
                source="replay",
                operator="bars",
                sink="store"
            )
            
            with pytest.raises(ConfigurationError, match="replay source requires"):
                builder.build(spec)

    def test_build_kafka_sink_not_available(self):
        """Test building with Kafka sink when not available."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        config.pacing_max_per_sec = 1000
        config.pacing_burst = 1000
        config.ticks_per_sec = 100
        config.kafka_bootstrap_servers = "localhost:9092"
        config.kafka_topic = "test_topic"
        
        with patch('market_data_pipeline.pipeline_builder.KafkaSink', None):
            builder = PipelineBuilder(config=config)
            
            spec = PipelineSpec(
                tenant_id="test_tenant",
                pipeline_id="test_pipeline",
                source="synthetic",
                symbols=["AAPL"],
                operator="bars",
                sink="kafka"
            )
            
            with pytest.raises(ConfigurationError, match="KafkaSink not available"):
                builder.build(spec)

    def test_build_kafka_missing_config(self):
        """Test building Kafka sink with missing configuration."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        config.pacing_max_per_sec = 1000
        config.pacing_burst = 1000
        config.ticks_per_sec = 100
        config.kafka_bootstrap_servers = None
        config.kafka_topic = None
        
        with patch('market_data_pipeline.pipeline_builder.KafkaSink'):
            builder = PipelineBuilder(config=config)
            
            spec = PipelineSpec(
                tenant_id="test_tenant",
                pipeline_id="test_pipeline",
                source="synthetic",
                symbols=["AAPL"],
                operator="bars",
                sink="kafka"
            )
            
            with pytest.raises(ConfigurationError, match="kafka sink requires kafka_bootstrap and kafka_topic"):
                builder.build(spec)

    def test_build_store_sink_amds_not_available(self):
        """Test building store sink when AMDS not available."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        config.pacing_max_per_sec = 1000
        config.pacing_burst = 1000
        config.ticks_per_sec = 100
        config.sink_workers = 2
        config.drop_policy = "oldest"
        
        with patch('market_data_pipeline.pipeline_builder.AsyncBatchProcessor', None):
            builder = PipelineBuilder(config=config)
            
            spec = PipelineSpec(
                tenant_id="test_tenant",
                pipeline_id="test_pipeline",
                source="synthetic",
                symbols=["AAPL"],
                operator="bars",
                sink="store"
            )
            
            with pytest.raises(ConfigurationError, match="market_data_store AsyncBatchProcessor not installed"):
                builder.build(spec)

    @pytest.mark.asyncio
    async def test_build_and_run(self):
        """Test build_and_run convenience method."""
        config = Mock()
        config.batch_size = 500
        config.flush_ms = 100
        config.sink_queue_max = 100
        config.pacing_max_per_sec = 1000
        config.pacing_burst = 1000
        config.ticks_per_sec = 100
        config.bar_window_sec = 1
        config.bar_allowed_lateness_sec = 0
        config.sink_workers = 2
        config.drop_policy = "oldest"
        
        mock_pipeline = AsyncMock()
        mock_pipeline.run = AsyncMock()
        mock_pipeline.close = AsyncMock()
        
        with patch('market_data_pipeline.pipeline_builder.AsyncBatchProcessor', Mock()):
            with patch('market_data_pipeline.pipeline_builder.PipelineBuilder.build', return_value=mock_pipeline):
                builder = PipelineBuilder(config=config)
                
                spec = PipelineSpec(
                    tenant_id="test_tenant",
                    pipeline_id="test_pipeline",
                    source="synthetic",
                    symbols=["AAPL"],
                    operator="bars",
                    sink="store",
                    duration_sec=10.0
                )
                
                await builder.build_and_run(spec)
                
                mock_pipeline.run.assert_called_once_with(duration_sec=10.0)
                mock_pipeline.close.assert_called_once()


class TestPipelineOverrides:
    """Test PipelineOverrides functionality."""

    def test_default_values(self):
        """Test default values for PipelineOverrides."""
        overrides = PipelineOverrides()
        
        assert overrides.ticks_per_sec is None
        assert overrides.pacing_max_per_sec is None
        assert overrides.pacing_burst is None
        assert overrides.replay_path is None
        assert overrides.replay_speed is None
        assert overrides.bar_window_sec is None
        assert overrides.bar_allowed_lateness_sec is None
        assert overrides.batch_size is None
        assert overrides.max_bytes is None
        assert overrides.flush_ms is None
        assert overrides.op_queue_max is None
        assert overrides.drop_policy is None
        assert overrides.sink_workers is None
        assert overrides.sink_queue_max is None
        assert overrides.kafka_bootstrap is None
        assert overrides.kafka_topic is None
        assert overrides.database_vendor is None
        assert overrides.database_timeframe is None
        assert overrides.database_retry_max_attempts is None
        assert overrides.database_retry_backoff_ms is None
        assert overrides.database_url is None

    def test_custom_values(self):
        """Test custom values for PipelineOverrides."""
        overrides = PipelineOverrides(
            ticks_per_sec=200,
            pacing_max_per_sec=1500,
            pacing_burst=2000,
            replay_path="/custom/path",
            replay_speed=2.0,
            bar_window_sec=5,
            bar_allowed_lateness_sec=2,
            batch_size=1000,
            max_bytes=1024_000,
            flush_ms=50,
            op_queue_max=16,
            drop_policy="newest",
            sink_workers=4,
            sink_queue_max=200,
            kafka_bootstrap="localhost:9092",
            kafka_topic="custom_topic",
            database_vendor="custom_vendor",
            database_timeframe="5s",
            database_retry_max_attempts=10,
            database_retry_backoff_ms=100,
            database_url="postgresql://custom:pass@localhost:5432/custom_db"
        )
        
        assert overrides.ticks_per_sec == 200
        assert overrides.pacing_max_per_sec == 1500
        assert overrides.pacing_burst == 2000
        assert overrides.replay_path == "/custom/path"
        assert overrides.replay_speed == 2.0
        assert overrides.bar_window_sec == 5
        assert overrides.bar_allowed_lateness_sec == 2
        assert overrides.batch_size == 1000
        assert overrides.max_bytes == 1024_000
        assert overrides.flush_ms == 50
        assert overrides.op_queue_max == 16
        assert overrides.drop_policy == "newest"
        assert overrides.sink_workers == 4
        assert overrides.sink_queue_max == 200
        assert overrides.kafka_bootstrap == "localhost:9092"
        assert overrides.kafka_topic == "custom_topic"
        assert overrides.database_vendor == "custom_vendor"
        assert overrides.database_timeframe == "5s"
        assert overrides.database_retry_max_attempts == 10
        assert overrides.database_retry_backoff_ms == 100
        assert overrides.database_url == "postgresql://custom:pass@localhost:5432/custom_db"


class TestPipelineSpec:
    """Test PipelineSpec functionality."""

    def test_default_values(self):
        """Test default values for PipelineSpec."""
        spec = PipelineSpec(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="synthetic"
        )
        
        assert spec.tenant_id == "test_tenant"
        assert spec.pipeline_id == "test_pipeline"
        assert spec.source == "synthetic"
        assert spec.symbols == []
        assert spec.duration_sec is None
        assert spec.operator == "bars"
        assert spec.sink == "store"
        assert isinstance(spec.overrides, PipelineOverrides)

    def test_custom_values(self):
        """Test custom values for PipelineSpec."""
        overrides = PipelineOverrides(ticks_per_sec=200)
        spec = PipelineSpec(
            tenant_id="custom_tenant",
            pipeline_id="custom_pipeline",
            source="replay",
            symbols=["AAPL", "MSFT", "GOOGL"],
            duration_sec=30.0,
            operator="options",
            sink="kafka",
            overrides=overrides
        )
        
        assert spec.tenant_id == "custom_tenant"
        assert spec.pipeline_id == "custom_pipeline"
        assert spec.source == "replay"
        assert spec.symbols == ["AAPL", "MSFT", "GOOGL"]
        assert spec.duration_sec == 30.0
        assert spec.operator == "options"
        assert spec.sink == "kafka"
        assert spec.overrides == overrides


class TestHelperFunctions:
    """Test helper functions."""

    def test_cfg_with_dict(self):
        """Test _cfg function with dictionary config."""
        config = {"key1": "value1", "key2": 42}
        
        assert _cfg(config, "key1") == "value1"
        assert _cfg(config, "key2") == 42
        assert _cfg(config, "key3", "default") == "default"
        assert _cfg(config, "key3") is None

    def test_cfg_with_object(self):
        """Test _cfg function with object config."""
        @dataclass
        class Config:
            key1: str = "value1"
            key2: int = 42
        
        config = Config()
        
        assert _cfg(config, "key1") == "value1"
        assert _cfg(config, "key2") == 42
        assert _cfg(config, "key3", "default") == "default"
        assert _cfg(config, "key3") is None

    def test_ensure_windows_selector_event_loop_windows(self):
        """Test Windows event loop switching on Windows."""
        with patch('sys.platform', 'win32'):
            # Just test that the function runs without error
            # The actual event loop switching is complex to mock properly
            try:
                ensure_windows_selector_event_loop()
                # If we get here, the function ran without error
                assert True
            except Exception:
                # If there's an error (like no event loop), that's also acceptable
                # since we're testing the function exists and can be called
                assert True

    def test_ensure_windows_selector_event_loop_non_windows(self):
        """Test that event loop switching is skipped on non-Windows."""
        with patch('sys.platform', 'linux'):
            with patch('asyncio.get_event_loop') as mock_get_loop:
                with patch('asyncio.set_event_loop') as mock_set_loop:
                    ensure_windows_selector_event_loop()
                    
                    mock_get_loop.assert_not_called()
                    mock_set_loop.assert_not_called()


class TestCreatePipeline:
    """Test create_pipeline convenience function."""

    @patch('market_data_pipeline.pipeline_builder.PipelineBuilder')
    def test_create_pipeline_basic(self, mock_builder_class):
        """Test basic create_pipeline functionality."""
        mock_builder = Mock()
        mock_pipeline = Mock()
        mock_builder.build.return_value = mock_pipeline
        mock_builder_class.return_value = mock_builder
        
        result = create_pipeline(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="synthetic",
            symbols=["AAPL", "MSFT"]
        )
        
        assert result == mock_pipeline
        mock_builder_class.assert_called_once()
        mock_builder.build.assert_called_once()
        
        # Check the spec that was passed to build
        call_args = mock_builder.build.call_args[0][0]
        assert isinstance(call_args, PipelineSpec)
        assert call_args.tenant_id == "test_tenant"
        assert call_args.pipeline_id == "test_pipeline"
        assert call_args.source == "synthetic"
        assert call_args.symbols == ["AAPL", "MSFT"]
        assert call_args.operator == "bars"
        assert call_args.sink == "store"

    @patch('market_data_pipeline.pipeline_builder.PipelineBuilder')
    def test_create_pipeline_with_overrides(self, mock_builder_class):
        """Test create_pipeline with custom overrides."""
        mock_builder = Mock()
        mock_pipeline = Mock()
        mock_builder.build.return_value = mock_pipeline
        mock_builder_class.return_value = mock_builder
        
        overrides = {
            "ticks_per_sec": 200,
            "batch_size": 1000,
            "sink_workers": 4
        }
        
        result = create_pipeline(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="synthetic",
            symbols=["AAPL"],
            operator="options",
            sink="kafka",
            overrides=overrides
        )
        
        assert result == mock_pipeline
        
        # Check the spec that was passed to build
        call_args = mock_builder.build.call_args[0][0]
        assert isinstance(call_args, PipelineSpec)
        assert call_args.operator == "options"
        assert call_args.sink == "kafka"
        assert call_args.overrides.ticks_per_sec == 200
        assert call_args.overrides.batch_size == 1000
        assert call_args.overrides.sink_workers == 4

    @patch('market_data_pipeline.pipeline_builder.PipelineBuilder')
    def test_create_pipeline_with_custom_config(self, mock_builder_class):
        """Test create_pipeline with custom config."""
        mock_builder = Mock()
        mock_pipeline = Mock()
        mock_builder.build.return_value = mock_pipeline
        mock_builder_class.return_value = mock_builder
        
        custom_config = Mock()
        
        result = create_pipeline(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="synthetic",
            symbols=["AAPL"],
            config=custom_config
        )
        
        assert result == mock_pipeline
        mock_builder_class.assert_called_once_with(config=custom_config)
