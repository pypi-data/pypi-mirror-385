"""Input validation for pipeline configurations.

This module implements the Single Responsibility Principle by focusing
solely on validation logic, making it easy to test and maintain.
"""

from typing import List
import logging

logger = logging.getLogger(__name__)

from .types import PipelineConfig, SimplePipelineConfig, ExplicitPipelineConfig, PipelineValidator


class BasePipelineValidator:
    """Base validator with common validation logic.
    
    This follows the Single Responsibility Principle by focusing
    only on validation concerns.
    """
    
    def _validate_required_fields(self, config: PipelineConfig) -> None:
        """Validate required fields are present."""
        if not config.tenant_id:
            raise ValueError("tenant_id is required")
        if not config.pipeline_id:
            raise ValueError("pipeline_id is required")
        if not config.symbols:
            raise ValueError("symbols list cannot be empty")
    
    def _validate_symbols(self, symbols: List[str]) -> None:
        """Validate symbols list."""
        if not symbols:
            raise ValueError("symbols list cannot be empty")
        if not all(isinstance(symbol, str) and symbol.strip() for symbol in symbols):
            raise ValueError("all symbols must be non-empty strings")


class SimplePipelineValidator(BasePipelineValidator):
    """Validator for simple pipeline configurations.
    
    This follows the Single Responsibility Principle by focusing
    only on simple pipeline validation.
    """
    
    def validate(self, config: SimplePipelineConfig) -> None:
        """Validate simple pipeline configuration.
        
        Args:
            config: The configuration to validate
            
        Raises:
            ValueError: If the configuration is invalid
        """
        logger.debug(f"Validating simple pipeline config for tenant {config.tenant_id}")
        
        # Validate base fields
        self._validate_required_fields(config)
        self._validate_symbols(config.symbols)
        
        # Validate simple pipeline specific fields
        if config.ticks_per_sec <= 0:
            raise ValueError("ticks_per_sec must be positive")
        if config.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if config.flush_ms <= 0:
            raise ValueError("flush_ms must be positive")
        if config.sink_workers <= 0:
            raise ValueError("sink_workers must be positive")
        if config.sink_queue_max <= 0:
            raise ValueError("sink_queue_max must be positive")
        if config.database_retry_max_attempts < 0:
            raise ValueError("database_retry_max_attempts must be non-negative")
        if config.database_retry_backoff_ms < 0:
            raise ValueError("database_retry_backoff_ms must be non-negative")
        
        logger.debug("Simple pipeline config validation successful")


class ExplicitPipelineValidator(BasePipelineValidator):
    """Validator for explicit pipeline configurations.
    
    This follows the Single Responsibility Principle by focusing
    only on explicit pipeline validation.
    """
    
    def validate(self, config: ExplicitPipelineConfig) -> None:
        """Validate explicit pipeline configuration.
        
        Args:
            config: The configuration to validate
            
        Raises:
            ValueError: If the configuration is invalid
        """
        logger.debug(f"Validating explicit pipeline config for tenant {config.tenant_id}")
        
        # Validate base fields
        self._validate_required_fields(config)
        self._validate_symbols(config.symbols)
        
        # Validate explicit pipeline specific fields
        if config.ticks_per_sec <= 0:
            raise ValueError("ticks_per_sec must be positive")
        if config.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if config.max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        if config.flush_ms <= 0:
            raise ValueError("flush_ms must be positive")
        if config.op_queue_max <= 0:
            raise ValueError("op_queue_max must be positive")
        if config.sink_workers <= 0:
            raise ValueError("sink_workers must be positive")
        if config.sink_queue_max <= 0:
            raise ValueError("sink_queue_max must be positive")
        if config.database_retry_max_attempts < 0:
            raise ValueError("database_retry_max_attempts must be non-negative")
        if config.database_retry_backoff_ms < 0:
            raise ValueError("database_retry_backoff_ms must be non-negative")
        if config.bar_window_sec <= 0:
            raise ValueError("bar_window_sec must be positive")
        if config.bar_allowed_lateness_sec < 0:
            raise ValueError("bar_allowed_lateness_sec must be non-negative")
        
        logger.debug("Explicit pipeline config validation successful")
