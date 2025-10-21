# Pipeline Builder Documentation

The `pipeline_builder` module provides a production-grade, centralized way to build and configure market data pipelines. It centralizes all configuration knobs while allowing per-call overrides for maximum flexibility.

## Overview

The pipeline builder supports three main patterns:

1. **Convenience Function**: `create_pipeline()` for simple one-off pipelines
2. **Builder Pattern**: `PipelineBuilder` class for complex configurations
3. **Spec Pattern**: `PipelineSpec` and `PipelineOverrides` for structured configuration

## Quick Start

### Basic Usage

```python
from market_data_pipeline import create_pipeline

# Simple synthetic data pipeline
pipeline = create_pipeline(
    tenant_id="demo",
    pipeline_id="synthetic_demo",
    source="synthetic",
    symbols=["AAPL", "MSFT"],
    duration_sec=10.0
)

# Run the pipeline
await pipeline.run()
await pipeline.close()
```

### With Custom Overrides

```python
# High-frequency trading configuration
pipeline = create_pipeline(
    tenant_id="trading",
    pipeline_id="hft_pipeline",
    source="ibkr",
    symbols=["SPY", "QQQ"],
    overrides={
        "ticks_per_sec": 500,
        "pacing_max_per_sec": 2000,
        "batch_size": 1000,
        "sink_workers": 4,
        "bar_allowed_lateness_sec": 1,
    }
)
```

## Configuration

### Pipeline Configuration

The pipeline builder uses a centralized configuration system with the following key settings:

#### Source Configuration
- `ticks_per_sec`: Ticks per second for synthetic/IBKR sources (default: 100)
- `replay_path`: Path to replay file for replay source
- `replay_speed`: Replay speed multiplier (default: 1.0)

#### Pacing Configuration
- `pacing_max_per_sec`: Maximum messages per second (default: 1000)
- `pacing_burst`: Pacing burst capacity (default: 1000)

#### Operator Configuration
- `bar_window_sec`: Bar aggregation window in seconds (default: 1)
- `bar_allowed_lateness_sec`: Allowed lateness for bar aggregation (default: 0)

#### Batcher Configuration
- `batch_size`: Maximum batch size (default: 500)
- `max_bytes`: Maximum batch size in bytes (default: 512,000)
- `flush_ms`: Flush interval in milliseconds (default: 100)
- `op_queue_max`: Maximum operator queue size (default: 8)
- `drop_policy`: Drop policy - "oldest" or "newest" (default: "oldest")

#### Sink Configuration
- `sink_workers`: Number of sink workers (default: 2)
- `sink_queue_max`: Maximum sink queue size (default: 100)
- `kafka_bootstrap_servers`: Kafka bootstrap servers
- `kafka_topic`: Kafka topic name

### Custom Configuration

```python
from market_data_pipeline.config import PipelineSettings

# Create custom configuration
custom_config = PipelineSettings(
    batch_size=2000,
    flush_ms=50,
    sink_workers=8,
    pacing_max_per_sec=5000,
    bar_window_sec=5,
)

# Use with builder
builder = PipelineBuilder(config=custom_config)
```

## Pipeline Types

### Supported Sources

#### Synthetic Source
```python
pipeline = create_pipeline(
    tenant_id="demo",
    pipeline_id="synthetic",
    source="synthetic",
    symbols=["AAPL", "MSFT", "GOOGL"]  # Required
)
```

#### Replay Source
```python
pipeline = create_pipeline(
    tenant_id="demo",
    pipeline_id="replay",
    source="replay",
    overrides={
        "replay_path": "/data/market_replay.parquet"  # Required
    }
)
```

#### IBKR Source (Optional)
```python
pipeline = create_pipeline(
    tenant_id="demo",
    pipeline_id="ibkr",
    source="ibkr",
    symbols=["SPY", "QQQ"]  # Required
)
```

### Supported Operators

#### Bars Operator
```python
pipeline = create_pipeline(
    tenant_id="demo",
    pipeline_id="bars",
    source="synthetic",
    symbols=["AAPL"],
    operator="bars"  # Default
)
```

#### Options Operator
```python
pipeline = create_pipeline(
    tenant_id="demo",
    pipeline_id="options",
    source="synthetic",
    symbols=["SPY"],
    operator="options"
)
```

### Supported Sinks

#### Store Sink
```python
pipeline = create_pipeline(
    tenant_id="demo",
    pipeline_id="store",
    source="synthetic",
    symbols=["AAPL"],
    sink="store"  # Default
)
```

#### Kafka Sink (Optional)
```python
pipeline = create_pipeline(
    tenant_id="demo",
    pipeline_id="kafka",
    source="synthetic",
    symbols=["AAPL"],
    sink="kafka",
    overrides={
        "kafka_bootstrap": "localhost:9092",
        "kafka_topic": "market_data"
    }
)
```

## Advanced Usage

### Builder Pattern

```python
from market_data_pipeline import PipelineBuilder, PipelineSpec, PipelineOverrides

# Create builder with custom config
builder = PipelineBuilder()

# Define pipeline spec
spec = PipelineSpec(
    tenant_id="production",
    pipeline_id="hft_pipeline",
    source="ibkr",
    symbols=["SPY", "QQQ", "IWM"],
    operator="bars",
    sink="store",
    overrides=PipelineOverrides(
        ticks_per_sec=1000,
        pacing_max_per_sec=5000,
        batch_size=2000,
        sink_workers=8,
        bar_allowed_lateness_sec=2,
    )
)

# Build and run
pipeline = builder.build(spec)
await pipeline.run()
```

### Concurrent Pipelines

```python
import asyncio

# Create multiple pipelines
pipelines = [
    create_pipeline(
        tenant_id="tenant1",
        pipeline_id="pipeline1",
        source="synthetic",
        symbols=["AAPL"]
    ),
    create_pipeline(
        tenant_id="tenant2", 
        pipeline_id="pipeline2",
        source="synthetic",
        symbols=["MSFT"]
    )
]

# Run concurrently
tasks = [pipeline.run() for pipeline in pipelines]
await asyncio.gather(*tasks)
```

### Error Handling

```python
try:
    pipeline = create_pipeline(
        tenant_id="demo",
        pipeline_id="test",
        source="ibkr",  # May not be available
        symbols=["AAPL"]
    )
    await pipeline.run()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Pipeline error: {e}")
finally:
    if 'pipeline' in locals():
        await pipeline.close()
```

## Windows Compatibility

The pipeline builder includes automatic Windows event loop handling:

```python
# Automatically handled in build_and_run()
await builder.build_and_run(spec)

# Or manually for custom event loops
from market_data_pipeline.pipeline_builder import ensure_windows_selector_event_loop
ensure_windows_selector_event_loop()
```

## Optional Dependencies

The pipeline builder gracefully handles missing optional dependencies:

- **IBKR Source**: Requires `market_data_pipeline.source.ibkr`
- **Kafka Sink**: Requires `market_data_pipeline.sink.kafka`
- **Store Sink**: Requires `market_data_store.async_client.AsyncBatchProcessor`

Missing dependencies will raise `ConfigurationError` with clear messages.

## Production Considerations

### Scaling Configuration

```python
# High-throughput configuration
overrides = {
    "ticks_per_sec": 1000,
    "pacing_max_per_sec": 10000,
    "pacing_burst": 15000,
    "batch_size": 5000,
    "flush_ms": 25,
    "sink_workers": 16,
    "sink_queue_max": 1000,
    "bar_allowed_lateness_sec": 5,
}
```

### Monitoring and Metrics

```python
# Enable metrics in configuration
config = PipelineSettings(
    enable_metrics=True,
    metrics_port=8080,
    enable_tracing=True
)
```

### Resource Management

```python
# Proper cleanup
try:
    pipeline = create_pipeline(...)
    await pipeline.run()
finally:
    await pipeline.close()
```

## Best Practices

1. **Use appropriate batch sizes** for your data volume
2. **Configure pacing limits** to prevent overwhelming downstream systems
3. **Set lateness windows** based on your latency requirements
4. **Monitor sink queue sizes** to detect backpressure
5. **Use structured logging** for production debugging
6. **Test with realistic data volumes** before production deployment

## Troubleshooting

### Common Issues

1. **"ReplaySource not available"**: Install replay source dependencies
2. **"IBKRSource not available"**: Install IBKR source dependencies  
3. **"KafkaSink not available"**: Install Kafka sink dependencies
4. **"AsyncBatchProcessor not installed"**: Install market_data_store
5. **Windows event loop issues**: Use `ensure_windows_selector_event_loop()`

### Debug Configuration

```python
# Print current configuration
config = get_pipeline_config()
print(f"Batch size: {config.batch_size}")
print(f"Flush interval: {config.flush_ms}ms")
print(f"Sink workers: {config.sink_workers}")
```

### Validation

```python
# Validate configuration before building
try:
    builder = PipelineBuilder()
    spec = PipelineSpec(...)
    pipeline = builder.build(spec)
    print("Pipeline configuration is valid")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```
