"""Pipeline factory implementations.

This module implements the Dependency Inversion Principle by depending
on abstractions (protocols) rather than concrete implementations.
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

from market_data_pipeline.pipeline_builder import create_pipeline as upstream_create_pipeline
from market_data_pipeline.pipeline import StreamingPipeline
from market_data_pipeline.source.synthetic import SyntheticSource
from market_data_pipeline.operator.bars import SecondBarAggregator
from market_data_pipeline.batcher.hybrid import HybridBatcher
from market_data_pipeline.sink.database import DatabaseSink

from .types import (
    PipelineConfig, SimplePipelineConfig, ExplicitPipelineConfig,
    PipelineFactory, PipelineValidator, PipelineConfigBuilder
)
from .validators import SimplePipelineValidator, ExplicitPipelineValidator
from .config_builders import SimplePipelineConfigBuilder, ExplicitPipelineConfigBuilder


class BasePipelineFactory:
    """Base pipeline factory with common functionality.
    
    This follows the Single Responsibility Principle by focusing
    only on pipeline creation concerns.
    """
    
    def __init__(self, validator: PipelineValidator, config_builder: PipelineConfigBuilder):
        """Initialize the factory with its dependencies.
        
        This follows the Dependency Inversion Principle by depending
        on abstractions rather than concrete implementations.
        
        Args:
            validator: The validator to use for configuration validation
            config_builder: The config builder to use for configuration building
        """
        self._validator = validator
        self._config_builder = config_builder
    
    def _validate_config(self, config: PipelineConfig) -> None:
        """Validate the pipeline configuration."""
        self._validator.validate(config)
    
    def _build_config(self, config: PipelineConfig) -> Any:
        """Build the pipeline configuration."""
        return self._config_builder.build(config)


class SimplePipelineFactory(BasePipelineFactory):
    """Factory for creating simple pipelines.
    
    This follows the Single Responsibility Principle by focusing
    only on simple pipeline creation.
    """
    
    def __init__(self):
        """Initialize the simple pipeline factory."""
        super().__init__(
            validator=SimplePipelineValidator(),
            config_builder=SimplePipelineConfigBuilder()
        )
    
    def create(self, config: SimplePipelineConfig) -> StreamingPipeline:
        """Create a simple pipeline from the given configuration.
        
        Args:
            config: The simple pipeline configuration
            
        Returns:
            The created pipeline
        """
        logger.info(f"Creating simple pipeline for tenant {config.tenant_id}")
        
        # Validate configuration
        self._validate_config(config)
        
        # Build configuration
        overrides = self._build_config(config)
        
        # Create pipeline using upstream factory
        pipeline = upstream_create_pipeline(
            tenant_id=config.tenant_id,
            pipeline_id=config.pipeline_id,
            source=config.source,
            symbols=config.symbols,
            duration_sec=config.duration_sec,
            operator=config.operator,
            sink=config.sink,
            overrides=overrides
        )
        
        logger.info(f"Simple pipeline created successfully for {len(config.symbols)} symbols")
        return pipeline


class ExplicitPipelineFactory(BasePipelineFactory):
    """Factory for creating explicit pipelines.
    
    This follows the Single Responsibility Principle by focusing
    only on explicit pipeline creation.
    """
    
    def __init__(self):
        """Initialize the explicit pipeline factory."""
        super().__init__(
            validator=ExplicitPipelineValidator(),
            config_builder=ExplicitPipelineConfigBuilder()
        )
    
    def create(self, config: ExplicitPipelineConfig) -> StreamingPipeline:
        """Create an explicit pipeline from the given configuration.
        
        Args:
            config: The explicit pipeline configuration
            
        Returns:
            The created pipeline
        """
        logger.info(f"Creating explicit pipeline for tenant {config.tenant_id}")
        
        # Validate configuration
        self._validate_config(config)
        
        # Build configuration
        component_configs = self._build_config(config)
        
        # Create components
        source = SyntheticSource(
            symbols=component_configs['source_config']['symbols'],
            ticks_per_sec=component_configs['source_config']['ticks_per_sec'],
            pacing_budget=component_configs['source_config']['pacing_budget'],
            ctx=component_configs['context']
        )
        
        operator = SecondBarAggregator(
            window_sec=component_configs['operator_config']['window_sec'],
            allowed_lateness_sec=component_configs['operator_config']['allowed_lateness_sec']
        )
        
        batcher = HybridBatcher(**component_configs['batcher_config'])
        
        sink = DatabaseSink(
            tenant_id=component_configs['sink_config']['tenant_id'],
            settings=component_configs['sink_config']['settings'],
            ctx=component_configs['context'],
            database_url=component_configs['sink_config']['database_url']
        )
        
        # Create pipeline
        from market_data_pipeline.pipeline import StreamingPipeline
        pipeline = StreamingPipeline(
            source=source,
            operator=operator,
            batcher=batcher,
            sink=sink,
            ctx=component_configs['context']
        )
        
        logger.info(f"Explicit pipeline created successfully for {len(config.symbols)} symbols")
        return pipeline


# Convenience factory instances
simple_factory = SimplePipelineFactory()
explicit_factory = ExplicitPipelineFactory()
