# Typed Overrides Guide

## Overview

The `pipeline_builder.create_pipeline()` function now accepts **typed `PipelineOverrides`** in addition to dicts, making the API more type-safe and eliminating the need for conversion wrappers.

## Changes Made

### pipeline_builder.py

```python
# Before (dict only)
def create_pipeline(..., overrides: Optional[Dict[str, Any]] = None):
    spec = PipelineSpec(..., overrides=PipelineOverrides(**(overrides or {})))

# After (dict or typed)
def create_pipeline(..., 
    overrides: Optional[Union[Dict[str, Any], PipelineOverrides]] = None
):
    ov = overrides if isinstance(overrides, PipelineOverrides) else PipelineOverrides(**(overrides or {}))
    spec = PipelineSpec(..., overrides=ov)
```

### Benefits

1. **Type Safety**: Pass dataclasses instead of dicts
2. **No Conversion**: Direct passing of `PipelineOverrides` 
3. **Better IDE Support**: Autocomplete and type checking
4. **Cleaner Code**: No wrapper functions needed
5. **Backward Compatible**: Dict overrides still work

## Usage Patterns

### Pattern 1: Dict Overrides (Backward Compatible)

```python
from market_data_pipeline.pipeline_builder import create_pipeline

pipeline = create_pipeline(
    tenant_id='test',
    pipeline_id='test',
    source='synthetic',
    symbols=['AAPL'],
    sink='database',
    overrides={
        'batch_size': 1000,
        'flush_ms': 500,
        'database_url': 'postgresql://localhost:5432/db',
    }
)
```

### Pattern 2: Typed PipelineOverrides (New)

```python
from market_data_pipeline.pipeline_builder import create_pipeline, PipelineOverrides

overrides = PipelineOverrides(
    batch_size=2000,
    flush_ms=1000,
    ticks_per_sec=100,
    database_url='postgresql://localhost:5432/db',
)

pipeline = create_pipeline(
    tenant_id='test',
    pipeline_id='test',
    source='synthetic',
    symbols=['MSFT'],
    sink='database',
    overrides=overrides,  # Pass dataclass directly!
)
```

### Pattern 3: With DatabaseSinkSettings (Advanced)

```python
from market_data_pipeline.pipeline_builder import create_pipeline, PipelineOverrides
from market_data_pipeline.sink.database import DatabaseSinkSettings

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
    database_url='postgresql://localhost:5432/db',
    database_settings=db_settings,  # Pass typed settings!
)

pipeline = create_pipeline(
    tenant_id='test',
    pipeline_id='test',
    source='synthetic',
    symbols=['GOOGL'],
    sink='database',
    overrides=overrides,
)
```

## market_data_core Integration

### The Flow

```
CORE Config
    ↓
SimplePipelineConfig (API config)
    ↓
SimplePipelineConfigBuilder.build()
    ↓
PipelineOverrides (typed!)
    ↓
upstream create_pipeline() (accepts typed directly!)
    ↓
StreamingPipeline
```

### Implementation in CORE

```python
from market_data_pipeline import SimplePipelineConfig, SimplePipelineConfigBuilder
from market_data_pipeline.pipeline_builder import create_pipeline as upstream_create

# 1. CORE builds its config from env/settings
config = SimplePipelineConfig(
    tenant_id='production',
    pipeline_id='equity_bars',
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    batch_size=1000,
    database_url='postgresql://localhost:5432/market_data',
)

# 2. CORE builds typed overrides
builder = SimplePipelineConfigBuilder()
typed_overrides = builder.build(config)  # Returns PipelineOverrides!

# 3. CORE passes typed overrides to upstream
pipeline = upstream_create(
    tenant_id=config.tenant_id,
    pipeline_id=config.pipeline_id,
    source=config.source,
    symbols=config.symbols,
    operator=config.operator,
    sink=config.sink,
    overrides=typed_overrides,  # No dict conversion needed!
)
```

### Simplified Pattern (Recommended for CORE)

```python
from market_data_pipeline import create_pipeline

# CORE just calls the high-level API
pipeline = create_pipeline(
    tenant_id='production',
    pipeline_id='equity_bars',
    symbols=['AAPL', 'MSFT'],
    source='synthetic',
    sink='database',
    batch_size=1000,
    database_url='postgresql://localhost:5432/market_data',
)
```

## API Factory Integration

Our API factories already produce and use typed overrides:

```python
# SimplePipelineConfigBuilder returns PipelineOverrides
class SimplePipelineConfigBuilder:
    def build(self, config: SimplePipelineConfig) -> PipelineOverrides:
        return PipelineOverrides(
            batch_size=config.batch_size,
            database_settings=DatabaseSinkSettings(...),
            # ... all typed!
        )

# SimplePipelineFactory passes it directly
class SimplePipelineFactory:
    def create(self, config: SimplePipelineConfig) -> StreamingPipeline:
        overrides = self._config_builder.build(config)  # PipelineOverrides
        return upstream_create_pipeline(
            ...,
            overrides=overrides  # Accepts typed directly!
        )
```

## Type Hierarchy

```
PipelineOverrides (dataclass)
├── Source settings
│   ├── ticks_per_sec
│   ├── pacing_max_per_sec
│   ├── pacing_burst
│   └── replay_*
├── Operator settings
│   ├── bar_window_sec
│   └── bar_allowed_lateness_sec
├── Batcher settings
│   ├── batch_size
│   ├── max_bytes
│   ├── flush_ms
│   ├── op_queue_max
│   └── drop_policy
└── Sink settings
    ├── sink_workers
    ├── sink_queue_max
    ├── kafka_*
    ├── database_*
    ├── database_settings (DatabaseSinkSettings)
    └── database_processor

DatabaseSinkSettings (dataclass)
├── vendor
├── timeframe
├── workers
├── queue_max
├── backpressure_policy
├── retry_max_attempts
└── retry_backoff_ms
```

## Testing

All tests verify both patterns work:

```bash
# Run typed overrides tests
pytest tests/unit/test_typed_overrides_integration.py -v

# Run all tests
pytest tests/unit/ -v
```

Current test results: **93 tests pass** ✅

## Migration Guide

### For Existing Code

No migration needed! Dict overrides still work:

```python
# This still works
pipeline = create_pipeline(..., overrides={'batch_size': 1000})
```

### For New Code

Use typed overrides for better type safety:

```python
# Better: Use typed overrides
overrides = PipelineOverrides(batch_size=1000)
pipeline = create_pipeline(..., overrides=overrides)
```

### For CORE Integration

Use the config builders:

```python
# Best: Use config builders
config = SimplePipelineConfig(...)
builder = SimplePipelineConfigBuilder()
typed_overrides = builder.build(config)
pipeline = upstream_create(..., overrides=typed_overrides)
```

## Benefits for CORE

1. **Type Safety**: No more dict conversion, everything is typed
2. **IDE Support**: Full autocomplete and type checking
3. **Validation**: Dataclass validation at creation time
4. **Cleaner**: No need for wrapper functions or dict unpacking
5. **Maintainable**: Changes to PipelineOverrides are caught at compile time

## Summary

✅ `create_pipeline()` accepts `Union[Dict, PipelineOverrides]`  
✅ API factories produce typed `PipelineOverrides`  
✅ `DatabaseSinkSettings` can be passed via `overrides.database_settings`  
✅ Backward compatible with dict overrides  
✅ All 93 tests pass  
✅ Ready for market_data_core integration  

The API is now fully type-safe while maintaining backward compatibility.

