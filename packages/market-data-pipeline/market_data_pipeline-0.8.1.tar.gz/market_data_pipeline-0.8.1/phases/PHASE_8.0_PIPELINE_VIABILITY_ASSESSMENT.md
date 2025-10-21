# Phase 8.0 Pipeline Integration — Viability & Planning Assessment

**Repository**: `market_data_pipeline`  
**Current Version**: v0.8.0 (README shows v0.8.1)  
**Target Version**: v0.9.0  
**Assessment Date**: October 17, 2025  
**Status**: 🔍 **PLANNING - NO CHANGES MADE**

---

## 📋 Executive Summary

### Overall Viability: **7.5/10** ⚠️ VIABLE WITH SIGNIFICANT CAVEATS

**Status**: Phase 8.0 is **technically viable** for the pipeline repository, but requires **significant foundational work** before implementation can begin.

### Critical Findings

| Category | Status | Impact |
|----------|--------|--------|
| **Core Dependency Missing** | 🔴 CRITICAL | market_data_core not in dependencies |
| **Existing Feedback System** | 🟢 GOOD | Phase 6.0A/B already implemented |
| **Local Protocol Definitions** | 🟡 MODERATE | RateCoordinator protocol exists locally |
| **Testing Infrastructure** | 🟢 EXCELLENT | 176 tests, good patterns established |
| **API Endpoints Missing** | 🟡 MODERATE | No health/control/federation endpoints |
| **Version Alignment** | 🔴 CRITICAL | Current v0.8.0, needs v0.9.0 |

---

## 🎯 Phase 8.0 Requirements for Pipeline

According to the plan, Pipeline v0.9.0 must:

### Day 3: Backpressure & Rate Control
- ✅ Emit/consume `FeedbackEvent` from Store (already done in Phase 6.0A)
- ✅ Produce `RateAdjustment` (logic exists, not using Core DTO)
- ❌ Remove duplicate feedback/adjustment models (need Core DTOs first)
- ❌ Implement Core's `RateController` protocol (local Protocol exists)
- ❌ Implement Core's `FeedbackPublisher` protocol (FeedbackBus exists)

### Day 4: Wiring & Metrics
- ✅ Wire settings into feedback path (PipelineFeedbackSettings exists)
- ✅ Expose Prometheus counters (Phase 6.0B metrics exist)
- ⚠️ Align metrics labels with Core DTO fields (need Core enums)

---

## 🔴 Critical Blockers

### 1. **market_data_core Dependency Completely Missing**

**Severity**: 🔴 **CRITICAL BLOCKER**

**Current State**:
```toml
# pyproject.toml - NO market_data_core dependency
dependencies = [
    "pydantic>=2.0.0",
    "fastapi>=0.100.0",
    # ... other deps, but NO market_data_core
]
```

**Evidence**:
- ❌ Not in `requirements.txt`
- ❌ Not in `pyproject.toml`
- ✅ All imports are conditional with `pytest.importorskip`
- ✅ Documentation references it as "optional external dependency"

**Current Usage Pattern**:
```python
# All market_data_core imports are optional
try:
    from market_data_core import Bar, Quote
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
```

**Impact on Phase 8.0**:
- Cannot import Core v1.1.0 DTOs (`FeedbackEvent`, `RateAdjustment`, etc.)
- Cannot implement Core protocols (`RateController`, `FeedbackPublisher`)
- Cannot use Core telemetry contracts (`HealthStatus`, `AuditEnvelope`)
- Pipeline has been designed to work **WITHOUT** Core dependency

**Required Action**:
```toml
# Add to pyproject.toml
dependencies = [
    "market_data_core>=1.1.0",  # NEW DEPENDENCY
    # ... existing deps
]
```

**Risk Assessment**: **HIGH**
- This is an **architectural shift** from optional to required dependency
- Need to verify market_data_core v1.1.0 exists and is published
- May break existing installations that don't have Core
- Requires coordination with Core release timeline

---

### 2. **Existing Phase 6.0 Feedback Implementation**

**Severity**: 🟡 **MODERATE - REQUIRES REFACTORING**

**Current State**: Pipeline already has a **complete, production-ready feedback system** implemented in Phase 6.0A/6.0B (October 2025):

**Existing Components**:

```python
# src/market_data_pipeline/orchestration/feedback/consumer.py
class RateCoordinator(Protocol):  # LOCAL PROTOCOL
    async def set_global_pressure(self, provider: str, level: str) -> None: ...
    async def set_budget_scale(self, provider: str, scale: float) -> None: ...

class FeedbackHandler:
    """Translates store FeedbackEvent into pipeline-level rate signals."""
    def __init__(self, rate: RateCoordinator, provider: str, policy: dict[str, float] | None = None):
        self.policy = policy or {"ok": 1.0, "soft": 0.5, "hard": 0.0}
    
    async def handle(self, event: Any) -> None:
        # Extract level from event (supports both attribute and dict access)
        if hasattr(event, "level"):
            level_obj = event.level
            level = getattr(level_obj, "value", str(level_obj)).lower()
        elif isinstance(event, dict):
            level = event.get("level", "ok").lower()
```

```python
# src/market_data_pipeline/orchestration/feedback/bus.py
class FeedbackBus:
    """Simple pub-sub bus for backpressure feedback events."""
    def subscribe(self, fn: Callable[[Any], Awaitable]) -> None: ...
    async def publish(self, event: Any) -> None: ...

def feedback_bus() -> FeedbackBus:
    """Get the global feedback bus. Tries to import from market_data_store first."""
    try:
        from market_data_store.coordinator.feedback import feedback_bus as store_bus
        return store_bus()
    except ImportError:
        # Fall back to local implementation
```

```python
# src/market_data_pipeline/settings/feedback.py
class PipelineFeedbackSettings(BaseSettings):
    enable_feedback: bool = Field(default=True)
    provider_name: str = Field(default="ibkr")
    scale_ok: float = Field(default=1.0, ge=0.0, le=1.0)
    scale_soft: float = Field(default=0.5, ge=0.0, le=1.0)
    scale_hard: float = Field(default=0.0, ge=0.0, le=1.0)
    
    model_config = {"env_prefix": "MDP_FB_"}
```

**Phase 6.0B Metrics**:
```python
# src/market_data_pipeline/metrics.py (lines 297-319)
PIPELINE_RATE_SCALE_FACTOR = Gauge(
    "pipeline_rate_scale_factor",
    "Current rate scale factor applied to provider (0.0..1.0).",
    ["provider"],
)

PIPELINE_BACKPRESSURE_STATE = Gauge(
    "pipeline_backpressure_state",
    "Backpressure state: 0=ok, 1=soft, 2=hard.",
    ["provider"],
)

PIPELINE_FEEDBACK_QUEUE_DEPTH = Gauge(
    "pipeline_feedback_queue_depth",
    "Queue depth reported by feedback source (echo of store).",
    ["source"],
)
```

**Integration in UnifiedRuntime**:
```python
# src/market_data_pipeline/runtime/unified_runtime.py (lines 141-179)
# Phase 6.0A: Setup backpressure feedback if enabled
self._feedback_handler = None
if self._settings.feedback.enable_feedback:
    self._rate_coordinator = RateCoordinator()
    self._feedback_handler = FeedbackHandler(
        rate=self._rate_coordinator,
        provider=self._settings.feedback.provider_name,
        policy=self._settings.feedback.get_policy()
    )
    feedback_bus().subscribe(self._feedback_handler.handle)
```

**Test Coverage**: 176 tests passing
- 25 unit tests for feedback
- 5 integration tests
- KEDA autoscaling manifests
- Production-ready documentation

**Gap Analysis vs Core v1.1.0**:

| Component | Current (Pipeline Phase 6.0) | Core v1.1.0 Expected | Gap |
|-----------|------------------------------|---------------------|-----|
| FeedbackEvent | Generic `Any` (duck-typed) | Pydantic `FeedbackEvent` DTO | Need Core DTO |
| RateAdjustment | Implicit in scale logic | Explicit Pydantic DTO | Need Core DTO |
| BackpressureLevel | String literals ("ok", "soft", "hard") | Enum `BackpressureLevel` | Need Core enum |
| RateController | Local Protocol | Core protocol | Replace with Core |
| FeedbackPublisher | FeedbackBus (different interface) | Core protocol | Adapter needed |

**Current Event Handling** (Duck-typed):
```python
async def handle(self, event: Any) -> None:
    # Extract level from event (supports both attribute and dict access)
    if hasattr(event, "level"):
        level_obj = event.level
        level = getattr(level_obj, "value", str(level_obj)).lower()
    elif isinstance(event, dict):
        level = event.get("level", "ok").lower()
```

**Phase 8.0 Target** (Core-typed):
```python
async def handle(self, event: FeedbackEvent) -> None:  # Core DTO
    scale = self._compute_scale(event.level)  # Core enum
    adjustment = RateAdjustment(  # Core DTO
        provider=self.provider,
        scale=scale,
        reason=event.level,
        ts=event.ts
    )
    await self.rate.apply(adjustment)
```

**Required Changes**:
1. Replace local `RateCoordinator` Protocol with Core protocol
2. Replace string literals with Core `BackpressureLevel` enum
3. Create `RateAdjustment` DTOs instead of implicit scale values
4. Type `event` parameter as Core `FeedbackEvent`
5. Adapt `FeedbackBus` to implement Core `FeedbackPublisher` protocol
6. Update tests to use Core DTOs
7. Update Prometheus metric labels to use Core enum values

**Backward Compatibility Concerns**: **HIGH**
- Breaking change to `FeedbackHandler` API
- Breaking change to `RateCoordinator` Protocol
- Settings remain compatible (string → enum mapping)
- Metrics labels change from strings to enum values (dashboard updates needed)

---

### 3. **No Health/Control/Audit/Federation Endpoints**

**Severity**: 🟡 **MODERATE - NEW DEVELOPMENT REQUIRED**

**Current State**:
```python
# src/market_data_pipeline/runners/api.py - FastAPI app exists
@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "healthy", "service": "market-data-pipeline"}  # Simple dict
```

**Gap**: 
- ✅ Basic `/health` endpoint exists
- ❌ Returns simple dict, not Core `HealthStatus` DTO
- ❌ No component health tracking
- ❌ No `/control/*` endpoints (pause/resume/reload)
- ❌ No `AuditEnvelope` emission
- ❌ No `/federation/*` endpoints
- ❌ No `ClusterTopology` exposure

**Phase 8.0 Requirements**:
```python
# Day 1: Orchestrator v0.4.0 - but Pipeline has no orchestrator role?
@router.get("/health", response_model=HealthStatus)  # Core DTO
async def get_health():
    components = [
        HealthComponent(name="feedback_bus", state="healthy"),
        HealthComponent(name="rate_coordinator", state="healthy"),
    ]
    return HealthStatus(
        service="pipeline",
        state="healthy",
        components=components,
        version=__version__,
        ts=time.time(),
    )
```

**Question**: Phase 8.0 plan focuses on Orchestrator receiving these changes on Day 1-2. **Does Pipeline need these endpoints?**

**Analysis**:
- Pipeline is NOT an orchestrator in the multi-repo architecture
- Pipeline consumes feedback, doesn't provide control surfaces
- Federation/cluster topology likely managed by Orchestrator repo, not Pipeline
- **Recommendation**: Pipeline may only need Day 3-4 changes, NOT Day 1-2

**Clarification Needed**: 
❓ Should Pipeline v0.9.0 expose health/control/federation endpoints, or is it purely a consumer of Core contracts for feedback?

---

## 🟢 Strengths & Readiness

### 1. **Excellent Testing Infrastructure**

**Current State**: ✅ **PRODUCTION-READY**

```
tests/
├── unit/ (35 files)
│   ├── orchestration/
│   │   ├── test_feedback_handler.py (complete)
│   │   ├── test_coordinator_feedback.py (complete)
│   │   └── test_coordinator.py (complete)
│   └── metrics/
│       └── test_pipeline_metrics.py (complete)
└── integration/
    └── test_feedback_integration.py (end-to-end)
```

**Test Quality**:
- ✅ 176 tests passing
- ✅ Protocol conformance tests
- ✅ Integration tests with feedback loop
- ✅ Prometheus metrics validation
- ✅ Mock `FeedbackEvent` classes used consistently
- ✅ Async patterns tested thoroughly

**Adaptation Path**: Tests already use mock DTOs, easy to replace with Core DTOs

---

### 2. **Protocol-Based Design Philosophy**

**Current State**: ✅ **ALREADY ALIGNED**

Pipeline extensively uses `typing.Protocol` for loose coupling:

```python
# src/market_data_pipeline/source/base.py
class TickSource(Protocol):
    """Protocol for market data sources."""
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    def ticks(self) -> AsyncIterator[Tick]: ...

# src/market_data_pipeline/sink/base.py
class Sink(Protocol):
    """Protocol for data persistence sinks."""
    async def write(self, batch: List[Bar]) -> None: ...
    async def close(self) -> None: ...

# src/market_data_pipeline/operator/base.py
class Operator(Protocol):
    """Protocol for data transformation operators."""
    async def process(self, tick: Tick) -> Optional[Bar]: ...

# src/market_data_pipeline/batcher/base.py
class Batcher(Protocol):
    """Protocol for batching aggregated data."""
    async def add(self, item: Bar) -> None: ...
    async def flush(self) -> List[Bar]: ...
```

**Alignment**: Phase 8.0's use of Core protocols (`RateController`, `FeedbackPublisher`) is **perfectly aligned** with existing architecture.

---

### 3. **Comprehensive Prometheus Metrics**

**Current State**: ✅ **KEDA-READY**

Phase 6.0B already implemented KEDA autoscaling metrics:

```python
# Existing metrics match Phase 8.0 requirements
PIPELINE_RATE_SCALE_FACTOR        # ✅ Day 4 requirement
PIPELINE_BACKPRESSURE_STATE       # ✅ Day 4 requirement  
PIPELINE_FEEDBACK_QUEUE_DEPTH     # ✅ Day 4 requirement
```

**Prometheus Endpoint**:
```python
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics_endpoint() -> str:
    return generate_latest()  # Already exposes all metrics
```

**Gap**: Metric labels use string literals, need to align with Core enum values.

---

### 4. **Pydantic Settings Architecture**

**Current State**: ✅ **COMPOSABLE**

```python
# src/market_data_pipeline/settings/runtime_unified.py
from pydantic_settings import BaseSettings
from .feedback import PipelineFeedbackSettings

class UnifiedRuntimeSettings(BaseSettings):
    mode: Literal["classic", "dag"] = Field(default="classic")
    feedback: PipelineFeedbackSettings = Field(
        default_factory=PipelineFeedbackSettings,
        description="Backpressure feedback settings (Phase 6.0A)"
    )
    
    model_config = {"env_prefix": "MDP_"}
```

**Alignment**: Matches Phase 8.0's `CompositeSettings` pattern perfectly.

---

## 🔧 Technical Debt & Compatibility

### 1. **Version Number Inconsistency**

**Current State**: ⚠️ **MINOR ISSUE**

```python
# src/market_data_pipeline/__init__.py
__version__ = "0.8.0"  # Phase 3.0 - Runtime Orchestration

# README.md
[![Version](https://img.shields.io/badge/version-0.8.1-blue)]

# pyproject.toml
version = "0.7.0"
```

**Phase 8.0 Requirement**: v0.9.0

**Action Required**: 
1. Decide canonical version (0.8.0 or 0.8.1)
2. Update all references
3. Bump to 0.9.0 for Phase 8.0

---

### 2. **market_data_store Integration**

**Current State**: ✅ **OPTIONAL DEPENDENCY**

```python
# FeedbackBus tries to import from store
try:
    from market_data_store.coordinator.feedback import feedback_bus as store_bus
    return store_bus()
except ImportError:
    # Fall back to local implementation
    if _global_bus is None:
        _global_bus = FeedbackBus()
    return _global_bus
```

**Phase 8.0 Alignment**: ✅ **GOOD**
- Store v0.4.0 will emit Core `FeedbackEvent`
- Pipeline's duck-typed handler can already consume it
- Once Core DTOs added, type safety improves

---

## 📊 Dependency Analysis

### Current Dependencies

```toml
# pyproject.toml - core dependencies
dependencies = [
    "pydantic>=2.0.0",           # ✅ Compatible with Core
    "pydantic-settings>=2.0.0",  # ✅ Compatible with Core
    "fastapi>=0.100.0",          # ✅ For API endpoints
    "prometheus-client>=0.17.0", # ✅ Metrics ready
    # ... 20+ other deps
]
```

**Missing**:
- ❌ `market_data_core>=1.1.0`

### Required for Phase 8.0

```toml
dependencies = [
    "market_data_core>=1.1.0",  # CRITICAL - NEW
    # ... existing deps
]
```

**Risk**: Need to verify Core v1.1.0 is published/available.

---

## 🗺️ Implementation Roadmap

### Pre-Phase 8.0 Requirements

**Must Complete BEFORE Day 3 Work**:

1. ✅ **Verify Core v1.1.0 Availability**
   - Confirm Core v1.1.0 is released and published
   - Verify all required DTOs exist:
     - `telemetry.FeedbackEvent`
     - `telemetry.RateAdjustment`
     - `telemetry.BackpressureLevel` (enum)
     - `telemetry.HealthStatus`
     - `telemetry.HealthComponent`
     - `telemetry.AuditEnvelope`
     - `telemetry.ControlAction`
     - `telemetry.ControlResult`
   - Verify protocols exist:
     - `protocols.RateController`
     - `protocols.FeedbackPublisher`

2. ✅ **Add Core Dependency**
   ```bash
   # Add to pyproject.toml
   dependencies = ["market_data_core>=1.1.0", ...]
   
   # Update requirements.txt
   pip-compile pyproject.toml
   
   # Install
   pip install -e .
   ```

3. ✅ **Version Alignment**
   - Resolve 0.8.0 vs 0.8.1 discrepancy
   - Bump to 0.9.0 in all locations:
     - `src/market_data_pipeline/__init__.py`
     - `pyproject.toml`
     - `README.md`

### Day 3: Backpressure & Rate Control

**Estimated Effort**: 8-12 hours

**Files to Modify**:

1. **`src/market_data_pipeline/orchestration/feedback/consumer.py`**
   ```python
   # BEFORE (Phase 6.0)
   from typing import Protocol
   class RateCoordinator(Protocol):
       async def set_global_pressure(self, provider: str, level: str) -> None: ...
       async def set_budget_scale(self, provider: str, scale: float) -> None: ...
   
   # AFTER (Phase 8.0)
   from market_data_core.protocols import RateController
   from market_data_core.telemetry import FeedbackEvent, RateAdjustment, BackpressureLevel
   
   class DefaultRateController(RateController):  # Core protocol
       def __init__(self, coordinator): self.coordinator = coordinator
       
       async def apply(self, adj: RateAdjustment) -> None:
           await self.coordinator.set_budget_scale(adj.provider, adj.scale)
   ```

2. **`src/market_data_pipeline/orchestration/feedback/bus.py`**
   ```python
   # Adapt to Core FeedbackPublisher protocol
   from market_data_core.protocols import FeedbackPublisher
   from market_data_core.telemetry import FeedbackEvent
   
   class FeedbackBus(FeedbackPublisher):  # Implement Core protocol
       async def publish(self, event: FeedbackEvent) -> None:
           for fn in self._subscribers:
               await fn(event)
   ```

3. **`src/market_data_pipeline/orchestration/coordinator.py`**
   ```python
   # Update backpressure level handling
   from market_data_core.telemetry import BackpressureLevel
   
   async def set_global_pressure(self, provider: str, level: BackpressureLevel) -> None:
       # Map enum to metric value
       level_value = {"ok": 0, "soft": 1, "hard": 2}[level.value]
       self._metric_pressure.labels(provider=provider).set(level_value)
   ```

**Tests to Update**:
- `tests/unit/orchestration/test_feedback_handler.py`
- `tests/unit/orchestration/test_coordinator_feedback.py`
- `tests/integration/test_feedback_integration.py`

**Breaking Changes**:
- ⚠️ `FeedbackHandler.__init__()` signature changes (RateCoordinator → RateController)
- ⚠️ `event` parameter type changes (Any → FeedbackEvent)
- ⚠️ `level` handling changes (str → BackpressureLevel enum)

**Deprecation Strategy**:
```python
# Support both old and new interfaces for one release
class FeedbackHandler:
    def __init__(
        self,
        rate: Union[RateCoordinator, RateController],  # Accept both
        provider: str,
        policy: Optional[Dict[str, float]] = None,
    ):
        if hasattr(rate, 'apply'):  # New Core protocol
            self.rate_controller = rate
        else:  # Old local protocol
            warnings.warn("RateCoordinator deprecated, use Core RateController", DeprecationWarning)
            self.rate_controller = _adapt_legacy(rate)
```

### Day 4: Wiring & Metrics

**Estimated Effort**: 4-6 hours

**Changes**:

1. **Metrics Label Alignment**
   ```python
   # src/market_data_pipeline/metrics.py
   # Update label values to use Core enum strings
   from market_data_core.telemetry import BackpressureLevel
   
   def record_backpressure(provider: str, level: BackpressureLevel):
       state_map = {
           BackpressureLevel.ok: 0,
           BackpressureLevel.soft: 1,
           BackpressureLevel.hard: 2,
       }
       PIPELINE_BACKPRESSURE_STATE.labels(provider=provider).set(state_map[level])
   ```

2. **Settings Compatibility**
   ```python
   # src/market_data_pipeline/settings/feedback.py
   # Map string config to Core enums
   from market_data_core.telemetry import BackpressureLevel
   
   def get_policy(self) -> Dict[BackpressureLevel, float]:
       return {
           BackpressureLevel.ok: self.scale_ok,
           BackpressureLevel.soft: self.scale_soft,
           BackpressureLevel.hard: self.scale_hard,
       }
   ```

**Tests**:
- `tests/unit/metrics/test_pipeline_metrics.py`
- Verify Prometheus label values match Core enum values

**Dashboard Updates Required**:
- Grafana dashboards using string literals need enum value updates
- Prometheus queries using label filters may need updates

### Optional: Health Endpoint Enhancement

**If Required** (clarify with cross-repo plan):

```python
# src/market_data_pipeline/runners/api.py
from market_data_core.telemetry import HealthStatus, HealthComponent

@app.get("/health", response_model=HealthStatus)
async def health() -> HealthStatus:
    components = [
        HealthComponent(name="feedback_bus", state="healthy"),
        HealthComponent(name="rate_coordinator", state="healthy"),
    ]
    return HealthStatus(
        service="pipeline",
        state="healthy",
        components=components,
        version=__version__,
        ts=time.time(),
    )
```

---

## 🧪 Testing Strategy

### Unit Tests

**Existing Test Structure** (reusable):
```python
# tests/unit/orchestration/test_feedback_handler.py
class MockFeedbackEvent:  # Replace with Core DTO
    def __init__(self, level: str, queue_size: int = 0, capacity: int = 1000):
        self.level = level
        self.queue_size = queue_size
        self.capacity = capacity
```

**Updated Tests**:
```python
from market_data_core.telemetry import FeedbackEvent, BackpressureLevel

def test_feedback_handler_soft_backpressure():
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=800,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    # ... test logic
```

### Integration Tests

**Existing** (adapt):
- `tests/integration/test_feedback_integration.py`

**New** (Phase 8.0 specific):
- `tests/integration/test_core_contract_conformance.py`
  - Verify RateController protocol conformance
  - Verify FeedbackPublisher protocol conformance
  - Verify FeedbackEvent → RateAdjustment conversion
  - Verify enum roundtrip (str ↔ BackpressureLevel)

### Meta Tests (Cross-Repo)

**Pipeline's Responsibility**:
```python
# meta/tests/test_pipeline_contracts.py
def test_rate_controller_protocol():
    from market_data_pipeline.orchestration.feedback import DefaultRateController
    from market_data_core.protocols import RateController
    assert isinstance(DefaultRateController(...), RateController)

def test_feedback_event_consumption():
    from market_data_core.telemetry import FeedbackEvent, BackpressureLevel
    from market_data_pipeline.orchestration.feedback import FeedbackHandler
    
    event = FeedbackEvent(
        coordinator_id="test",
        queue_size=500,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    # Handler should accept Core DTO without errors
```

---

## ⚠️ Risks & Mitigation

### Risk 1: Core v1.1.0 Not Available

**Likelihood**: Medium  
**Impact**: Critical (blocks entire Phase 8.0)

**Mitigation**:
- ✅ Verify Core v1.1.0 release schedule BEFORE starting
- ✅ Review Core v1.1.0 API contracts BEFORE planning
- ✅ Build against Core v1.1.0 beta if needed
- ⚠️ Consider: Can we implement against Core v1.0.0 and upgrade?

### Risk 2: Breaking Changes to Production Feedback System

**Likelihood**: High  
**Impact**: High (Phase 6.0 just completed, October 2025)

**Mitigation**:
- ✅ Deprecation strategy with dual support for 1 release
- ✅ Feature flag: `MDP_FB_USE_CORE_CONTRACTS=false` (default true)
- ✅ Comprehensive test coverage before/after
- ✅ Gradual rollout: v0.9.0-alpha, v0.9.0-beta, v0.9.0

### Risk 3: Prometheus Dashboard Breakage

**Likelihood**: Medium  
**Impact**: Medium (monitoring/alerting)

**Mitigation**:
- ✅ Document label value changes
- ✅ Provide PromQL query migration guide
- ✅ Maintain backward-compatible label values if possible
- ✅ Version Grafana dashboards

### Risk 4: Unclear Role Boundaries

**Likelihood**: Medium  
**Impact**: Medium (wasted effort)

**Question**: Does Pipeline need health/control/federation endpoints (Day 1-2) or only feedback contracts (Day 3-4)?

**Mitigation**:
- ✅ Clarify Pipeline's role in multi-repo architecture
- ✅ Review Phase 8.0 plan with architects
- ✅ Confirm which days apply to Pipeline

### Risk 5: market_data_store Synchronization

**Likelihood**: Medium  
**Impact**: Medium (integration testing)

**Current State**: Pipeline imports `market_data_store` optionally for feedback bus

**Mitigation**:
- ✅ Coordinate Store v0.4.0 release (emits Core FeedbackEvent)
- ✅ Test integration with Store v0.4.0-beta
- ✅ Ensure backward compatibility with Store v0.3.x

---

## 📅 Timeline Estimate

### Pre-Work (Must Complete First)
- **Verify Core v1.1.0 availability**: 1-2 hours
- **Add Core dependency**: 1 hour
- **Version alignment**: 0.5 hours
- **Review Core contracts**: 2-3 hours
- **Update development environment**: 1 hour

**Total Pre-Work**: **5-7.5 hours**

### Day 3 Implementation (Backpressure & Rate Control)
- **Replace RateCoordinator protocol**: 2-3 hours
- **Implement FeedbackPublisher adapter**: 2 hours
- **Update FeedbackHandler**: 2-3 hours
- **Update RateCoordinator integration**: 2 hours
- **Update unit tests**: 2-3 hours
- **Update integration tests**: 2 hours

**Total Day 3**: **12-15 hours**

### Day 4 Implementation (Wiring & Metrics)
- **Metrics label alignment**: 2-3 hours
- **Settings enum mapping**: 1-2 hours
- **Test metrics conformance**: 1-2 hours
- **Dashboard update documentation**: 1 hour

**Total Day 4**: **5-8 hours**

### Optional: Health/Control Endpoints
- **Health endpoint with Core DTOs**: 2 hours
- **Component health tracking**: 2 hours
- **Tests**: 1 hour

**Total Optional**: **5 hours**

### Testing & Documentation
- **Cross-repo contract tests**: 3-4 hours
- **Update README/docs**: 2 hours
- **CHANGELOG**: 1 hour
- **Migration guide**: 2 hours

**Total Testing/Docs**: **8-9 hours**

### **Grand Total: 30-44.5 hours**

**Recommended Sprint**: 5-6 working days (with buffer)

---

## 📝 File Inventory

### Files to Modify

| File | Changes | Complexity | Tests |
|------|---------|-----------|-------|
| `pyproject.toml` | Add Core dependency | Low | - |
| `src/market_data_pipeline/__init__.py` | Bump version to 0.9.0 | Low | - |
| `src/market_data_pipeline/orchestration/feedback/consumer.py` | Replace Protocol, add Core DTOs | **High** | ✅ |
| `src/market_data_pipeline/orchestration/feedback/bus.py` | Implement FeedbackPublisher | Medium | ✅ |
| `src/market_data_pipeline/orchestration/coordinator.py` | Use BackpressureLevel enum | Medium | ✅ |
| `src/market_data_pipeline/settings/feedback.py` | Enum mapping | Low | ✅ |
| `src/market_data_pipeline/metrics.py` | Label alignment | Low | ✅ |
| `src/market_data_pipeline/runtime/unified_runtime.py` | Update instantiation | Medium | ✅ |
| `tests/unit/orchestration/test_feedback_handler.py` | Use Core DTOs | Medium | - |
| `tests/unit/orchestration/test_coordinator_feedback.py` | Use Core DTOs | Medium | - |
| `tests/integration/test_feedback_integration.py` | Use Core DTOs | Medium | - |
| `tests/unit/metrics/test_pipeline_metrics.py` | Verify enum labels | Low | - |

### New Files to Create

| File | Purpose | Priority |
|------|---------|----------|
| `tests/integration/test_core_contract_conformance.py` | Protocol conformance | High |
| `docs/PHASE_8.0_MIGRATION_GUIDE.md` | User migration guide | High |
| `PHASE_8.0_IMPLEMENTATION_COMPLETE.md` | Implementation record | Medium |

### Documentation to Update

| File | Updates |
|------|---------|
| `README.md` | Version bump, Core dependency |
| `CHANGELOG.md` | Phase 8.0 changes |
| `docs/ORCHESTRATION.md` | Core protocol usage |
| `examples/*.py` | Use Core DTOs where applicable |

---

## 🔍 Open Questions for Clarification

### Critical Questions

1. **❓ Core Dependency Availability**
   - Is `market_data_core` v1.1.0 published/available?
   - Can we install it: `pip install market_data_core==1.1.0`?
   - What is the Core release timeline vs Pipeline v0.9.0?

2. **❓ Pipeline's Role in Multi-Repo Architecture**
   - Should Pipeline implement health/control/federation endpoints (Day 1-2)?
   - Or is Pipeline purely a consumer of Core contracts (Day 3-4 only)?
   - Is Pipeline a "service" that needs control surfaces, or a "library"?

3. **❓ Breaking Changes Acceptability**
   - Is v0.9.0 allowed to have breaking changes to Phase 6.0 APIs?
   - Or must we maintain backward compatibility?
   - What's the deprecation timeline?

4. **❓ Coordination with Store v0.4.0**
   - When is Store v0.4.0 (emitting Core FeedbackEvent) releasing?
   - Can we test Pipeline v0.9.0 against Store v0.3.x (pre-Core)?
   - Do we need dual-compatibility during transition?

5. **❓ Meta CI Infrastructure**
   - Where will cross-repo contract tests live?
   - Who owns the meta CI pipeline?
   - What's the CI strategy for multi-repo PRs?

### Nice-to-Have Clarifications

6. **❓ CompositeSettings Adoption**
   - Phase 8.0 mentions CompositeSettings - should Pipeline adopt?
   - Or continue with UnifiedRuntimeSettings?
   - Is this optional or required?

7. **❓ Grafana Dashboard Ownership**
   - Who updates Grafana dashboards for label changes?
   - Is there a shared dashboard repository?
   - Migration vs new dashboard strategy?

---

## 🎯 Recommendations

### Immediate Actions (This Week)

1. **✅ Verify Core v1.1.0 Availability**
   - Contact Core team
   - Review Core v1.1.0 API documentation
   - Confirm DTOs and protocols exist as specified

2. **✅ Clarify Pipeline's Role**
   - Does Pipeline need Day 1-2 (health/control/federation)?
   - Or only Day 3-4 (feedback contracts)?
   - Get architectural confirmation

3. **✅ Review Breaking Change Policy**
   - Confirm v0.9.0 can break Phase 6.0 APIs
   - Or must maintain backward compat
   - Define deprecation strategy

### Pre-Implementation Checklist

Before starting Day 3 work:

- [ ] Core v1.1.0 is published and accessible
- [ ] Core contracts reviewed and match Phase 8.0 plan
- [ ] Pipeline role clarified (which days apply)
- [ ] Breaking change policy confirmed
- [ ] Store v0.4.0 timeline confirmed
- [ ] Meta CI strategy defined
- [ ] Version numbers aligned across repo

### Phase 8.0 Execution Strategy

**Recommended Approach**: **Incremental with Feature Flags**

```python
# Allow gradual adoption
class PipelineFeedbackSettings(BaseSettings):
    use_core_contracts: bool = Field(
        default=True,
        description="Use Core v1.1.0 contracts (disable for v0.8.x compat)"
    )
```

**Phases**:
1. **v0.9.0-alpha**: Core contracts, feature-flagged (default OFF)
2. **v0.9.0-beta**: Feature flag default ON, dual support
3. **v0.9.0**: Full Core adoption, deprecation warnings
4. **v0.10.0**: Remove legacy support

### Success Criteria

Phase 8.0 is successful when:

- ✅ Pipeline installs with `market_data_core>=1.1.0` dependency
- ✅ `FeedbackHandler` accepts Core `FeedbackEvent` DTO
- ✅ `RateAdjustment` DTOs created and used
- ✅ Local `RateCoordinator` Protocol replaced with Core protocol
- ✅ `FeedbackBus` implements Core `FeedbackPublisher` protocol
- ✅ Prometheus metrics use Core enum label values
- ✅ All 176+ tests passing
- ✅ Integration with Store v0.4.0 verified
- ✅ Meta contract tests passing
- ✅ Zero downtime deployment path documented
- ✅ Grafana dashboard migration guide complete

---

## 📚 Appendix

### A. Current Feedback System Architecture (Phase 6.0)

```
┌─────────────────────────────────────────────────────────────┐
│                     market_data_store                       │
│  WriteCoordinator                                           │
│    - Queue fills up (6000/10000)                           │
│    - Publishes FeedbackEvent (duck-typed dict/object)     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ FeedbackEvent (duck-typed)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              market_data_pipeline (Phase 6.0)               │
│                                                              │
│  FeedbackBus (pub-sub)                                      │
│    └─▶ FeedbackHandler.handle(event: Any)                  │
│         - Extract level: "ok"/"soft"/"hard" (string)       │
│         - Map to scale: 1.0, 0.5, 0.0 (float)             │
│         - RateCoordinator.set_budget_scale(provider, scale) │
│         - RateCoordinator.set_global_pressure(provider, level)│
│                                                              │
│  RateCoordinator (local Protocol)                           │
│    - Token bucket rate adjustment                           │
│    - Prometheus metrics: PIPELINE_RATE_SCALE_FACTOR        │
│                         PIPELINE_BACKPRESSURE_STATE        │
│                                                              │
│  Metrics: pipeline_backpressure_state{provider="ibkr"}=1   │
└─────────────────────────────────────────────────────────────┘
```

### B. Target Feedback System Architecture (Phase 8.0)

```
┌─────────────────────────────────────────────────────────────┐
│             market_data_store v0.4.0 (Day 5)               │
│  RedisFeedbackPublisher (Core FeedbackPublisher protocol)  │
│    - Publishes Core FeedbackEvent DTO                      │
│      { coordinator_id, queue_size, capacity,               │
│        level: BackpressureLevel.soft, source, ts }        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ FeedbackEvent (Core DTO)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│          market_data_pipeline v0.9.0 (Day 3-4)             │
│                                                              │
│  FeedbackBus (Core FeedbackPublisher)                       │
│    └─▶ FeedbackHandler.handle(event: FeedbackEvent)       │
│         - to_adjustment(event) → RateAdjustment DTO        │
│         - RateController.apply(adjustment)                  │
│                                                              │
│  DefaultRateController (Core RateController protocol)       │
│    async def apply(self, adj: RateAdjustment):             │
│      - self.token_bucket.set_rate(adj.scale)               │
│                                                              │
│  Metrics: pipeline_backpressure_state{provider="ibkr",     │
│           reason="soft"}=1  # Core enum labels             │
└─────────────────────────────────────────────────────────────┘
```

### C. Mapping: Phase 6.0 → Phase 8.0

| Phase 6.0 (Current) | Phase 8.0 (Target) | Change Type |
|---------------------|-------------------|-------------|
| `event: Any` | `event: FeedbackEvent` | Type tightening |
| `level: str` ("ok") | `level: BackpressureLevel.ok` | Enum |
| `scale: float` (implicit) | `RateAdjustment(scale=...)` | Explicit DTO |
| Local `RateCoordinator` Protocol | Core `RateController` | Protocol replacement |
| `FeedbackBus` (custom) | Core `FeedbackPublisher` | Protocol impl |
| String policy map | Enum policy map | Enum keys |
| Metric labels: string | Metric labels: enum values | Label update |

### D. Test Coverage Map

| Test File | Current Coverage | Phase 8.0 Updates Needed |
|-----------|-----------------|-------------------------|
| `test_feedback_handler.py` | 25 tests, MockFeedbackEvent | Replace mocks with Core DTOs |
| `test_coordinator_feedback.py` | 13 tests, scale validation | Add RateAdjustment assertions |
| `test_feedback_integration.py` | 5 tests, end-to-end | Use Core DTOs end-to-end |
| `test_pipeline_metrics.py` | 8 tests, label validation | Verify Core enum label values |
| **New**: `test_core_contract_conformance.py` | - | Protocol isinstance checks |

### E. Environment Variables

| Current (Phase 6.0) | Phase 8.0 | Notes |
|--------------------|----------|-------|
| `MDP_FB_ENABLE_FEEDBACK=true` | ✅ Same | No change |
| `MDP_FB_PROVIDER_NAME=ibkr` | ✅ Same | No change |
| `MDP_FB_SCALE_OK=1.0` | ✅ Same | Mapped to enum |
| `MDP_FB_SCALE_SOFT=0.5` | ✅ Same | Mapped to enum |
| `MDP_FB_SCALE_HARD=0.0` | ✅ Same | Mapped to enum |
| - | `MDP_FB_USE_CORE_CONTRACTS=true` | **New** (feature flag) |

### F. Prometheus Metrics Changes

| Metric | Current Labels | Phase 8.0 Labels | Dashboard Impact |
|--------|---------------|-----------------|-----------------|
| `pipeline_rate_scale_factor` | `provider` (str) | ✅ Same | None |
| `pipeline_backpressure_state` | `provider` (str) | `provider` (str), value 0/1/2 | None (already numeric) |
| `pipeline_feedback_queue_depth` | `source` (str) | ✅ Same | None |

**Good News**: Metrics are already numeric (0/1/2), so dashboard queries don't need updates!

---

## ✅ Final Verdict

### Viability: **7.5/10** ⚠️ **VIABLE WITH PREPARATION**

**Can We Do Phase 8.0?** **YES**, but with critical prerequisites.

**Should We Do Phase 8.0 Now?** **NOT YET** - complete prerequisites first.

### Prerequisites (Blocking)

1. ✅ Confirm Core v1.1.0 availability
2. ✅ Clarify Pipeline's role (Day 3-4 only? Or Day 1-4?)
3. ✅ Define breaking change policy
4. ✅ Coordinate with Store v0.4.0 timeline

### Go/No-Go Criteria

**GO** if:
- ✅ Core v1.1.0 is published and accessible
- ✅ Architectural questions answered
- ✅ Breaking changes approved
- ✅ 5-6 day sprint available

**NO-GO** if:
- ❌ Core v1.1.0 not ready
- ❌ Role ambiguity remains
- ❌ Breaking changes not allowed
- ❌ Store v0.4.0 significantly delayed

### Confidence Level

**Technical Implementation**: 9/10 ✅ (well-understood, good patterns)  
**Dependency Coordination**: 5/10 ⚠️ (requires cross-repo sync)  
**Timeline Predictability**: 7/10 ✅ (clear scope, known codebase)

---

**Assessment Completed**: October 17, 2025  
**Next Step**: Resolve open questions, then proceed to implementation planning.

