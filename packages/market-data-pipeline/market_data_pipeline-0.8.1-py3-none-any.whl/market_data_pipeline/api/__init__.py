"""High-level API for market data pipeline creation.

This module provides a clean, consolidated interface that follows
SOLID principles and eliminates the need for multiple wrapper functions.
"""

# High-level API
from .interface import create_pipeline, create_explicit_pipeline

# Factories (if you want direct factory access)
from .factory import SimplePipelineFactory, ExplicitPipelineFactory, simple_factory, explicit_factory

# Config types
from .types import (
    SimplePipelineConfig,
    ExplicitPipelineConfig,
    DropPolicy,
    BackpressurePolicy,
)

# Validators & builders (optional public access)
from .validators import SimplePipelineValidator, ExplicitPipelineValidator
from .config_builders import SimplePipelineConfigBuilder, ExplicitPipelineConfigBuilder

__all__ = [
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
]
