"""Configuration builders for pipeline creation.

This module implements the Open/Closed Principle by providing a base
configuration builder that can be extended for new pipeline types
without modifying existing code.
"""

import os
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

from market_data_pipeline.pipeline_builder import PipelineOverrides
from market_data_pipeline.sink.database import DatabaseSinkSettings
from market_data_pipeline.source.synthetic import SyntheticSource
from market_data_pipeline.operator.bars import SecondBarAggregator
from market_data_pipeline.batcher.hybrid import HybridBatcher
from market_data_pipeline.sink.database import DatabaseSink
from market_data_pipeline.context import PipelineContext

from .types import (
    PipelineConfig, SimplePipelineConfig, ExplicitPipelineConfig,
    PipelineConfigBuilder, DropPolicy, BackpressurePolicy
)


class BaseConfigBuilder:
    """Base configuration builder with common functionality.
    
    This follows the Single Responsibility Principle by focusing
    only on configuration building concerns.
    """
    
    def _get_database_url(self, config: PipelineConfig) -> str:
        """Get database URL from config or environment."""
        if config.database_url:
            return config.database_url
        return os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/market_data")
    
    def _map_drop_policy_to_backpressure(self, drop_policy: DropPolicy) -> BackpressurePolicy:
        """Map drop policy to backpressure policy."""
        mapping = {
            DropPolicy.OLDEST: BackpressurePolicy.DROP_OLDEST,
            DropPolicy.NEWEST: BackpressurePolicy.DROP_NEWEST,
            DropPolicy.BLOCK: BackpressurePolicy.BLOCK
        }
        return mapping[drop_policy]


class SimplePipelineConfigBuilder(BaseConfigBuilder):
    """Configuration builder for simple pipelines.
    
    This follows the Single Responsibility Principle by focusing
    only on simple pipeline configuration building.
    """
    
    def build(self, config: SimplePipelineConfig) -> PipelineOverrides:
        """Build PipelineOverrides for simple pipeline.
        
        Args:
            config: The simple pipeline configuration
            
        Returns:
            Configured PipelineOverrides object
        """
        logger.debug(f"Building simple pipeline config for {len(config.symbols)} symbols")
        
        database_url = self._get_database_url(config)
        backpressure_policy = self._map_drop_policy_to_backpressure(config.drop_policy)
        
        return PipelineOverrides(
            ticks_per_sec=config.ticks_per_sec,
            pacing_max_per_sec=config.pacing_budget[1],
            pacing_burst=config.pacing_budget[0],
            batch_size=config.batch_size,
            flush_ms=config.flush_ms,
            drop_policy=config.drop_policy.value,
            sink_workers=config.sink_workers,
            sink_queue_max=config.sink_queue_max,
            database_vendor=config.database_vendor,
            database_timeframe=config.database_timeframe,
            database_retry_max_attempts=config.database_retry_max_attempts,
            database_retry_backoff_ms=config.database_retry_backoff_ms,
            database_url=database_url,
            database_settings=DatabaseSinkSettings(
                vendor=config.database_vendor,
                timeframe=config.database_timeframe,
                workers=config.sink_workers,
                queue_max=config.sink_queue_max,
                backpressure_policy=backpressure_policy.value,
                retry_max_attempts=config.database_retry_max_attempts,
                retry_backoff_ms=config.database_retry_backoff_ms,
            )
        )


class ExplicitPipelineConfigBuilder(BaseConfigBuilder):
    """Configuration builder for explicit pipelines.
    
    This follows the Single Responsibility Principle by focusing
    only on explicit pipeline configuration building.
    """
    
    def build(self, config: ExplicitPipelineConfig) -> Dict[str, Any]:
        """Build component configuration for explicit pipeline.
        
        Args:
            config: The explicit pipeline configuration
            
        Returns:
            Dictionary containing all component configurations
        """
        logger.debug(f"Building explicit pipeline config for {len(config.symbols)} symbols")
        
        database_url = self._get_database_url(config)
        backpressure_policy = self._map_drop_policy_to_backpressure(config.drop_policy)
        
        return {
            'context': PipelineContext(tenant_id=config.tenant_id, pipeline_id=config.pipeline_id),
            'source_config': {
                'symbols': config.symbols,
                'ticks_per_sec': config.ticks_per_sec,
                'pacing_budget': config.pacing_budget,
            },
            'operator_config': {
                'window_sec': config.bar_window_sec,
                'allowed_lateness_sec': config.bar_allowed_lateness_sec,
            },
            'batcher_config': {
                'max_rows': config.batch_size,
                'max_bytes': config.max_bytes,
                'flush_ms': config.flush_ms,
                'op_queue_max': config.op_queue_max,
                'drop_policy': config.drop_policy.value,
            },
            'sink_config': {
                'tenant_id': config.tenant_id,
                'settings': DatabaseSinkSettings(
                    vendor=config.database_vendor,
                    timeframe=config.database_timeframe,
                    workers=config.sink_workers,
                    queue_max=config.sink_queue_max,
                    backpressure_policy=backpressure_policy.value,
                    retry_max_attempts=config.database_retry_max_attempts,
                    retry_backoff_ms=config.database_retry_backoff_ms,
                ),
                'database_url': database_url,
            }
        }
