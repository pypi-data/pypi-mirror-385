"""
Integration tests for typed overrides support.

This test verifies that PipelineOverrides and DatabaseSinkSettings can be
passed as typed dataclasses instead of dicts, making the API more type-safe.
"""

import pytest
from market_data_pipeline.pipeline_builder import (
    create_pipeline as upstream_create_pipeline,
    PipelineOverrides,
)
from market_data_pipeline.sink.database import DatabaseSinkSettings


class TestTypedOverridesBackwardCompatibility:
    """Test that dict overrides still work (backward compatibility)."""

    def test_dict_overrides_synthetic_database(self):
        """Test dict overrides with synthetic source and database sink."""
        pipeline = upstream_create_pipeline(
            tenant_id='test',
            pipeline_id='test_dict',
            source='synthetic',
            symbols=['AAPL'],
            sink='database',
            overrides={
                'batch_size': 1000,
                'flush_ms': 500,
                'database_url': 'postgresql://test:test@localhost:5432/test',
            }
        )
        
        assert pipeline is not None
        assert pipeline.ctx.tenant_id == 'test'
        assert pipeline.ctx.pipeline_id == 'test_dict'


class TestTypedOverridesNewPattern:
    """Test that typed PipelineOverrides work."""

    def test_typed_overrides_basic(self):
        """Test basic typed overrides."""
        overrides = PipelineOverrides(
            batch_size=2000,
            flush_ms=1000,
            ticks_per_sec=100,
            database_url='postgresql://test:test@localhost:5432/test',
        )
        
        pipeline = upstream_create_pipeline(
            tenant_id='test',
            pipeline_id='test_typed',
            source='synthetic',
            symbols=['MSFT'],
            sink='database',
            overrides=overrides,
        )
        
        assert pipeline is not None
        assert pipeline.ctx.tenant_id == 'test'
        assert pipeline.ctx.pipeline_id == 'test_typed'

    def test_typed_overrides_with_database_settings(self):
        """Test typed overrides with DatabaseSinkSettings."""
        db_settings = DatabaseSinkSettings(
            vendor='market_data_core',
            timeframe='1s',
            workers=4,
            queue_max=500,
            backpressure_policy='drop_oldest',
            retry_max_attempts=10,
            retry_backoff_ms=100,
        )
        
        overrides = PipelineOverrides(
            batch_size=3000,
            flush_ms=2000,
            database_url='postgresql://test:test@localhost:5432/test',
            database_settings=db_settings,
        )
        
        pipeline = upstream_create_pipeline(
            tenant_id='test',
            pipeline_id='test_full_typed',
            source='synthetic',
            symbols=['GOOGL'],
            sink='database',
            overrides=overrides,
        )
        
        assert pipeline is not None
        assert pipeline.ctx.tenant_id == 'test'
        assert pipeline.ctx.pipeline_id == 'test_full_typed'


class TestAPIWithTypedOverrides:
    """Test that the high-level API produces and uses typed overrides."""

    def test_api_config_produces_typed_overrides(self):
        """Test that SimplePipelineConfigBuilder produces PipelineOverrides."""
        from market_data_pipeline import (
            SimplePipelineConfig,
            SimplePipelineConfigBuilder,
            DropPolicy,
        )
        
        config = SimplePipelineConfig(
            tenant_id='test',
            pipeline_id='test_api',
            symbols=['TSLA'],
            batch_size=1500,
            drop_policy=DropPolicy.OLDEST,
            database_url='postgresql://test:test@localhost:5432/test',
        )
        
        builder = SimplePipelineConfigBuilder()
        overrides = builder.build(config)
        
        # Verify it's a typed PipelineOverrides, not a dict
        assert isinstance(overrides, PipelineOverrides)
        assert overrides.batch_size == 1500
        assert overrides.drop_policy == 'oldest'
        
        # Verify it has database_settings
        assert overrides.database_settings is not None
        assert isinstance(overrides.database_settings, DatabaseSinkSettings)
        assert overrides.database_settings.vendor == 'market_data_core'

    def test_api_factory_uses_typed_overrides(self):
        """Test that SimplePipelineFactory passes typed overrides to upstream."""
        from market_data_pipeline import (
            SimplePipelineConfig,
            simple_factory,
            DropPolicy,
        )
        
        config = SimplePipelineConfig(
            tenant_id='test',
            pipeline_id='test_factory',
            symbols=['NVDA'],
            batch_size=2000,
            drop_policy=DropPolicy.NEWEST,
            database_url='postgresql://test:test@localhost:5432/test',
        )
        
        # This internally builds PipelineOverrides and passes it to upstream
        pipeline = simple_factory.create(config)
        
        assert pipeline is not None
        assert pipeline.ctx.tenant_id == 'test'
        assert pipeline.ctx.pipeline_id == 'test_factory'

    def test_api_high_level_function(self):
        """Test that create_pipeline high-level function works."""
        from market_data_pipeline import create_pipeline, DropPolicy
        
        # This should internally create config, build overrides, and pass to upstream
        pipeline = create_pipeline(
            tenant_id='test',
            pipeline_id='test_high_level',
            symbols=['AAPL', 'MSFT'],
            source='synthetic',
            sink='database',
            batch_size=2500,
            drop_policy='oldest',
            database_url='postgresql://test:test@localhost:5432/test',
        )
        
        assert pipeline is not None
        assert pipeline.ctx.tenant_id == 'test'
        assert pipeline.ctx.pipeline_id == 'test_high_level'


class TestMarketDataCoreUsagePattern:
    """Test the usage pattern that market_data_core will use."""

    def test_core_pattern_with_typed_overrides(self):
        """
        Demonstrate how CORE can use typed overrides.
        
        CORE workflow:
        1. Get config from env/settings
        2. Build SimplePipelineConfig
        3. Build typed PipelineOverrides
        4. Pass to upstream create_pipeline
        """
        from market_data_pipeline import SimplePipelineConfig, SimplePipelineConfigBuilder
        from market_data_pipeline.pipeline_builder import create_pipeline as upstream_create
        
        # CORE builds its config
        config = SimplePipelineConfig(
            tenant_id='production',
            pipeline_id='equity_bars',
            symbols=['AAPL', 'MSFT', 'GOOGL'],
            batch_size=1000,
            database_url='postgresql://localhost:5432/market_data',
        )
        
        # CORE builds typed overrides
        builder = SimplePipelineConfigBuilder()
        typed_overrides = builder.build(config)
        
        # Verify it's typed
        assert isinstance(typed_overrides, PipelineOverrides)
        assert isinstance(typed_overrides.database_settings, DatabaseSinkSettings)
        
        # CORE passes typed overrides to upstream
        pipeline = upstream_create(
            tenant_id=config.tenant_id,
            pipeline_id=config.pipeline_id,
            source=config.source,
            symbols=config.symbols,
            operator=config.operator,
            sink=config.sink,
            duration_sec=config.duration_sec,
            overrides=typed_overrides,  # Typed! No dict conversion needed
        )
        
        assert pipeline is not None
        assert pipeline.ctx.tenant_id == 'production'

    def test_core_pattern_simplified(self):
        """
        Demonstrate the simplified CORE pattern using high-level API.
        
        This is even simpler - CORE just uses the high-level create_pipeline.
        """
        from market_data_pipeline import create_pipeline
        
        # CORE just calls create_pipeline with its config
        pipeline = create_pipeline(
            tenant_id='production',
            pipeline_id='equity_bars_simple',
            symbols=['AAPL', 'MSFT'],
            source='synthetic',
            sink='database',
            batch_size=1000,
            database_url='postgresql://localhost:5432/market_data',
        )
        
        assert pipeline is not None
        assert pipeline.ctx.tenant_id == 'production'

