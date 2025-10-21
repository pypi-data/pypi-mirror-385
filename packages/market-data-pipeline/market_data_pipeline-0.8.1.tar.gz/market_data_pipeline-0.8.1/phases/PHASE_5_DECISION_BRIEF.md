# Phase 5.0 - Executive Decision Brief

**Status**: 🟡 NEEDS DECISIONS BEFORE PROCEEDING  
**Viability**: ✅ 8.5/10 - APPROVED WITH MODIFICATIONS  
**Timeline**: 3-4 weeks (66-88 hours)  

---

## 🎯 Quick Decision Summary

### ✅ GREEN LIGHT - Proceed As Planned
- Core DAG architecture is sound
- Opt-in design maintains backward compatibility
- Scaffolding is high quality
- Builds naturally on Phase 3.0
- Clear value proposition

### ⚠️ DECISIONS REQUIRED

#### **DECISION 1: Runtime API Strategy** 🔴 BLOCKER

**Context**: Overlap between existing and proposed runtime APIs

Current State:
```python
# Phase 3.0 (existing)
from market_data_pipeline.orchestration import PipelineRuntime

# Phase 5.0 (proposed)
from market_data_pipeline.dag.runtime import DagRuntime
from market_data_pipeline.orchestration.runtime_api import DAGRuntimeAPI
```

**Options**:

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **A: Merge APIs** | Clean, unified | More work | ⭐ **RECOMMENDED** |
| **B: Keep Separate** | Faster | Confusing | ❌ Not recommended |
| **C: Deprecate Old** | Clean break | Breaking change | ❌ Breaks promise |

**Recommendation**: **Option A**
- Enhance existing `orchestration.PipelineRuntime` to support DAG mode
- Add `runtime.create_dag()` method
- Single API, multiple modes

**Action**: Choose option before starting implementation

---

#### **DECISION 2: External Dependencies** 🟡 IMPORTANT

**Context**: Examples require unreleased packages

```python
from market_data_core import MarketDataProvider        # Not available
from market_data_store.coordinator import WriteCoordinator  # v0.9.0 unreleased
from market_data_ibkr import IBKRProvider             # Not available
```

**Options**:

| Option | Pros | Cons |
|--------|------|------|
| **A: Stub Everything** | Works now | Less real-world testing |
| **B: Wait for Deps** | Full integration | Delays Phase 5.0 |
| **C: Hybrid** | Best of both | More complex |

**Recommendation**: **Option C (Hybrid)**
```python
try:
    from market_data_core import MarketDataProvider
    HAS_CORE = True
except ImportError:
    HAS_CORE = False
    MarketDataProvider = None  # Stub

# Tests skip if not available
@pytest.mark.skipif(not HAS_CORE, reason="market_data_core not installed")
def test_provider_integration():
    ...
```

**Action**: Implement conditional imports with graceful degradation

---

#### **DECISION 3: Logging Library** 🟢 MINOR

**Context**: Inconsistent logging approach

Current:
```python
import logging
logger = logging.getLogger(__name__)
```

Proposed:
```python
from loguru import logger
```

**Recommendation**: **Use existing `logging` module**
- Consistency with codebase
- No new dependency
- Standard library

**Action**: Replace `loguru` with `logging` in provided code

---

### 🔧 Required Modifications

#### 1. Add Dependencies to `pyproject.toml`
```toml
[project.dependencies]
# ... existing ...
"mmh3>=4.0.0",         # Hash partitioning (NEW)

# Note: loguru NOT added - using standard logging instead
```

#### 2. Fix Type Hints for Python 3.11
```python
# Before
def add(self, item: Any) -> list[Window]:

# After
from typing import List
def add(self, item: Any) -> List[Window]:
```

#### 3. Complete Placeholder Implementations

Replace mocks in:
- `dag/runtime.py:_run_node()` - Core execution loop
- `contrib/operators/ohlc_resample.py` - Empty placeholder

---

## 📊 Risk Dashboard

| Risk | Severity | Probability | Mitigation Status |
|------|----------|-------------|-------------------|
| External dependencies unavailable | 🔴 High | 🔴 High | ✅ Plan ready |
| API confusion (dual runtimes) | 🟡 Med | 🔴 High | ⚠️ Needs decision |
| Incomplete implementations | 🟡 Med | 🟡 Med | ✅ Plan ready |
| Performance regression | 🟢 Low | 🟡 Med | ✅ Opt-in design |
| Breaking existing tests | 🔴 High | 🟢 Low | ✅ Opt-in design |

**Overall Risk**: 🟡 **MEDIUM** - Manageable with proper execution

---

## 📅 Implementation Phases

### Phase 5.0.1 - Foundation (Week 1)
**Goal**: Core DAG without external dependencies  
**Hours**: 15-20  
**Tests**: +15-20  
**Deliverable**: Working `DagRuntime` for simple graphs

### Phase 5.0.2 - Windowing (Week 2)
**Goal**: Stateful operations  
**Hours**: 10-15  
**Tests**: +10-15  
**Deliverable**: Window operators and partitioning

### Phase 5.0.3 - Operators (Week 2)
**Goal**: Reusable streaming operators  
**Hours**: 8-10  
**Tests**: +8-12  
**Deliverable**: Dedupe, throttle, router, resample

### Phase 5.0.4 - Adapters (Week 3)
**Goal**: External integration (optional)  
**Hours**: 12-15  
**Tests**: +5-8  
**Deliverable**: Conditional adapters for store/core

### Phase 5.0.5 - API (Week 3)
**Goal**: Unified high-level API  
**Hours**: 8-10  
**Tests**: +5  
**Deliverable**: Clean public API, docs

### Phase 5.0.6 - Examples (Week 4)
**Goal**: Working examples  
**Hours**: 5-8  
**Tests**: +3  
**Deliverable**: 3+ runnable examples

### Phase 5.0.7 - Backpressure (Week 4)
**Goal**: Store integration  
**Hours**: 8-10  
**Tests**: +5  
**Deliverable**: Backpressure feedback, autoscaling metrics

**TOTAL**: 66-88 hours over 3-4 weeks

---

## ✅ Success Criteria

### Phase 5.0 MVP (Must Have)
- [ ] All 123 existing tests pass (**CRITICAL**)
- [ ] Core DAG executes simple graphs
- [ ] Cycle detection works
- [ ] Channel backpressure works
- [ ] 40+ new tests passing
- [ ] No external dependencies required for core
- [ ] Documentation complete
- [ ] Zero linter/type errors

### Phase 5.0 Complete (Should Have)
- [ ] Windowing operators work
- [ ] 4+ contrib operators implemented
- [ ] 60+ new tests passing
- [ ] 1+ runnable example (standalone)
- [ ] Performance benchmarks

### Phase 5.1+ (Nice to Have)
- [ ] Integration with `market_data_store` v0.9.0
- [ ] Backpressure feedback working
- [ ] 3+ integration examples

---

## 🚦 Pre-Flight Checklist

Before starting implementation:

- [ ] **DECISION 1** resolved (runtime API strategy)
- [ ] **DECISION 2** resolved (dependency handling)
- [ ] Virtual environment active
- [ ] All 123 existing tests pass
- [ ] Git branch created: `git checkout -b phase-5.0-dag-runtime`
- [ ] Dependencies added to `pyproject.toml`
- [ ] Team/stakeholders aligned
- [ ] This brief approved

---

## 📝 Recommended Actions

### Immediate (Today)
1. ✅ Virtual environment activated
2. ⚠️ **Make DECISION 1** (runtime API)
3. ⚠️ **Make DECISION 2** (dependencies)
4. Run existing tests: `pytest tests/unit/ -q`

### Before Implementation (Tomorrow)
5. Create feature branch
6. Update `pyproject.toml` with `mmh3`
7. Create stub files for external packages
8. Update version to "0.9.0-dev"

### Week 1
9. Begin Phase 5.0.1 (Foundation)
10. Daily test runs to catch regressions early

---

## 💡 Key Insights

### Why This Design Works
1. **Opt-in**: Doesn't break existing code
2. **Incremental**: Can ship parts independently
3. **Extensible**: Clean protocols for custom operators
4. **Observable**: Prometheus metrics throughout
5. **Tested**: Comprehensive test strategy

### Why This is Worth Doing
1. **Flexibility**: DAG > linear pipeline for complex flows
2. **Composability**: Mix and match operators easily
3. **Performance**: Better parallelization opportunities
4. **Autoscaling**: Direct KEDA/HPA integration
5. **Future-proof**: Foundation for Phase 6+ features

### What Could Go Wrong
1. **Dependency hell**: External packages unavailable
   - *Mitigation*: Conditional imports, stubs
2. **API confusion**: Two runtime APIs
   - *Mitigation*: Decision 1 resolution
3. **Complexity creep**: Too many abstractions
   - *Mitigation*: Keep core simple, extras in `contrib/`

---

## 🎯 Bottom Line

**Should we proceed?** ✅ **YES**

**Confidence Level**: **85%**

**Critical Path**:
1. Resolve runtime API decision (**BLOCKER**)
2. Implement core DAG (Phase 5.0.1)
3. Add windowing and operators
4. Integration layer (when deps available)

**Expected Outcome**: Production-ready streaming DAG engine that:
- Maintains 100% backward compatibility
- Provides clear upgrade path
- Enables advanced streaming patterns
- Sets foundation for autoscaling

**Recommended Start Date**: After DECISION 1 is made

---

**Prepared By**: AI Code Assistant  
**Date**: 2024-10-15  
**Version**: 1.0  
**Next Review**: After DECISION 1

