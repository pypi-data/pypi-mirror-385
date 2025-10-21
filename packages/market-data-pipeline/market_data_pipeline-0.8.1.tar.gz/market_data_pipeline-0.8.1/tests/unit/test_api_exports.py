"""
Unit tests for API exports and structure.

This test validates that the public API is correctly exposed from the
market_data_pipeline package for consumption by market_data_core.
"""

import pytest


class TestAPIExports:
    """Test that all expected API exports are available."""

    def test_high_level_api_imports(self):
        """Test that high-level API functions can be imported."""
        from market_data_pipeline import create_pipeline, create_explicit_pipeline
        
        assert callable(create_pipeline)
        assert callable(create_explicit_pipeline)

    def test_factory_imports(self):
        """Test that factory classes and instances can be imported."""
        from market_data_pipeline import (
            SimplePipelineFactory,
            ExplicitPipelineFactory,
            simple_factory,
            explicit_factory,
        )
        
        assert SimplePipelineFactory is not None
        assert ExplicitPipelineFactory is not None
        assert simple_factory is not None
        assert explicit_factory is not None

    def test_config_type_imports(self):
        """Test that config types can be imported."""
        from market_data_pipeline import (
            SimplePipelineConfig,
            ExplicitPipelineConfig,
            DropPolicy,
            BackpressurePolicy,
        )
        
        assert SimplePipelineConfig is not None
        assert ExplicitPipelineConfig is not None
        assert DropPolicy is not None
        assert BackpressurePolicy is not None

    def test_validator_builder_imports(self):
        """Test that validators and builders can be imported."""
        from market_data_pipeline import (
            SimplePipelineValidator,
            ExplicitPipelineValidator,
            SimplePipelineConfigBuilder,
            ExplicitPipelineConfigBuilder,
        )
        
        assert SimplePipelineValidator is not None
        assert ExplicitPipelineValidator is not None
        assert SimplePipelineConfigBuilder is not None
        assert ExplicitPipelineConfigBuilder is not None

    def test_existing_exports(self):
        """Test that existing exports still work."""
        from market_data_pipeline import StreamingPipeline, DatabaseSinkSettings
        
        assert StreamingPipeline is not None
        assert DatabaseSinkSettings is not None

    def test_all_exports_list(self):
        """Test that __all__ contains expected exports."""
        import market_data_pipeline
        
        expected_exports = {
            # High-level API
            "create_pipeline",
            "create_explicit_pipeline",
            # Factories
            "SimplePipelineFactory",
            "ExplicitPipelineFactory",
            "simple_factory",
            "explicit_factory",
            # Types
            "SimplePipelineConfig",
            "ExplicitPipelineConfig",
            "DropPolicy",
            "BackpressurePolicy",
            # Validators/builders
            "SimplePipelineValidator",
            "ExplicitPipelineValidator",
            "SimplePipelineConfigBuilder",
            "ExplicitPipelineConfigBuilder",
            # Existing
            "StreamingPipeline",
            "DatabaseSinkSettings",
        }
        
        actual_exports = set(market_data_pipeline.__all__)
        
        # Check that all expected exports are present
        assert expected_exports.issubset(actual_exports), \
            f"Missing exports: {expected_exports - actual_exports}"


class TestConfigCreation:
    """Test that config objects can be created correctly."""

    def test_simple_pipeline_config_creation(self):
        """Test SimplePipelineConfig can be created."""
        from market_data_pipeline import SimplePipelineConfig, DropPolicy
        
        config = SimplePipelineConfig(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            symbols=["AAPL", "MSFT"],
            drop_policy=DropPolicy.OLDEST,
        )
        
        assert config.tenant_id == "test_tenant"
        assert config.pipeline_id == "test_pipeline"
        assert config.symbols == ["AAPL", "MSFT"]
        assert config.drop_policy == DropPolicy.OLDEST

    def test_explicit_pipeline_config_creation(self):
        """Test ExplicitPipelineConfig can be created."""
        from market_data_pipeline import ExplicitPipelineConfig, DropPolicy
        
        config = ExplicitPipelineConfig(
            tenant_id="test_tenant",
            pipeline_id="test_explicit",
            symbols=["TSLA"],
            ticks_per_sec=100,
            batch_size=1000,
            drop_policy=DropPolicy.NEWEST,
        )
        
        assert config.tenant_id == "test_tenant"
        assert config.pipeline_id == "test_explicit"
        assert config.symbols == ["TSLA"]
        assert config.ticks_per_sec == 100
        assert config.batch_size == 1000
        assert config.drop_policy == DropPolicy.NEWEST

    def test_drop_policy_enum_values(self):
        """Test DropPolicy enum values."""
        from market_data_pipeline import DropPolicy
        
        assert DropPolicy.OLDEST.value == "oldest"
        assert DropPolicy.NEWEST.value == "newest"
        assert DropPolicy.BLOCK.value == "block"

    def test_backpressure_policy_enum_values(self):
        """Test BackpressurePolicy enum values."""
        from market_data_pipeline import BackpressurePolicy
        
        assert BackpressurePolicy.DROP_OLDEST.value == "drop_oldest"
        assert BackpressurePolicy.DROP_NEWEST.value == "drop_newest"
        assert BackpressurePolicy.BLOCK.value == "block"


class TestValidatorPattern:
    """Test that validators work correctly."""

    def test_simple_validator_success(self):
        """Test SimplePipelineValidator with valid config."""
        from market_data_pipeline import (
            SimplePipelineConfig,
            SimplePipelineValidator,
            DropPolicy,
        )
        
        config = SimplePipelineConfig(
            tenant_id="test",
            pipeline_id="test",
            symbols=["AAPL"],
            drop_policy=DropPolicy.OLDEST,
        )
        
        validator = SimplePipelineValidator()
        # Should not raise
        validator.validate(config)

    def test_simple_validator_empty_symbols(self):
        """Test SimplePipelineValidator fails on empty symbols."""
        from market_data_pipeline import (
            SimplePipelineConfig,
            SimplePipelineValidator,
            DropPolicy,
        )
        
        config = SimplePipelineConfig(
            tenant_id="test",
            pipeline_id="test",
            symbols=[],  # Empty symbols
            drop_policy=DropPolicy.OLDEST,
        )
        
        validator = SimplePipelineValidator()
        with pytest.raises(ValueError, match="symbols list cannot be empty"):
            validator.validate(config)

    def test_explicit_validator_success(self):
        """Test ExplicitPipelineValidator with valid config."""
        from market_data_pipeline import (
            ExplicitPipelineConfig,
            ExplicitPipelineValidator,
            DropPolicy,
        )
        
        config = ExplicitPipelineConfig(
            tenant_id="test",
            pipeline_id="test",
            symbols=["AAPL"],
            drop_policy=DropPolicy.OLDEST,
        )
        
        validator = ExplicitPipelineValidator()
        # Should not raise
        validator.validate(config)


class TestConfigBuilderPattern:
    """Test that config builders work correctly."""

    def test_simple_config_builder(self):
        """Test SimplePipelineConfigBuilder builds overrides."""
        from market_data_pipeline import (
            SimplePipelineConfig,
            SimplePipelineConfigBuilder,
            DropPolicy,
        )
        
        config = SimplePipelineConfig(
            tenant_id="test",
            pipeline_id="test",
            symbols=["AAPL"],
            batch_size=500,
            drop_policy=DropPolicy.OLDEST,
        )
        
        builder = SimplePipelineConfigBuilder()
        overrides = builder.build(config)
        
        assert overrides.batch_size == 500
        assert overrides.drop_policy == "oldest"

    def test_explicit_config_builder(self):
        """Test ExplicitPipelineConfigBuilder builds component configs."""
        from market_data_pipeline import (
            ExplicitPipelineConfig,
            ExplicitPipelineConfigBuilder,
            DropPolicy,
        )
        
        config = ExplicitPipelineConfig(
            tenant_id="test",
            pipeline_id="test",
            symbols=["AAPL"],
            batch_size=1000,
            bar_window_sec=1,
            drop_policy=DropPolicy.OLDEST,
        )
        
        builder = ExplicitPipelineConfigBuilder()
        components = builder.build(config)
        
        assert "context" in components
        assert "source_config" in components
        assert "operator_config" in components
        assert "batcher_config" in components
        assert "sink_config" in components
        
        assert components["batcher_config"]["max_rows"] == 1000
        assert components["operator_config"]["window_sec"] == 1


class TestFactoryPattern:
    """Test that factories work correctly."""

    def test_simple_factory_instance_exists(self):
        """Test that simple_factory instance is available."""
        from market_data_pipeline import simple_factory
        
        assert simple_factory is not None
        assert hasattr(simple_factory, "create")

    def test_explicit_factory_instance_exists(self):
        """Test that explicit_factory instance is available."""
        from market_data_pipeline import explicit_factory
        
        assert explicit_factory is not None
        assert hasattr(explicit_factory, "create")

    def test_simple_factory_class_instantiation(self):
        """Test that SimplePipelineFactory can be instantiated."""
        from market_data_pipeline import SimplePipelineFactory
        
        factory = SimplePipelineFactory()
        assert factory is not None
        assert hasattr(factory, "create")

    def test_explicit_factory_class_instantiation(self):
        """Test that ExplicitPipelineFactory can be instantiated."""
        from market_data_pipeline import ExplicitPipelineFactory
        
        factory = ExplicitPipelineFactory()
        assert factory is not None
        assert hasattr(factory, "create")

