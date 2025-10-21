"""Market Data Pipeline - Orchestration layer for market data processing."""

__version__ = "0.9.0"  # Phase 8.0 - Core v1.1.0 Integration

# Core pipeline components
from .pipeline import StreamingPipeline
from .context import PipelineContext
from .config import get_pipeline_config, PipelineSettings

# Pipeline builder
from .pipeline_builder import (
    PipelineBuilder,
    PipelineSpec,
    PipelineOverrides,
    create_pipeline as upstream_create_pipeline,
    ensure_windows_selector_event_loop,
)

# Database sink settings
from .sink.database import DatabaseSinkSettings

# High-level API
from .api.interface import create_pipeline, create_explicit_pipeline

# Factories (if you want direct factory access)
from .api.factory import SimplePipelineFactory, ExplicitPipelineFactory, simple_factory, explicit_factory

# Config types
from .api.types import (
    SimplePipelineConfig,
    ExplicitPipelineConfig,
    DropPolicy,
    BackpressurePolicy,
)

# Validators & builders (optional public access)
from .api.validators import SimplePipelineValidator, ExplicitPipelineValidator
from .api.config_builders import SimplePipelineConfigBuilder, ExplicitPipelineConfigBuilder

# Error types
from .errors import (
    PipelineError,
    ConfigurationError,
    SourceError,
    OperatorError,
    BatcherError,
    SinkError,
    PacingError,
)

# Orchestration layer (Phase 3.0) - Opt-in
# These are available but not included in __all__ by default
# Users opt-in by explicitly importing: from market_data_pipeline.orchestration import ...
# This maintains backward compatibility while providing new orchestration features

__all__ = [
    # Core
    "StreamingPipeline",
    "PipelineContext",
    "get_pipeline_config",
    "PipelineSettings",
    
    # Builder
    "PipelineBuilder",
    "PipelineSpec", 
    "PipelineOverrides",
    "upstream_create_pipeline",
    "ensure_windows_selector_event_loop",
    
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
    
    # Validators & builders
    "SimplePipelineValidator",
    "ExplicitPipelineValidator",
    "SimplePipelineConfigBuilder",
    "ExplicitPipelineConfigBuilder",
    
    # Database
    "DatabaseSinkSettings",
    
    # Errors
    "PipelineError",
    "ConfigurationError",
    "SourceError",
    "OperatorError",
    "BatcherError",
    "SinkError",
    "PacingError",
]
