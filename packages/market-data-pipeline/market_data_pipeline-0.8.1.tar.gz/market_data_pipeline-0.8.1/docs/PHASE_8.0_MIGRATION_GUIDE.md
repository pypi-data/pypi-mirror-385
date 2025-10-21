# Phase 8.0 Migration Guide

## Overview

Phase 8.0 integrates **Core v1.1.0 contracts** into `market-data-pipeline v0.9.0`, bringing standardized DTOs and protocols for telemetry, feedback, and rate control across the entire market data system.

**Guiding Principle**: Contracts-first. All feedback and rate control now uses Core DTOs (`FeedbackEvent`, `RateAdjustment`, `BackpressureLevel`) and protocols (`RateController`, `FeedbackPublisher`).

---

## What Changed?

### Core Dependency Added

**Before (Phase 6.0)**:
```toml
# pyproject.toml - No Core dependency
dependencies = [
    "pydantic>=2.0.0",
    # ...
]
```

**After (Phase 8.0)**:
```toml
dependencies = [
    "market-data-core>=1.1.0",  # ✅ Core contracts now imported
    "pydantic>=2.0.0",
    # ...
]
```

---

## Breaking Changes & Migration Paths

### 1. FeedbackEvent → Core DTO

**Old Code (Phase 6.0)**:
```python
# Custom duck-typed event
class FeedbackEvent:
    def __init__(self, level: str, queue_size: int, capacity: int):
        self.level = MockLevel(level)  # String-based
        self.queue_size = queue_size
        self.capacity = capacity
```

**New Code (Phase 8.0)**:
```python
from market_data_core.telemetry import FeedbackEvent, BackpressureLevel
import time

# Core DTO with strict enum
event = FeedbackEvent(
    coordinator_id="store_01",
    queue_size=800,
    capacity=1000,
    level=BackpressureLevel.soft,  # ✅ Enum, not string
    source="store",
    ts=time.time()
)
```

**Migration Steps**:
1. Replace custom `FeedbackEvent` with `from market_data_core.telemetry import FeedbackEvent`
2. Change `level="soft"` (string) → `level=BackpressureLevel.soft` (enum)
3. Add `coordinator_id`, `source`, and `ts` fields

---

### 2. BackpressureLevel → Enum (no more strings)

**Old Code (Phase 6.0)**:
```python
# String-based level matching
if event.level.value.lower() == "soft":
    scale = 0.5
elif event.level.value.lower() == "hard":
    scale = 0.0
```

**New Code (Phase 8.0)**:
```python
from market_data_core.telemetry import BackpressureLevel

# Enum comparison (type-safe)
if event.level == BackpressureLevel.soft:
    scale = 0.5
elif event.level == BackpressureLevel.hard:
    scale = 0.0
```

**Migration Steps**:
1. Replace all string comparisons (`"soft"`, `"hard"`, `"ok"`) with enum members
2. Use `BackpressureLevel.soft.value` if you need the string representation

---

### 3. Policy Mapping → Enum Keys

**Old Code (Phase 6.0)**:
```python
# Settings returned dict with string keys
policy = {
    "ok": 1.0,
    "soft": 0.5,
    "hard": 0.0
}
```

**New Code (Phase 8.0)**:
```python
from market_data_core.telemetry import BackpressureLevel

# Settings now returns dict with enum keys
policy = {
    BackpressureLevel.ok: 1.0,
    BackpressureLevel.soft: 0.5,
    BackpressureLevel.hard: 0.0
}
```

**Backward Compatibility**:
```python
# Phase 8.0 FeedbackHandler accepts BOTH formats:
legacy_policy = {"ok": 1.0, "soft": 0.75, "hard": 0.25}  # ✅ Still works
modern_policy = {BackpressureLevel.ok: 1.0, ...}          # ✅ Preferred
```

---

### 4. RateAdjustment → Core DTO

**Old Code (Phase 6.0)**:
```python
# Implicit scaling via set_budget_scale()
await rate_coordinator.set_budget_scale(provider="ibkr", scale=0.5)
await rate_coordinator.set_global_pressure(provider="ibkr", level="soft")
```

**New Code (Phase 8.0)**:
```python
from market_data_core.telemetry import RateAdjustment, BackpressureLevel
import time

# Explicit RateAdjustment DTO
adjustment = RateAdjustment(
    provider="ibkr",
    scale=0.5,
    reason=BackpressureLevel.soft,  # ✅ Enum reason
    ts=time.time()
)
await rate_controller.apply(adjustment)  # Core protocol method
```

---

### 5. RateController Protocol Adoption

**Old Code (Phase 6.0)**:
```python
# RateCoordinator used directly
handler = FeedbackHandler(rate=rate_coordinator, provider="ibkr")
```

**New Code (Phase 8.0)**:
```python
from market_data_pipeline.orchestration.feedback import (
    FeedbackHandler,
    RateCoordinatorAdapter  # ✅ Adapter wraps legacy coordinator
)

# Wrap coordinator to implement Core RateController protocol
adapter = RateCoordinatorAdapter(rate_coordinator)
handler = FeedbackHandler(rate=adapter, provider="ibkr")
```

**Why the adapter?**
- `RateCoordinator` (Phase 6.0) uses `set_budget_scale(provider, scale)`
- Core `RateController` protocol expects `apply(adjustment: RateAdjustment)`
- `RateCoordinatorAdapter` bridges the two interfaces

---

### 6. FeedbackHandler Signature Change

**Old Code (Phase 6.0)**:
```python
async def handle(self, event: dict | Any) -> None:
    """Handle any dict-like event."""
    level = event.get("level") or event.level.value
```

**New Code (Phase 8.0)**:
```python
async def handle(self, event: FeedbackEvent) -> None:
    """Handle Core FeedbackEvent DTO only."""
    level = event.level  # BackpressureLevel enum
```

**Migration**: Update all event publishers to send Core `FeedbackEvent` DTOs.

---

### 7. Metrics Labels → Enum Values

**Old Code (Phase 6.0)**:
```python
# Label used lowercase string
rate_adj_counter.labels(provider="ibkr", reason="soft").inc()
```

**New Code (Phase 8.0)**:
```python
from market_data_core.telemetry import RateAdjustment

# Label uses enum.value
adj = RateAdjustment(...)
rate_adj_counter.labels(provider=adj.provider, reason=adj.reason.value).inc()
```

**Impact**: Prometheus label values remain strings (`"ok"`, `"soft"`, `"hard"`) so **dashboards are unchanged**.

---

## UnifiedRuntime Integration

**Automatic Migration**: If you use `UnifiedRuntime` with feedback enabled, **no code changes needed**! Phase 8.0 internally wraps the coordinator with the adapter.

**Before & After (no changes)**:
```python
settings = UnifiedRuntimeSettings(
    mode="dag",
    dag={"graph": {...}},
    feedback={
        "enable_feedback": True,
        "provider_name": "ibkr"
    }
)

async with UnifiedRuntime(settings) as rt:
    await rt.run()  # ✅ Works in both Phase 6.0 and 8.0
```

---

## Testing Migration

### Unit Tests

**Old Approach (Phase 6.0)**:
```python
class MockFeedbackEvent:
    def __init__(self, level: str):
        self.level = MockLevel(level)

event = MockFeedbackEvent("soft")
```

**New Approach (Phase 8.0)**:
```python
from market_data_core.telemetry import FeedbackEvent, BackpressureLevel
import time

event = FeedbackEvent(
    coordinator_id="test",
    queue_size=500,
    capacity=1000,
    level=BackpressureLevel.soft,
    source="test",
    ts=time.time()
)
```

### Protocol Conformance Tests

**New in Phase 8.0**:
```python
from market_data_core.protocols import RateController, FeedbackPublisher

def test_adapter_implements_protocol():
    adapter = RateCoordinatorAdapter(coordinator)
    assert isinstance(adapter, RateController)  # ✅ Protocol check

def test_bus_implements_protocol():
    bus = FeedbackBus()
    assert isinstance(bus, FeedbackPublisher)  # ✅ Protocol check
```

---

## Deprecation Timeline

| Component | Status | Removal |
|-----------|--------|---------|
| String-based `level` comparisons | ⚠️ Deprecated | v0.10.0 |
| Dict-based `FeedbackEvent` | ⚠️ Deprecated | v0.10.0 |
| Direct `RateCoordinator` without adapter | ⚠️ Deprecated | v0.10.0 |
| `set_budget_scale()` / `set_global_pressure()` | ✅ Kept for backward compat | — |

---

## Troubleshooting

### Error: `'str' object has no attribute 'value'`

**Cause**: Mixing string levels with enum comparisons.

**Fix**:
```python
# ❌ Old
if event.level == "soft":

# ✅ New
from market_data_core.telemetry import BackpressureLevel
if event.level == BackpressureLevel.soft:
```

---

### Error: `'RateCoordinator' object has no attribute 'apply'`

**Cause**: Passing `RateCoordinator` directly to `FeedbackHandler`.

**Fix**:
```python
# ❌ Old
handler = FeedbackHandler(rate=rate_coordinator, ...)

# ✅ New
from market_data_pipeline.orchestration.feedback import RateCoordinatorAdapter
adapter = RateCoordinatorAdapter(rate_coordinator)
handler = FeedbackHandler(rate=adapter, ...)
```

---

### Error: `TypeError: __init__() got an unexpected keyword argument 'coordinator_id'`

**Cause**: Using old custom `FeedbackEvent` instead of Core DTO.

**Fix**:
```python
# ❌ Old
from my_custom_module import FeedbackEvent

# ✅ New
from market_data_core.telemetry import FeedbackEvent
```

---

## Rollout Checklist

- [ ] Install `market-data-core>=1.1.0`
- [ ] Update imports: `from market_data_core.telemetry import FeedbackEvent, BackpressureLevel, RateAdjustment`
- [ ] Replace string levels with enums: `"soft"` → `BackpressureLevel.soft`
- [ ] Wrap `RateCoordinator` with `RateCoordinatorAdapter` where needed
- [ ] Update tests to use Core DTOs
- [ ] Verify Prometheus metrics labels unchanged
- [ ] Run full test suite: `pytest -q --maxfail=1`
- [ ] Deploy Store → Pipeline → Orchestrator (in order)

---

## Benefits

✅ **Type Safety**: Enums prevent typos (`"Soft"` vs `"soft"`)  
✅ **Cross-Repo Consistency**: All repos speak the same language  
✅ **Protocol Compliance**: `isinstance(adapter, RateController)` enables duck typing  
✅ **JSON Roundtrip**: Core DTOs serialize/deserialize cleanly  
✅ **Testability**: Mock Core protocols instead of concrete classes  
✅ **Future-Proof**: Core contracts evolve independently of implementations  

---

## Questions?

See also:
- `PHASE_8.0_IMPLEMENTATION_COMPLETE.md` for technical details
- `CHANGELOG.md` for release notes
- Core v1.1.0 documentation for DTO schemas

