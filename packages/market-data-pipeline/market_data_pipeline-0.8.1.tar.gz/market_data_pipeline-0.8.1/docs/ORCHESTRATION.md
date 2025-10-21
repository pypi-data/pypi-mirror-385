# Phase 3.0 - Runtime Orchestration Layer

## Overview

The orchestration layer provides advanced runtime coordination across multiple market data sources and pipelines. It includes:

- **SourceRegistry**: Dynamic discovery and loading of data sources
- **SourceRouter**: Automatic routing with fallback between multiple sources
- **RateCoordinator**: Global rate limiting across all pipelines
- **CircuitBreaker**: Protection against repeated provider failures
- **PipelineRuntime**: Unified orchestration API

## Design Principles

### Opt-In Architecture

The orchestration layer is **completely opt-in**. Existing code continues to work without changes:

```python
# Existing API (still works!)
from market_data_pipeline import create_pipeline

pipeline = create_pipeline(
    tenant_id='my_tenant',
    pipeline_id='my_pipeline',
    source='synthetic',
    symbols=['AAPL']
)
```

To use orchestration, explicitly import from the `orchestration` module:

```python
# New orchestration API (opt-in)
from market_data_pipeline.orchestration import PipelineRuntime

async with PipelineRuntime() as runtime:
    async for quote in runtime.stream_quotes(['AAPL']):
        process(quote)
```

### Backward Compatibility

- ✅ All existing tests pass (93 tests)
- ✅ No breaking changes to existing APIs
- ✅ Orchestration components are separate module
- ✅ Can use new features incrementally

---

## Components

### 1. SourceRegistry

Dynamically registers and loads TickSource implementations.

**Features:**
- Static registration of sources
- Dynamic loading via `importlib`
- Entrypoint discovery for external providers

**Usage:**

```python
from market_data_pipeline.orchestration import SourceRegistry
from market_data_pipeline.source.synthetic import SyntheticSource

registry = SourceRegistry()

# Manual registration
registry.register("synthetic", SyntheticSource)

# Load by name
source_cls = registry.load("synthetic")
source = source_cls(symbols=["AAPL"], ...)

# Discover external providers
registry.discover_entrypoints()
```

**External Provider Registration:**

Providers can register via `pyproject.toml`:

```toml
[project.entry-points."market_data.providers"]
ibkr = "market_data_ibkr:IBKRProvider"
polygon = "market_data_polygon:PolygonProvider"
```

---

### 2. SourceRouter

Meta-source that routes between multiple sources with automatic fallback.

**Features:**
- Implements `TickSource` protocol (drop-in replacement)
- Automatic fallback on errors
- Multiple routing strategies (currently: "first")

**Usage:**

```python
from market_data_pipeline.orchestration import SourceRouter

# Create sources
ibkr = IBKRSource(symbols=['AAPL'], ...)
polygon = PolygonSource(symbols=['AAPL'], ...)

# Create router
router = SourceRouter(
    sources=[ibkr, polygon],
    strategy="first"
)

# Use like any source
async for quote in router.stream():
    print(quote)
```

**As Pipeline Source:**

```python
# Router can be used directly in pipelines
pipeline = StreamingPipeline(
    source=router,  # Router is a TickSource!
    operator=operator,
    batcher=batcher,
    sink=sink,
    ctx=ctx
)
```

---

### 3. RateCoordinator

Global rate limiting across all pipelines and providers.

**Features:**
- Token bucket rate limiting (extends existing `Pacer`)
- Circuit breaker integration
- Cooldown management
- Per-provider budgets

**Usage:**

```python
from market_data_pipeline.orchestration import RateCoordinator

coordinator = RateCoordinator()

# Register provider with rate limits
coordinator.register_provider(
    name="ibkr",
    capacity=60,        # Burst capacity
    refill_rate=60,     # Tokens/sec
    cooldown_sec=600,   # 10min cooldown on errors
    breaker_threshold=5,
    breaker_timeout=60.0
)

# Acquire tokens (blocks if not available)
await coordinator.acquire("ibkr")

# Record failures for circuit breaker
await coordinator.record_failure("ibkr")

# Trigger cooldown on pacing errors
await coordinator.trigger_cooldown("ibkr", "market_data")
```

---

### 4. CircuitBreaker

Protects against repeated provider failures.

**Features:**
- Three states: CLOSED, OPEN, HALF_OPEN
- Automatic recovery after timeout
- Manual reset capability

**Usage:**

```python
from market_data_pipeline.orchestration import CircuitBreaker, CircuitBreakerOpen

breaker = CircuitBreaker(
    threshold=5,     # Open after 5 failures
    timeout=60.0     # Stay open for 60 seconds
)

# Check state
if breaker.is_open():
    raise CircuitBreakerOpen("IBKR")

# Record failures
try:
    await ibkr.connect()
except Exception:
    await breaker.record_failure()
    raise

# Record success
await breaker.record_success()

# Manual reset
await breaker.reset()
```

---

### 5. PipelineRuntime

High-level orchestrator that ties everything together.

**Features:**
- Unified API for streaming and pipeline execution
- Automatic source routing
- Global rate coordination
- Circuit breaker protection
- Context manager support

**Usage:**

```python
from market_data_pipeline.orchestration import (
    PipelineRuntime,
    PipelineRuntimeSettings
)

# Configure runtime
settings = PipelineRuntimeSettings(
    orchestration_enabled=True,
    max_concurrent_pipelines=10,
    enable_rate_coordination=True,
    circuit_breaker_threshold=5,
    circuit_breaker_timeout_sec=60.0,
)

# Use as context manager
async with PipelineRuntime(settings) as runtime:
    # Stream quotes
    async for quote in runtime.stream_quotes(['AAPL', 'MSFT']):
        print(f"{quote.symbol}: ${quote.price}")
    
    # Or run pipelines
    spec = PipelineSpec(...)
    key = await runtime.run_pipeline(spec)
    
    # List running pipelines
    pipelines = await runtime.list_pipelines()
    
    # Stop a pipeline
    await runtime.stop_pipeline(key)
```

---

## Examples

### Example 1: Simple Quote Streaming

```python
import asyncio
from market_data_pipeline.orchestration import PipelineRuntime

async def main():
    async with PipelineRuntime() as runtime:
        count = 0
        async for quote in runtime.stream_quotes(['AAPL']):
            print(f"{quote.symbol}: ${quote.price}")
            count += 1
            if count >= 100:
                break

asyncio.run(main())
```

### Example 2: Multi-Provider with Fallback

```python
from market_data_pipeline.orchestration import (
    SourceRegistry,
    SourceRouter,
)

# Create registry
registry = SourceRegistry()
registry.discover_entrypoints()  # Find external providers

# Create sources
ibkr = registry.load("ibkr")
polygon = registry.load("polygon")

ibkr_source = ibkr(symbols=['AAPL'], ...)
polygon_source = polygon(symbols=['AAPL'], ...)

# Create router with fallback
router = SourceRouter(
    sources=[ibkr_source, polygon_source],
    strategy="first"
)

# Stream with automatic fallback
async for quote in router.stream():
    print(quote)
```

### Example 3: Rate-Limited Pipeline

```python
from market_data_pipeline.orchestration import (
    RateCoordinator,
    CircuitBreaker,
)

# Setup rate coordination
coordinator = RateCoordinator()
coordinator.register_provider("ibkr", capacity=60, refill_rate=60)

# Setup circuit breaker
breaker = CircuitBreaker(threshold=5, timeout=60.0)

# Use in pipeline
async def process_quotes():
    while True:
        # Check circuit breaker
        if breaker.is_open():
            await asyncio.sleep(1)
            continue
        
        try:
            # Acquire rate limit token
            await coordinator.acquire("ibkr")
            
            # Fetch quote
            quote = await ibkr.get_quote("AAPL")
            
            # Record success
            await breaker.record_success()
            
        except Exception as e:
            # Record failure
            await breaker.record_failure()
            await coordinator.record_failure("ibkr")
```

---

## Integration with Existing Code

### Pattern 1: Add Orchestration to Existing Pipeline

```python
# Before (existing code)
from market_data_pipeline import create_pipeline

pipeline = create_pipeline(...)
await pipeline.run()

# After (with orchestration)
from market_data_pipeline import create_pipeline
from market_data_pipeline.orchestration import (
    SourceRouter,
    RateCoordinator,
)

# Add router and coordinator
router = SourceRouter(sources=[...])
coordinator = RateCoordinator()

# Rest stays the same
pipeline = create_pipeline(...)
await pipeline.run()
```

### Pattern 2: Gradual Migration

```python
# Start with simple API
from market_data_pipeline import create_pipeline

pipeline = create_pipeline(...)

# Add orchestration features gradually
from market_data_pipeline.orchestration import RateCoordinator

coordinator = RateCoordinator()
coordinator.register_provider("ibkr")

# Eventually move to full runtime
from market_data_pipeline.orchestration import PipelineRuntime

async with PipelineRuntime() as runtime:
    # All orchestration features enabled
    ...
```

---

## Testing

### Unit Tests

All orchestration components have comprehensive unit tests:

```bash
# Run orchestration tests
pytest tests/unit/orchestration/ -v

# Results:
# - test_registry.py: 5 tests
# - test_circuit_breaker.py: 5 tests
# - test_coordinator.py: 7 tests
# - test_router.py: 7 tests
# - test_runtime.py: 6 tests
# Total: 30 tests
```

### Integration Tests

Full integration tests with existing pipeline:

```bash
# Run all tests (including orchestration)
pytest tests/unit/ -v

# Results: 123 tests (93 existing + 30 new)
```

### Backward Compatibility

```bash
# Verify no existing tests broke
pytest tests/unit/ --ignore=tests/unit/orchestration/ -v

# Results: 93 tests (all passing)
```

---

## Configuration

### Settings

```python
from market_data_pipeline.orchestration import PipelineRuntimeSettings

settings = PipelineRuntimeSettings(
    # Base pipeline settings
    pipeline=PipelineSettings(...),
    
    # Orchestration settings
    orchestration_enabled=True,
    max_concurrent_pipelines=10,
    enable_rate_coordination=True,
    
    # Circuit breaker settings
    circuit_breaker_threshold=5,
    circuit_breaker_timeout_sec=60.0,
    
    # Provider settings (future)
    providers={
        'ibkr': {...},
        'polygon': {...},
    }
)
```

---

## Future Enhancements

Phase 3.0 provides the foundation for:

1. **Multiple Routing Strategies**
   - Round-robin load balancing
   - Latency-based routing
   - Geographic routing

2. **Advanced Rate Limiting**
   - Per-tenant budgets
   - Priority queues
   - Adaptive rate limiting

3. **Enhanced Monitoring**
   - Provider health metrics
   - Circuit breaker state tracking
   - Route selection analytics

4. **Provider Management**
   - Hot-reload of providers
   - Provider versioning
   - A/B testing

---

## Migration Guide

### For Simple Use Cases

**No changes needed!** Continue using existing APIs.

### For Advanced Use Cases

1. **Enable orchestration:**
   ```python
   from market_data_pipeline.orchestration import PipelineRuntime
   ```

2. **Configure settings:**
   ```python
   settings = PipelineRuntimeSettings(...)
   ```

3. **Use runtime:**
   ```python
   async with PipelineRuntime(settings) as runtime:
       ...
   ```

### For Provider Developers

1. **Implement TickSource protocol**
2. **Register via entrypoint**
3. **Document rate limits**

---

## Summary

✅ **Backward Compatible**: All existing code works unchanged  
✅ **Opt-In**: Use orchestration features only when needed  
✅ **Tested**: 30 new tests, 123 total passing  
✅ **Production Ready**: Follows SOLID principles  
✅ **Extensible**: Easy to add new providers and strategies  

Phase 3.0 provides enterprise-grade orchestration while maintaining the simplicity of the existing API.

