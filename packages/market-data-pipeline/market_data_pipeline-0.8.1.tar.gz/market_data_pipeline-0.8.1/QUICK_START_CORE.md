# Quick Start Guide for market_data_core

## Installation

```bash
pip install market-data-pipeline
```

## Basic Usage

```python
from market_data_pipeline import create_pipeline, SimplePipelineConfig, DropPolicy

# Option 1: Direct function call (recommended)
pipeline = create_pipeline(
    tenant_id='my_tenant',
    pipeline_id='my_pipeline',
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    database_url='postgresql://localhost:5432/market_data'
)

# Option 2: Using config object
config = SimplePipelineConfig(
    tenant_id='my_tenant',
    pipeline_id='my_pipeline',
    symbols=['AAPL', 'MSFT'],
    drop_policy=DropPolicy.OLDEST,
    ticks_per_sec=100,
    batch_size=1000,
    database_url='postgresql://localhost:5432/market_data'
)

from market_data_pipeline import simple_factory
pipeline = simple_factory.create(config)

# Option 3: Using typed overrides (advanced)
from market_data_pipeline.pipeline_builder import create_pipeline, PipelineOverrides

overrides = PipelineOverrides(
    batch_size=1000,
    flush_ms=500,
    database_url='postgresql://localhost:5432/market_data'
)

pipeline = create_pipeline(
    tenant_id='my_tenant',
    pipeline_id='my_pipeline',
    source='synthetic',
    symbols=['AAPL', 'MSFT'],
    sink='database',
    overrides=overrides  # Pass typed overrides directly!
)
```

## Configuration Options

### SimplePipelineConfig

```python
SimplePipelineConfig(
    # Required
    tenant_id='my_tenant',
    pipeline_id='my_pipeline',
    symbols=['AAPL', 'MSFT'],
    
    # Optional (with defaults)
    source='synthetic',              # 'synthetic', 'replay', 'ibkr'
    operator='bars',                 # 'bars', 'options'
    sink='database',                 # 'database', 'kafka', 'store'
    duration_sec=None,               # None = run forever
    ticks_per_sec=10,
    batch_size=500,
    flush_ms=1000,
    pacing_budget=(1000, 1000),      # (burst, refill)
    drop_policy=DropPolicy.OLDEST,   # OLDEST, NEWEST, BLOCK
    sink_workers=2,
    sink_queue_max=200,
    database_vendor='market_data_core',
    database_timeframe='1s',
    database_retry_max_attempts=5,
    database_retry_backoff_ms=50,
    database_url=None,               # Falls back to env var
)
```

### ExplicitPipelineConfig

```python
from market_data_pipeline import create_explicit_pipeline, ExplicitPipelineConfig

config = ExplicitPipelineConfig(
    # Required
    tenant_id='my_tenant',
    pipeline_id='hft_pipeline',
    symbols=['AAPL'],
    
    # Optional (with defaults)
    ticks_per_sec=10,
    pacing_budget=(1000, 1000),
    batch_size=500,
    max_bytes=512_000,
    flush_ms=1000,
    op_queue_max=8,
    drop_policy=DropPolicy.OLDEST,
    sink_workers=2,
    sink_queue_max=200,
    database_vendor='market_data_core',
    database_timeframe='1s',
    database_retry_max_attempts=5,
    database_retry_backoff_ms=50,
    bar_window_sec=1,
    bar_allowed_lateness_sec=0,
    database_url=None,
)

pipeline = create_explicit_pipeline(**config.__dict__)
```

## Drop Policies

```python
from market_data_pipeline import DropPolicy

DropPolicy.OLDEST  # Drop oldest data when queue is full
DropPolicy.NEWEST  # Drop newest data when queue is full
DropPolicy.BLOCK   # Block producer when queue is full
```

## Running the Pipeline

```python
# Start the pipeline (async)
await pipeline.run()

# Or use the runner utilities
from market_data_pipeline.runners import run_pipeline_async

await run_pipeline_async(pipeline)
```

## Example for Production

```python
import os
from market_data_pipeline import create_pipeline, DropPolicy

# Get config from environment/settings
pipeline = create_pipeline(
    tenant_id=os.getenv('TENANT_ID'),
    pipeline_id=os.getenv('PIPELINE_ID'),
    symbols=os.getenv('SYMBOLS', 'AAPL,MSFT,GOOGL').split(','),
    ticks_per_sec=int(os.getenv('TICKS_PER_SEC', '100')),
    batch_size=int(os.getenv('BATCH_SIZE', '1000')),
    drop_policy=os.getenv('DROP_POLICY', 'oldest'),
    database_url=os.getenv('DATABASE_URL'),
)

# Run it
import asyncio
asyncio.run(pipeline.run())
```

## Testing

```python
# For testing, use in-memory database
test_pipeline = create_pipeline(
    tenant_id='test',
    pipeline_id='test',
    symbols=['AAPL'],
    duration_sec=5.0,  # Run for 5 seconds
    database_url='sqlite:///:memory:'
)
```

## Available Exports

All imports from single package:

```python
from market_data_pipeline import (
    # High-level API
    create_pipeline,
    create_explicit_pipeline,
    
    # Factories
    SimplePipelineFactory,
    ExplicitPipelineFactory,
    simple_factory,
    explicit_factory,
    
    # Config types
    SimplePipelineConfig,
    ExplicitPipelineConfig,
    DropPolicy,
    BackpressurePolicy,
    
    # Validators & builders (optional)
    SimplePipelineValidator,
    ExplicitPipelineValidator,
    SimplePipelineConfigBuilder,
    ExplicitPipelineConfigBuilder,
    
    # Core types
    StreamingPipeline,
    DatabaseSinkSettings,
)
```

## Support

For issues or questions, refer to the main documentation or the API_VERIFICATION_SUMMARY.md file.

