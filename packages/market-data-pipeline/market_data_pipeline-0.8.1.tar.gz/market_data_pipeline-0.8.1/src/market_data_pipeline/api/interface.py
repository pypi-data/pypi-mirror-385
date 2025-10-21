"""Unified interface for pipeline creation.

This module provides a clean, consolidated interface that follows
SOLID principles and eliminates the need for multiple wrapper functions.
"""

from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

from .types import SimplePipelineConfig, ExplicitPipelineConfig, DropPolicy
from .factory import simple_factory, explicit_factory


def create_pipeline(
    tenant_id: str,
    pipeline_id: str,
    *,
    symbols: Optional[List[str]] = None,
    # Simple pipeline parameters
    source: str = "synthetic",
    operator: str = "bars", 
    sink: str = "database",
    duration_sec: Optional[float] = None,
    ticks_per_sec: int = 10,
    batch_size: int = 500,
    flush_ms: int = 1000,
    pacing_budget: Tuple[int, int] = (1000, 1000),
    drop_policy: str = "oldest",
    sink_workers: int = 2,
    sink_queue_max: int = 200,
    database_vendor: str = "market_data_core",
    database_timeframe: str = "1s",
    database_retry_max_attempts: int = 5,
    database_retry_backoff_ms: int = 50,
    database_url: Optional[str] = None,
    **kwargs
):
    """Create a pipeline using the simple pattern (recommended).
    
    This is the main entry point for pipeline creation. It uses the
    simple pattern by default, which is suitable for most use cases.
    
    Args:
        tenant_id: Tenant identifier for multi-tenant support
        pipeline_id: Unique pipeline identifier
        symbols: List of symbols to process (defaults to common stocks)
        source: Source type ('synthetic', 'replay', 'ibkr')
        operator: Operator type ('bars', 'options')
        sink: Sink type ('database', 'kafka', 'store')
        duration_sec: Optional duration limit for the pipeline
        ticks_per_sec: Number of ticks per second (for synthetic source)
        batch_size: Maximum batch size for batching
        flush_ms: Flush interval in milliseconds
        pacing_budget: Pacing budget for rate limiting (burst, refill)
        drop_policy: Policy for handling backpressure ('oldest', 'newest', 'block')
        sink_workers: Number of sink workers
        sink_queue_max: Maximum sink queue size
        database_vendor: Database vendor identifier
        database_timeframe: Database timeframe setting
        database_retry_max_attempts: Maximum retry attempts for database operations
        database_retry_backoff_ms: Backoff delay between retries
        database_url: Database connection URL
        **kwargs: Additional parameters passed to create_pipeline
        
    Returns:
        Configured StreamingPipeline instance
    """
    # Set default symbols if not provided
    if not symbols:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    
    # Create configuration
    config = SimplePipelineConfig(
        tenant_id=tenant_id,
        pipeline_id=pipeline_id,
        symbols=symbols,
        source=source,
        operator=operator,
        sink=sink,
        duration_sec=duration_sec,
        ticks_per_sec=ticks_per_sec,
        batch_size=batch_size,
        flush_ms=flush_ms,
        pacing_budget=pacing_budget,
        drop_policy=DropPolicy(drop_policy),
        sink_workers=sink_workers,
        sink_queue_max=sink_queue_max,
        database_vendor=database_vendor,
        database_timeframe=database_timeframe,
        database_retry_max_attempts=database_retry_max_attempts,
        database_retry_backoff_ms=database_retry_backoff_ms,
        database_url=database_url
    )
    
    # Create pipeline using factory
    return simple_factory.create(config)


def create_explicit_pipeline(
    tenant_id: str,
    pipeline_id: str,
    *,
    symbols: Optional[List[str]] = None,
    ticks_per_sec: int = 10,
    pacing_budget: Tuple[int, int] = (1000, 1000),
    batch_size: int = 500,
    max_bytes: int = 512_000,
    flush_ms: int = 1000,
    op_queue_max: int = 8,
    drop_policy: str = "oldest",
    sink_workers: int = 2,
    sink_queue_max: int = 200,
    database_vendor: str = "market_data_core",
    database_timeframe: str = "1s",
    database_retry_max_attempts: int = 5,
    database_retry_backoff_ms: int = 50,
    database_url: Optional[str] = None,
    bar_window_sec: int = 1,
    bar_allowed_lateness_sec: int = 0
):
    """Create a pipeline using the explicit pattern (advanced control).
    
    This approach gives maximum control over each component and is useful
    when you need fine-grained control over the pipeline configuration.
    
    Args:
        tenant_id: Tenant identifier for multi-tenant support
        pipeline_id: Unique pipeline identifier
        symbols: List of symbols to process (defaults to common stocks)
        ticks_per_sec: Number of ticks per second (for synthetic source)
        pacing_budget: Pacing budget for rate limiting (burst, refill)
        batch_size: Maximum batch size for batching
        max_bytes: Maximum bytes per batch
        flush_ms: Flush interval in milliseconds
        op_queue_max: Maximum operator queue size
        drop_policy: Policy for handling backpressure ('oldest', 'newest', 'block')
        sink_workers: Number of sink workers
        sink_queue_max: Maximum sink queue size
        database_vendor: Database vendor identifier
        database_timeframe: Database timeframe setting
        database_retry_max_attempts: Maximum retry attempts for database operations
        database_retry_backoff_ms: Backoff delay between retries
        database_url: Database connection URL
        bar_window_sec: Bar aggregation window in seconds
        bar_allowed_lateness_sec: Allowed lateness for bar aggregation
        
    Returns:
        Configured StreamingPipeline instance
    """
    # Set default symbols if not provided
    if not symbols:
        symbols = ["AAPL", "MSFT", "GOOGL"]
    
    # Create configuration
    config = ExplicitPipelineConfig(
        tenant_id=tenant_id,
        pipeline_id=pipeline_id,
        symbols=symbols,
        ticks_per_sec=ticks_per_sec,
        pacing_budget=pacing_budget,
        batch_size=batch_size,
        max_bytes=max_bytes,
        flush_ms=flush_ms,
        op_queue_max=op_queue_max,
        drop_policy=DropPolicy(drop_policy),
        sink_workers=sink_workers,
        sink_queue_max=sink_queue_max,
        database_vendor=database_vendor,
        database_timeframe=database_timeframe,
        database_retry_max_attempts=database_retry_max_attempts,
        database_retry_backoff_ms=database_retry_backoff_ms,
        database_url=database_url,
        bar_window_sec=bar_window_sec,
        bar_allowed_lateness_sec=bar_allowed_lateness_sec
    )
    
    # Create pipeline using factory
    return explicit_factory.create(config)
