"""Type definitions for pipeline configuration.

This module defines the data structures used throughout the pipeline system,
following the Interface Segregation Principle by providing focused, minimal interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Protocol
from enum import Enum

from market_data_pipeline.pipeline import StreamingPipeline
from market_data_pipeline.pipeline_builder import PipelineOverrides
from market_data_pipeline.sink.database import DatabaseSinkSettings


class DropPolicy(Enum):
    """Enumeration of supported drop policies."""
    OLDEST = "oldest"
    NEWEST = "newest"
    BLOCK = "block"


class BackpressurePolicy(Enum):
    """Enumeration of supported backpressure policies."""
    DROP_OLDEST = "drop_oldest"
    DROP_NEWEST = "drop_newest"
    BLOCK = "block"


@dataclass
class PipelineConfig:
    """Base configuration for all pipeline types.
    
    This follows the Interface Segregation Principle by providing
    only the essential configuration needed by all pipeline types.
    """
    tenant_id: str
    pipeline_id: str
    symbols: List[str]
    database_url: Optional[str] = None


@dataclass
class SimplePipelineConfig(PipelineConfig):
    """Configuration for simple pipeline creation.
    
    Extends the base configuration with parameters specific to
    the simple pipeline pattern.
    """
    source: str = "synthetic"
    operator: str = "bars"
    sink: str = "database"
    duration_sec: Optional[float] = None
    ticks_per_sec: int = 10
    batch_size: int = 500
    flush_ms: int = 1000
    pacing_budget: Tuple[int, int] = (1000, 1000)
    drop_policy: DropPolicy = DropPolicy.OLDEST
    sink_workers: int = 2
    sink_queue_max: int = 200
    database_vendor: str = "market_data_core"
    database_timeframe: str = "1s"
    database_retry_max_attempts: int = 5
    database_retry_backoff_ms: int = 50


@dataclass
class ExplicitPipelineConfig(PipelineConfig):
    """Configuration for explicit pipeline creation.
    
    Extends the base configuration with parameters specific to
    the explicit pipeline pattern.
    """
    ticks_per_sec: int = 10
    pacing_budget: Tuple[int, int] = (1000, 1000)
    batch_size: int = 500
    max_bytes: int = 512_000
    flush_ms: int = 1000
    op_queue_max: int = 8
    drop_policy: DropPolicy = DropPolicy.OLDEST
    sink_workers: int = 2
    sink_queue_max: int = 200
    database_vendor: str = "market_data_core"
    database_timeframe: str = "1s"
    database_retry_max_attempts: int = 5
    database_retry_backoff_ms: int = 50
    bar_window_sec: int = 1
    bar_allowed_lateness_sec: int = 0


class PipelineValidator(Protocol):
    """Protocol for pipeline configuration validation.
    
    This follows the Interface Segregation Principle by defining
    a minimal interface for validation.
    """
    
    def validate(self, config: PipelineConfig) -> None:
        """Validate the pipeline configuration.
        
        Args:
            config: The configuration to validate
            
        Raises:
            ValueError: If the configuration is invalid
        """
        ...


class PipelineConfigBuilder(Protocol):
    """Protocol for building pipeline configurations.
    
    This follows the Interface Segregation Principle by defining
    a minimal interface for configuration building.
    """
    
    def build(self, config: PipelineConfig) -> Any:
        """Build the pipeline configuration.
        
        Args:
            config: The base configuration
            
        Returns:
            The built configuration object
        """
        ...


class PipelineFactory(Protocol):
    """Protocol for creating pipelines.
    
    This follows the Interface Segregation Principle by defining
    a minimal interface for pipeline creation.
    """
    
    def create(self, config: PipelineConfig) -> StreamingPipeline:
        """Create a pipeline from the given configuration.
        
        Args:
            config: The pipeline configuration
            
        Returns:
            The created pipeline
        """
        ...
