# Phase 3.0 Evaluation - Runtime Orchestration Layer

## Executive Summary

**Overall Assessment:** ✅ **FEASIBLE with STRATEGIC CONSIDERATIONS**

The proposed Phase 3.0 orchestration layer is architecturally sound and fills genuine gaps in the current system. However, there are important overlaps, design considerations, and migration concerns that need careful planning.

**Recommendation:** Implement Phase 3.0 **incrementally** with modifications to avoid duplication and maintain backward compatibility with the existing pipeline architecture.

---

## Current Architecture Analysis

### What We Have Now

#### 1. **StreamingPipeline** (`pipeline.py`)
- **Role:** Single-pipeline orchestrator
- **Features:**
  - Connects source → operator → batcher → sink
  - Manages lifecycle (start, run, graceful shutdown)
  - Handles duration-limited execution
  - Error handling and logging
- **Scope:** One pipeline instance = one data flow

#### 2. **PipelineBuilder** (`pipeline_builder.py`)
- **Role:** Factory for creating pipelines
- **Features:**
  - Spec-based pipeline construction
  - Component validation and wiring
  - Overrides system for configuration
  - `create_pipeline()` convenience function
- **Scope:** Build-time configuration

#### 3. **PipelineService** (`runners/service.py`)
- **Role:** Multi-pipeline manager
- **Features:**
  - Create/delete/list multiple pipelines
  - AsyncTask management for concurrent pipelines
  - Pipeline registry (dict-based, in-memory)
  - Status tracking
- **Scope:** Runtime management of multiple pipelines
- **⚠️ OVERLAP:** This is already a simple orchestrator!

#### 4. **Source Abstraction** (`source/base.py`)
- **Protocol:** `TickSource`
- **Features:**
  - Protocol-based (already abstract!)
  - Capabilities system
  - Health/status reporting
  - Telemetry built-in
- **Implementations:** SyntheticSource, ReplaySource, IBKRSource

#### 5. **Pacing** (`pacing.py`)
- **Features:**
  - Token bucket rate limiter
  - Per-source pacing
  - Budget configuration
- **Current Scope:** Per-source instance

#### 6. **Config** (`config.py`)
- **Features:**
  - Pydantic settings
  - Environment variable support
  - YAML config loading
  - Comprehensive pipeline settings

### What's Missing (Phase 3.0 Addresses)

1. ✅ **Dynamic Provider Discovery** - No runtime loading of providers
2. ✅ **Fallback/Routing Logic** - No provider selection or failover
3. ✅ **Global Rate Coordination** - Pacing is per-source, not cross-pipeline
4. ✅ **Circuit Breaker** - Not implemented
5. ✅ **Job Scheduler** - PipelineService is basic, not feature-rich
6. ⚠️ **Provider Registry** - Partially addressed by PipelineService

---

## Phase 3.0 Proposal Analysis

### Component-by-Component Evaluation

#### 1. **ProviderRegistry**

**Proposed Purpose:** Dynamic loading of provider implementations

**Current State:**
- ✅ Providers exist: `SyntheticSource`, `ReplaySource`, `IBKRSource`
- ✅ Protocol exists: `TickSource` 
- ❌ No dynamic loading via `importlib` or entrypoints
- ❌ No registration system

**Overlap:** Minimal - this is genuinely new functionality

**Design Considerations:**
- Should this register `TickSource` implementations or higher-level "providers"?
- Current architecture has sources as **components**, not full providers
- IBKR provider would come from `market_data_core.ibkr`, not pipeline
  
**Recommendation:** ✅ **IMPLEMENT with modifications**
- Register `TickSource` implementations
- Support both static registration and entrypoint discovery
- Consider: Is this `SourceRegistry` or `ProviderRegistry`?
  - Current architecture: Sources are pipeline components
  - Phase 3 vision: Providers are external packages (IBKR, Polygon, etc.)
  - **Suggestion:** `SourceRegistry` for now, evolve to `ProviderRegistry` later

**Example:**
```python
class SourceRegistry:
    """Registry for TickSource implementations."""
    def register(self, name: str, source_cls: type[TickSource]) -> None: ...
    def load(self, name: str) -> type[TickSource]: ...
    def discover_entrypoints(self) -> None: ...  # importlib.metadata
```

---

#### 2. **SourceRouter**

**Proposed Purpose:** Route requests to "best available" provider with fallback

**Current State:**
- ❌ No routing logic
- ❌ No fallback mechanism
- ❌ No provider selection
- ✅ Multiple sources exist but are statically configured

**Overlap:** Minimal - genuinely new

**Design Considerations:**
- **Current Architecture:** Each pipeline has ONE source (configured at build time)
- **Phase 3 Vision:** Dynamic routing at runtime
- **Gap:** This fundamentally changes the execution model!

**Current Flow:**
```
PipelineBuilder → creates single source → StreamingPipeline → runs
```

**Phase 3 Flow:**
```
PipelineRuntime → SourceRouter → selects provider → yields quotes
```

**Questions:**
1. Does SourceRouter replace the current pipeline model or augment it?
2. How does this interact with the existing `StreamingPipeline`?
3. Should routing happen at pipeline creation or runtime?

**Recommendation:** ⚠️ **IMPLEMENT CAREFULLY**
- Start with **configuration-time routing** (select best source at build)
- Add **runtime fallback** for errors
- Don't break existing `StreamingPipeline` architecture
- Consider: Router as a **MetaSource** that wraps multiple sources

**Example:**
```python
class SourceRouter(TickSource):
    """Meta-source that routes to multiple underlying sources."""
    def __init__(self, sources: list[TickSource], strategy: str = "first"):
        self.sources = sources
        self.strategy = strategy  # "first", "round_robin", "fastest"
    
    async def stream(self) -> AsyncIterator[Quote]:
        # Route to best available source with fallback
        for source in self._select_sources():
            try:
                async for quote in source.stream():
                    yield quote
                break  # Success
            except Exception as e:
                logger.warning(f"Source {source} failed, trying next...")
                continue
```

---

#### 3. **RateCoordinator**

**Proposed Purpose:** Global rate limiting across all pipelines

**Current State:**
- ✅ Per-source pacing: `Pacer` class with token bucket
- ❌ No cross-pipeline coordination
- ❌ No global budgets
- ❌ No circuit breaker

**Overlap:** **MEDIUM** - extends existing pacing

**Design Considerations:**
- Current `Pacer` is per-source instance
- Multiple pipelines = multiple Pacer instances = no coordination
- Need shared state across pipelines

**Recommendation:** ✅ **IMPLEMENT**
- Build on existing `Pacer` infrastructure
- Add global coordination layer
- Support per-provider and per-tenant budgets
- Integrate with circuit breaker pattern

**Example:**
```python
class RateCoordinator:
    """Global rate coordination across all pipelines."""
    def __init__(self):
        self._global_buckets: dict[str, Pacer] = {}
        self._cooldowns: dict[str, CooldownManager] = {}
        self._circuit_breakers: dict[str, CircuitBreaker] = {}
    
    def register_provider(self, name: str, budget: Budget):
        self._global_buckets[name] = Pacer(budget)
    
    async def acquire(self, provider: str, n: int = 1):
        """Acquire tokens from global bucket."""
        if provider in self._circuit_breakers:
            if self._circuit_breakers[provider].is_open():
                raise CircuitBreakerOpen(provider)
        
        await self._global_buckets[provider].allow(n)
    
    async def record_failure(self, provider: str):
        """Record failure for circuit breaker."""
        if provider in self._circuit_breakers:
            await self._circuit_breakers[provider].record_failure()
```

---

#### 4. **JobScheduler**

**Proposed Purpose:** Async job orchestration and micro-batch management

**Current State:**
- ✅ **PipelineService already does this!**
  - Creates asyncio.Task per pipeline
  - Manages multiple concurrent pipelines
  - Tracks jobs in dict
  - Graceful shutdown
- ❌ No priority scheduling
- ❌ No resource limits
- ❌ No job dependencies

**Overlap:** **HIGH** - PipelineService is already a basic scheduler

**Recommendation:** ⚠️ **ENHANCE EXISTING vs. NEW**

**Option A:** Enhance `PipelineService`
- Add priority queues
- Add resource limits (max concurrent jobs)
- Add job dependencies
- Add more sophisticated lifecycle management

**Option B:** Create new `JobScheduler`, deprecate `PipelineService`
- Clean break from existing architecture
- More flexible design
- Requires migration

**Recommendation:** **Option A** - Enhance existing `PipelineService`
- Less disruption
- Maintains backward compatibility
- Can add features incrementally

**Enhancement Ideas:**
```python
class PipelineService:
    def __init__(self, config, max_concurrent: int = 10):
        self.pipelines: dict[str, PipelineHandle] = {}
        self.max_concurrent = max_concurrent
        self.pending_queue: asyncio.Queue[PipelineSpec] = asyncio.Queue()
    
    async def submit_job(self, spec: PipelineSpec, priority: int = 0):
        """Submit job with priority."""
        if len(self.pipelines) >= self.max_concurrent:
            await self.pending_queue.put((priority, spec))
        else:
            await self.create_pipeline(spec)
    
    async def _scheduler_loop(self):
        """Process pending jobs."""
        while self.running:
            if len(self.pipelines) < self.max_concurrent:
                priority, spec = await self.pending_queue.get()
                await self.create_pipeline(spec)
```

---

#### 5. **PipelineRuntime**

**Proposed Purpose:** Unified orchestration entrypoint

**Current State:**
- ✅ Multiple entrypoints exist:
  - `create_pipeline()` function (high-level API)
  - `PipelineBuilder` class
  - `PipelineService` (multi-pipeline)
  - FastAPI endpoint (`runners/api.py`)
- ❌ No unified "runtime" concept
- ❌ Components not wired together at startup

**Overlap:** **MEDIUM** - consolidates existing pieces

**Recommendation:** ✅ **IMPLEMENT** - but carefully integrate with existing APIs

**Design Considerations:**
- Don't break existing APIs (backward compatibility)
- `PipelineRuntime` should be a **higher-level orchestrator**
- Should wrap/use existing components, not replace them

**Example:**
```python
class PipelineRuntime:
    """High-level runtime orchestrator."""
    def __init__(self, settings: PipelineSettings):
        self.settings = settings
        self.registry = SourceRegistry()
        self.router = SourceRouter(self.registry, settings)
        self.rate_coordinator = RateCoordinator()
        self.service = PipelineService(settings)  # Reuse!
    
    async def __aenter__(self):
        await self.service.start()
        await self._initialize_providers()
        return self
    
    async def __aexit__(self, *args):
        await self.service.stop()
    
    async def stream_quotes(self, symbols: list[str]):
        """High-level streaming API."""
        # Use router to get best source
        async for quote in self.router.stream_quotes(symbols):
            yield quote
    
    async def run_pipeline(self, spec: PipelineSpec):
        """Run a full pipeline with all orchestration."""
        return await self.service.create_pipeline(spec)
```

---

## Architectural Concerns & Recommendations

### 1. **Two Execution Models**

**Current:**
```
Pipeline = Source → Operator → Batcher → Sink
(One instance, one data flow)
```

**Phase 3:**
```
Runtime = Router → Coordinator → Scheduler → (multiple pipelines)
(Orchestration layer above pipelines)
```

**Concern:** These are complementary but need clear boundaries

**Recommendation:**
- **Keep both models**
- Runtime orchestrates **multiple pipelines**
- Each pipeline still follows Source → Operator → Batcher → Sink
- Router can be **used as a source** in a pipeline

---

### 2. **Source vs Provider Abstraction**

**Current:** Sources are pipeline components implementing `TickSource`

**Phase 3:** Providers are external packages with multiple capabilities

**Gap:** IBKR is currently a `TickSource`. In Phase 3, is IBKR a provider?

**Recommendation:**
- **Define clear terminology:**
  - **Source:** Pipeline component (TickSource protocol)
  - **Provider:** External package (e.g., `market_data_core.ibkr`)
  - **Adapter:** Wraps provider → source
  
**Example:**
```python
# market_data_core.ibkr provides:
class IBKRProvider:
    def stream_quotes(...) -> AsyncIterator[Quote]: ...
    def get_historical_bars(...) -> list[Bar]: ...
    def get_options_chain(...) -> list[Option]: ...

# market_data_pipeline provides adapter:
class IBKRSource(TickSource):
    def __init__(self, provider: IBKRProvider):
        self.provider = provider
    
    async def stream(self) -> AsyncIterator[Quote]:
        async for quote in self.provider.stream_quotes(...):
            yield quote
```

---

### 3. **Settings Proliferation**

**Current:**
- `PipelineSettings` in `config.py` (comprehensive)
- `PipelineOverrides` in `pipeline_builder.py`
- Component-specific settings (DatabaseSinkSettings, etc.)

**Phase 3 adds:**
- Provider-specific settings
- Router settings
- Coordinator settings
- Runtime settings

**Concern:** Settings explosion

**Recommendation:**
- **Hierarchical settings structure:**
```python
@dataclass
class PipelineRuntimeSettings:
    # Core pipeline settings
    pipeline: PipelineSettings
    
    # Provider settings
    providers: dict[str, ProviderSettings]
    
    # Orchestration settings
    max_concurrent_pipelines: int = 10
    enable_routing: bool = False
    enable_rate_coordination: bool = True
    
    # Circuit breaker settings
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_sec: float = 60.0
```

---

### 4. **market_data_core Integration**

**Concern:** Phase 3 assumes IBKR provider comes from `market_data_core`, but:
- Current `IBKRSource` is a stub in pipeline
- Real IBKR implementation would be in `market_data_core.ibkr`
- How do they connect?

**Recommendation:**
- **Provider Discovery Pattern:**
```python
# In market_data_core.ibkr:
class IBKRProvider:
    """IBKR implementation with full TWS/Gateway connection."""
    ...

# Register via entrypoint (pyproject.toml):
[project.entry-points."market_data.providers"]
ibkr = "market_data_core.ibkr:IBKRProvider"

# In market_data_pipeline:
registry = SourceRegistry()
registry.discover_entrypoints()  # Finds IBKRProvider
provider_cls = registry.load("ibkr")
provider = provider_cls(settings.ibkr)
```

---

## Migration Path & Implementation Strategy

### Phase 3.1: Foundation (Non-Breaking)

**Add without changing existing code:**

1. **SourceRegistry**
   - New file: `registry.py`
   - Register existing sources statically
   - Add entrypoint discovery
   - No impact on existing pipelines

2. **RateCoordinator**
   - New file: `rate_coordinator.py`
   - Build on existing `Pacer`
   - Optional - existing pipelines don't use it

3. **Circuit Breaker**
   - New file: `circuit_breaker.py`
   - Standalone utility
   - Can be integrated later

**Tests:**
- `test_registry.py`
- `test_rate_coordinator.py`
- `test_circuit_breaker.py`

### Phase 3.2: Router & Integration

4. **SourceRouter**
   - New file: `router.py`
   - Implements `TickSource` protocol (can be used as a source!)
   - Wraps multiple sources with fallback
   - Backward compatible: can use single source

5. **Enhance PipelineService**
   - Add priority scheduling
   - Add resource limits
   - Add job dependencies
   - Maintain backward compatibility

**Tests:**
- `test_router.py`
- `test_service_enhanced.py`

### Phase 3.3: Runtime Orchestrator

6. **PipelineRuntime**
   - New file: `runtime.py`
   - Wires together: Registry → Router → Coordinator → Service
   - Provides unified API
   - Existing APIs still work

7. **Settings Consolidation**
   - Update `settings.py` with hierarchical structure
   - Maintain backward compatibility with `PipelineSettings`

**Tests:**
- `test_runtime.py`
- `test_runtime_integration.py`

### Phase 3.4: Examples & Documentation

8. **Examples**
   - `examples/run_quote_stream.py`
   - `examples/multi_provider_routing.py`
   - `examples/rate_limited_pipelines.py`

9. **Documentation**
   - Update architecture diagrams
   - Migration guide
   - Provider development guide

---

## Potential Issues & Solutions

### Issue 1: Two Ways to Create Pipelines

**Problem:**
- Old way: `create_pipeline()`, `PipelineBuilder`
- New way: `PipelineRuntime`

**Solution:**
- Keep both!
- `PipelineRuntime` is **optional** enhancement
- Simple use cases: use existing API
- Complex orchestration: use Runtime

### Issue 2: Provider vs Source Confusion

**Problem:**
- Terminology overlap
- IBKR is both a "provider" and a "source"

**Solution:**
- Clear documentation
- Use "Provider" for external packages
- Use "Source" for pipeline components
- Sources can **wrap** providers

### Issue 3: Performance Overhead

**Problem:**
- Router adds indirection
- Coordinator adds synchronization
- May impact latency

**Solution:**
- Make orchestration **opt-in**
- Simple pipelines bypass orchestration
- Benchmark and optimize
- Use async primitives carefully (minimize locks)

### Issue 4: Testing Complexity

**Problem:**
- Orchestration layer adds complexity
- Hard to test fallback logic
- Hard to test circuit breakers

**Solution:**
- Mock providers for tests
- Inject failures for testing
- Separate unit tests (per component) from integration tests
- Use fixtures for complex setups

---

## Final Recommendations

### ✅ IMPLEMENT

1. **SourceRegistry** - genuinely useful, no conflicts
2. **RateCoordinator** - fills real gap, extends existing pacing
3. **Circuit Breaker** - production necessity, standalone
4. **SourceRouter** - valuable for multi-provider, careful design needed

### ⚠️ ENHANCE (Don't Replace)

5. **JobScheduler** → Enhance `PipelineService`
   - Add features incrementally
   - Maintain backward compatibility
   - Avoid reinventing working code

### ✅ ADD (High-Level Wrapper)

6. **PipelineRuntime** - useful unification layer
   - Don't break existing APIs
   - Make it **opt-in**
   - Wire existing components together

### 📋 Additional Work Needed

7. **Provider Interface Design**
   - Define `MarketDataProvider` protocol in `market_data_core`
   - Clear contract for provider implementations
   - Standardized error handling

8. **Settings Hierarchy**
   - Consolidate settings into coherent structure
   - Avoid duplication
   - Support both flat and hierarchical config

9. **Documentation & Examples**
   - Clear migration path
   - When to use Runtime vs. simple API
   - Provider development guide

---

## Proposed File Structure

```
market-data-pipeline/
├── src/market_data_pipeline/
│   ├── __init__.py
│   ├── orchestration/          # NEW: Phase 3 components
│   │   ├── __init__.py
│   │   ├── registry.py         # SourceRegistry
│   │   ├── router.py           # SourceRouter
│   │   ├── coordinator.py      # RateCoordinator
│   │   ├── circuit_breaker.py  # Circuit breaker
│   │   └── runtime.py          # PipelineRuntime
│   │
│   ├── runners/                 # EXISTING: Enhanced
│   │   ├── service.py          # PipelineService (enhanced)
│   │   ├── api.py              # FastAPI app
│   │   └── cli.py
│   │
│   ├── api/                     # Phase 1-2 (existing)
│   ├── source/                  # Existing sources
│   ├── operator/                # Existing operators
│   ├── batcher/                 # Existing batchers
│   ├── sink/                    # Existing sinks
│   ├── pipeline.py              # StreamingPipeline (keep!)
│   ├── pipeline_builder.py      # PipelineBuilder (keep!)
│   ├── config.py                # Settings
│   ├── pacing.py                # Pacer (keep, extend)
│   └── ...
│
├── tests/
│   ├── unit/
│   │   ├── orchestration/       # NEW
│   │   │   ├── test_registry.py
│   │   │   ├── test_router.py
│   │   │   ├── test_coordinator.py
│   │   │   ├── test_circuit_breaker.py
│   │   │   └── test_runtime.py
│   │   └── ...
│   └── integration/
│       └── test_orchestration_e2e.py
│
└── examples/
    ├── run_quote_stream.py
    ├── multi_provider_routing.py
    └── rate_limited_pipelines.py
```

---

## Summary

**Phase 3.0 is FEASIBLE and VALUABLE**, but requires:

1. ✅ **Incremental Implementation** - don't break existing code
2. ✅ **Clear Abstraction Boundaries** - source vs provider vs adapter
3. ✅ **Enhance, Don't Replace** - PipelineService already works
4. ✅ **Opt-in Orchestration** - simple use cases stay simple
5. ✅ **Provider Interface Design** - needs coordination with market_data_core
6. ⚠️ **Careful Integration** - two execution models must coexist

**Timeline Estimate:**
- Phase 3.1 (Foundation): 1-2 weeks
- Phase 3.2 (Router & Enhanced Service): 1-2 weeks  
- Phase 3.3 (Runtime): 1 week
- Phase 3.4 (Examples & Docs): 1 week
- **Total: 4-6 weeks** for complete Phase 3.0

**Key Success Criteria:**
- ✅ Backward compatibility maintained
- ✅ All existing tests pass
- ✅ New orchestration features opt-in
- ✅ Clear migration path documented
- ✅ Provider interface defined with market_data_core

