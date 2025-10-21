# Phase 5.0 Streaming DAG Runtime - Evaluation & Implementation Plan

**Date**: 2024-10-15  
**Current Version**: v0.8.0 (Phase 3.0 complete)  
**Target Version**: v0.9.0 (Phase 5.0)  
**Status**: PLANNING - DO NOT IMPLEMENT YET

---

## Executive Summary

### Proposal Overview
Transform `market_data_pipeline` into a first-class streaming DAG engine that composes providers → operators → sinks, with autoscaling hooks and backpressure feedback from `market_data_store`.

### Complexity Assessment
- **Scope**: Large architectural enhancement
- **Risk Level**: Medium-High
- **Estimated Effort**: 40-60 hours development + 15-20 hours testing
- **Breaking Changes**: None (opt-in design)
- **Dependencies**: `market_data_core`, `market_data_store` v0.9.0+

### Viability Score: **8.5/10** ✅ VIABLE

**Strengths**:
- ✅ Well-architected design with clear separation of concerns
- ✅ Opt-in approach maintains backward compatibility
- ✅ Leverages existing Phase 3.0 orchestration infrastructure
- ✅ Complete scaffolding provided
- ✅ Aligns with existing async/streaming patterns

**Concerns**:
- ⚠️ External dependencies on `market_data_core` and `market_data_store` v0.9.0
- ⚠️ Overlaps with existing `orchestration/` package (needs clear delineation)
- ⚠️ Missing dependency: `mmh3` (for hash partitioning)
- ⚠️ Missing dependency: `loguru` (used in examples)
- ⚠️ Examples reference unreleased `market_data_store` v0.9.0 features

---

## 1. Architectural Compatibility Analysis

### 1.1 Current Architecture (v0.8.0)

```
StreamingPipeline (core)
├── Source (TickSource protocol)
├── Operator (transform/aggregate)
├── Batcher (flow control)
└── Sink (persistence)

orchestration/ (Phase 3.0)
├── SourceRegistry
├── SourceRouter (implements TickSource)
├── RateCoordinator
├── CircuitBreaker
└── PipelineRuntime
```

### 1.2 Proposed Architecture (v0.9.0)

```
DAG Runtime (new)
├── dag/
│   ├── nodes.py (SourceNode, TransformNode, SinkNode protocols)
│   ├── graph.py (Dag model, validation)
│   ├── runtime.py (DagRuntime scheduler)
│   ├── edges.py (Channel, partitioners)
│   ├── windowing.py (TumblingWindowAssigner)
│   └── partitions.py (hash_partition)
├── adapters/
│   ├── provider_source.py (wraps MarketDataProvider)
│   └── sink_adapter.py (wraps WriteCoordinator)
└── contrib/operators/
    ├── dedupe.py
    ├── throttle.py
    └── router.py
```

### 1.3 Integration Points

| Component | Existing | Phase 5.0 | Relationship |
|-----------|----------|-----------|--------------|
| `StreamingPipeline` | ✅ Core | ⚪ Unchanged | DAG nodes can wrap pipeline |
| `TickSource` | ✅ Protocol | ✅ `SourceNode` | Similar protocols, compatible |
| `Operator` | ✅ Transform | ✅ `TransformNode` | DAG nodes more generic |
| `Sink` | ✅ Batch writes | ✅ `SinkNode` | Compatible interfaces |
| `orchestration.SourceRouter` | ✅ Phase 3.0 | ✅ Can be DAG node | Already compatible |
| `orchestration.PipelineRuntime` | ✅ Phase 3.0 | ⚠️ Overlap | Needs clarification |
| `Batcher` | ✅ Flow control | ✅ In DAG edges | Different layer |

### 1.4 Potential Conflicts

#### ⚠️ **ISSUE 1: Dual Runtime APIs**

**Problem**: 
- Existing: `orchestration.PipelineRuntime` (Phase 3.0)
- Proposed: `dag.DagRuntime` + `orchestration.runtime_api.DAGRuntimeAPI` (Phase 5.0)

**Resolution**:
- **Option A** (Recommended): Merge into single `orchestration.PipelineRuntime` with DAG support
- **Option B**: Keep separate, rename `orchestration.PipelineRuntime` → `LegacyPipelineRuntime`
- **Option C**: New `orchestration.runtime_api.DAGRuntimeAPI` becomes the high-level API

**Recommendation**: **Option A** - Enhance existing `PipelineRuntime` with DAG capabilities.

#### ⚠️ **ISSUE 2: Overlapping Settings**

**Problem**:
- Existing: `orchestration.runtime.PipelineRuntimeSettings`
- Proposed: `orchestration.settings.DagRuntimeSettings`

**Resolution**: Merge into unified settings hierarchy.

#### ⚠️ **ISSUE 3: Protocol Duplication**

**Problem**:
- `TickSource` vs `SourceNode` (similar but not identical)
- `Operator` vs `TransformNode` (different signatures)
- `Sink` vs `SinkNode` (batch vs sequence)

**Resolution**: Create adapter layer to bridge protocols.

---

## 2. Dependency Analysis

### 2.1 Required New Dependencies

```toml
# pyproject.toml additions needed:

[project.dependencies]
# ... existing ...
"loguru>=0.7.0",       # Used in dag/runtime.py
"mmh3>=4.0.0",         # Used in dag/partitions.py
```

### 2.2 External Package Dependencies

| Package | Version | Status | Risk |
|---------|---------|--------|------|
| `market_data_core` | Any | ⚠️ Optional | Medium - May not exist |
| `market_data_store` | v0.9.0+ | ⚠️ Required | **HIGH** - Unreleased |
| `market_data_ibkr` | Any | ⚠️ Optional | Medium - May not exist |

**Critical Dependency Issue**:
```python
# examples/dag_realtime_bars.py imports unreleased packages:
from market_data_core import Instrument
from market_data_ibkr import IBKRProvider, IBKRSettings
from market_data_store.coordinator.write_coordinator import WriteCoordinator
```

**Resolution**:
1. Make examples conditional (check imports)
2. Add stubs/mocks for development
3. Document external dependencies clearly
4. Add integration tests that skip if dependencies unavailable

### 2.3 Current Import Patterns

The codebase already uses optional imports in some places:

```python
# src/market_data_pipeline/source/ibkr.py
async def start(self) -> None:
    # TODO: Initialize IBKR connection via market_data_core
    # This will use market_data_core.ibkr or similar
```

**Recommendation**: Follow same pattern for Phase 5.0.

---

## 3. Code Quality & Standards

### 3.1 Provided Scaffolding Analysis

✅ **Strengths**:
- Complete type hints with Protocols and Generics
- Comprehensive docstrings
- Prometheus metrics integration
- AsyncIterator patterns match existing code
- Clean dataclass usage

⚠️ **Issues**:

1. **Missing Type Annotations** (minor):
   ```python
   # dag/windowing.py:21
   def add(self, item: Any) -> list[Window]:  # Should be List[Window] for 3.11
   ```

2. **Inconsistent Logging**:
   - Proposed code uses `loguru.logger`
   - Existing code uses `logging.getLogger(__name__)`
   
   **Fix**: Standardize on Python's `logging` module for consistency.

3. **Import Issues**:
   ```python
   # dag/partitions.py
   import mmh3  # Not in dependencies
   ```

4. **Incomplete Implementations**:
   ```python
   # dag/runtime.py:43 - _run_node is a mock placeholder
   async def _run_node(self, node_id: str, node):
       """Placeholder execution loop per node (mock)."""
       while self._running:
           NODE_QUEUE_DEPTH.labels(node=node_id).set(0)
           RUNTIME_LOOP_ITERATIONS.inc()
           await asyncio.sleep(0.5)
   ```

### 3.2 Testing Requirements

**Minimum Test Coverage**:
- [ ] `dag/nodes.py` - Protocol compliance tests
- [ ] `dag/edges.py` - Channel backpressure tests
- [ ] `dag/graph.py` - Cycle detection, validation
- [ ] `dag/runtime.py` - Start/stop, error handling
- [ ] `dag/windowing.py` - Window assignment logic
- [ ] `dag/partitions.py` - Hash distribution
- [ ] `adapters/` - Integration with external packages
- [ ] `contrib/operators/` - Deduplication, throttling
- [ ] `orchestration/runtime_api.py` - High-level API

**Estimated Test Suite**: ~40-50 new tests

### 3.3 Linting & Type Checking

**Current Standards** (from pyproject.toml):
```toml
[tool.ruff]
target-version = "py311"
line-length = 88
# 38 rule categories enabled

[tool.mypy]
disallow_untyped_defs = true
disallow_incomplete_defs = true
strict_equality = true
```

**Phase 5.0 Compliance**:
- ✅ Type hints present (needs minor fixes)
- ⚠️ Some `Any` types (acceptable for generic framework)
- ✅ No obvious linting violations
- ⚠️ Incomplete implementations will fail `warn_unreachable`

---

## 4. Implementation Plan

### Phase 5.0.1 - Foundation (Week 1: 15-20 hours)

**Goals**: Core DAG infrastructure without external dependencies

**Tasks**:
1. ✅ Add dependencies to `pyproject.toml`
   - `loguru>=0.7.0`
   - `mmh3>=4.0.0`
   
2. ✅ Create `dag/` package structure
   - `nodes.py` - Protocols and base classes
   - `edges.py` - Channel with backpressure
   - `graph.py` - DAG model and validation
   - `metrics.py` - Prometheus instrumentation
   
3. ✅ Implement core runtime
   - `dag/runtime.py` - Basic scheduler (replace mock)
   - Start/stop lifecycle
   - Error handling
   - Graceful shutdown

4. ✅ Fix logging consistency
   - Replace `loguru` with `logging` module
   - Match existing patterns

5. ✅ Unit tests for core DAG
   - Graph validation (acyclicity)
   - Channel backpressure
   - Runtime lifecycle
   
**Deliverables**:
- Working `DagRuntime` that executes simple graphs
- 15-20 tests passing
- No external dependencies yet

---

### Phase 5.0.2 - Windowing & Partitioning (Week 2: 10-15 hours)

**Goals**: Add stateful operators and partitioning

**Tasks**:
1. ✅ Implement windowing
   - `dag/windowing.py` - TumblingWindowAssigner
   - Event-time watermarks
   - Late data handling
   
2. ✅ Implement partitioning
   - `dag/partitions.py` - Hash-based partitioning
   - Consistent hashing
   - Keyed state

3. ✅ Unit tests
   - Window assignment logic
   - Partition distribution
   - Late event handling

**Deliverables**:
- Working window operators
- Stateful processing
- 10-15 additional tests

---

### Phase 5.0.3 - Contrib Operators (Week 2: 8-10 hours)

**Goals**: Reusable streaming operators

**Tasks**:
1. ✅ Implement operators
   - `contrib/operators/dedupe.py` - Deduplication
   - `contrib/operators/throttle.py` - Rate limiting
   - `contrib/operators/router.py` - Fan-out routing
   - `contrib/operators/ohlc_resample.py` - Bar resampling (stub)

2. ✅ Unit tests for each operator

**Deliverables**:
- 4 working operators
- 8-12 additional tests

---

### Phase 5.0.4 - Adapters (Week 3: 12-15 hours)

**Goals**: Integration with external packages (optional)

**Tasks**:
1. ✅ Create adapter stubs
   - `adapters/provider_source.py` - Mock MarketDataProvider
   - `adapters/sink_adapter.py` - Mock WriteCoordinator
   - `adapters/serialization.py` - JSON/msgpack serialization

2. ✅ Conditional imports
   ```python
   try:
       from market_data_core import MarketDataProvider
   except ImportError:
       MarketDataProvider = None  # Use stub
   ```

3. ✅ Integration tests (skip if unavailable)
   - Mark with `pytest.mark.integration`
   - Skip if external packages missing

**Deliverables**:
- Adapter layer for external integration
- Graceful degradation when packages unavailable
- 5-8 integration tests (may skip)

---

### Phase 5.0.5 - High-Level API (Week 3: 8-10 hours)

**Goals**: Unified orchestration API

**Tasks**:
1. ✅ Resolve runtime API overlap
   - Enhance `orchestration.PipelineRuntime` with DAG support
   - Or create new `orchestration.DAGRuntimeAPI`
   
2. ✅ Merge settings
   - Unified `PipelineRuntimeSettings` + `DagRuntimeSettings`
   
3. ✅ Update documentation
   - `docs/DAG_RUNTIME.md` - Architecture guide
   - `docs/MIGRATION_PHASE5.md` - Migration guide
   - Update main `README.md`

**Deliverables**:
- Clean high-level API
- Comprehensive documentation
- Migration guide

---

### Phase 5.0.6 - Examples & Polish (Week 4: 5-8 hours)

**Goals**: Working examples and final polish

**Tasks**:
1. ✅ Create runnable examples
   - `examples/dag_simple.py` - Basic DAG (no external deps)
   - `examples/dag_windowed.py` - Windowing example
   - `examples/dag_realtime_bars.py` - Full example (conditional)

2. ✅ Polish code
   - Fix type hints (list → List for 3.11)
   - Complete docstrings
   - Remove TODOs/FIXMEs

3. ✅ Final testing
   - Run full test suite
   - Check coverage (target: 85%+)
   - Linting and type checking

**Deliverables**:
- 3+ working examples
- All tests passing
- Documentation complete

---

### Phase 5.0.7 - Backpressure Integration (Week 4: 8-10 hours)

**Goals**: Connect to `market_data_store` backpressure signals

**Tasks**:
1. ✅ Design backpressure API
   - Polling vs push-based
   - Metrics to monitor
   - Throttling strategy

2. ✅ Implement coordinator integration
   ```python
   # Pseudo-code
   async def check_backpressure(self):
       metrics = await self.coordinator.get_metrics()
       if metrics.queue_depth > self.high_watermark:
           await self.slow_down()
   ```

3. ✅ Add autoscaling metrics
   - KEDA-compatible Prometheus metrics
   - HPA-friendly gauges

**Deliverables**:
- Backpressure feedback loop
- Autoscaling metrics
- Integration tests

---

## 5. Testing Strategy

### 5.1 Test Structure

```
tests/
├── unit/
│   ├── dag/
│   │   ├── test_nodes.py
│   │   ├── test_edges.py
│   │   ├── test_graph.py
│   │   ├── test_runtime.py
│   │   ├── test_windowing.py
│   │   └── test_partitions.py
│   ├── adapters/
│   │   ├── test_provider_source.py
│   │   ├── test_sink_adapter.py
│   │   └── test_serialization.py
│   └── contrib/
│       ├── test_dedupe.py
│       ├── test_throttle.py
│       └── test_router.py
├── integration/
│   ├── test_dag_e2e.py
│   ├── test_dag_with_store.py  # Skip if unavailable
│   └── test_dag_backpressure.py
└── examples/
    └── test_examples_run.py  # Smoke tests
```

### 5.2 Test Coverage Goals

| Component | Target Coverage | Priority |
|-----------|----------------|----------|
| `dag/graph.py` | 95%+ | High |
| `dag/runtime.py` | 90%+ | High |
| `dag/edges.py` | 90%+ | High |
| `dag/windowing.py` | 85%+ | Medium |
| `dag/partitions.py` | 85%+ | Medium |
| `contrib/operators/` | 80%+ | Medium |
| `adapters/` | 75%+ | Low (external deps) |

### 5.3 Backward Compatibility Tests

**Critical**: All 123 existing tests must pass!

```bash
# Run before starting Phase 5.0
pytest tests/unit/ -q
# Expected: 123 passed

# Run after each sub-phase
pytest tests/ -q
# Expected: 123+ passed (no failures)
```

---

## 6. Risk Assessment & Mitigation

### 6.1 High Risks

#### 🔴 **RISK 1: External Dependencies**

**Risk**: Examples depend on unreleased `market_data_store` v0.9.0

**Impact**: High - Cannot test integration features  
**Probability**: High - Dependencies not in repo

**Mitigation**:
1. Create stubs/mocks for development
2. Make integration tests conditional
3. Document dependency versions clearly
4. Add CI skip conditions

**Status**: Manageable with conditional imports

---

#### 🟡 **RISK 2: API Confusion**

**Risk**: Two runtime APIs (`PipelineRuntime` vs `DagRuntime`)

**Impact**: Medium - User confusion  
**Probability**: High - Already present in design

**Mitigation**:
1. Merge into single API (recommended)
2. Clear documentation on which to use
3. Deprecation path if needed

**Status**: Requires design decision

---

#### 🟡 **RISK 3: Incomplete Implementations**

**Risk**: Scaffolding has placeholder code (e.g., `_run_node`)

**Impact**: High - Won't work without completion  
**Probability**: Medium - Needs significant work

**Mitigation**:
1. Incremental implementation plan
2. Clear TODOs marked
3. Comprehensive testing

**Status**: Expected, plan accounts for this

---

### 6.2 Medium Risks

#### 🟡 **RISK 4: Performance**

**Risk**: DAG overhead vs direct pipeline

**Impact**: Medium - May affect latency  
**Probability**: Medium

**Mitigation**:
1. Benchmark against existing pipeline
2. Optimize hot paths
3. Make DAG opt-in

---

#### 🟡 **RISK 5: Complexity**

**Risk**: Increased codebase complexity

**Impact**: Medium - Maintenance burden  
**Probability**: High

**Mitigation**:
1. Comprehensive documentation
2. Clear separation of concerns
3. Gradual adoption path

---

## 7. Success Criteria

### 7.1 Must-Have (Phase 5.0 Blocker)

- [ ] All 123 existing tests pass (backward compatibility)
- [ ] Core DAG runtime executes simple graphs
- [ ] Graph validation prevents cycles
- [ ] Channel backpressure works
- [ ] 40+ new tests passing
- [ ] Documentation complete
- [ ] No new linter/type errors

### 7.2 Should-Have (Phase 5.0 Complete)

- [ ] Windowing operators work
- [ ] Partitioning works
- [ ] 4+ contrib operators implemented
- [ ] 60+ new tests passing
- [ ] 1+ runnable example (no external deps)
- [ ] Performance benchmarks

### 7.3 Nice-to-Have (Phase 5.1+)

- [ ] Integration with `market_data_store` v0.9.0
- [ ] Backpressure feedback working
- [ ] Autoscaling metrics exposed
- [ ] 3+ runnable examples
- [ ] Advanced operators (OHLC resample)

---

## 8. Recommendations

### 8.1 Proceed with Modifications ✅

**Verdict**: **APPROVED** with following changes:

1. **Resolve API Overlap**
   - Decision needed: Merge or separate runtime APIs
   - Recommendation: Merge into enhanced `PipelineRuntime`

2. **Add Missing Dependencies**
   ```toml
   "loguru>=0.7.0",
   "mmh3>=4.0.0",
   ```

3. **Fix Logging Consistency**
   - Replace `loguru` with standard `logging` module
   - Match existing patterns

4. **Make Adapters Optional**
   - Conditional imports with graceful fallbacks
   - Stubs for missing packages

5. **Complete Implementations**
   - Replace mock/placeholder code
   - Follow incremental plan

6. **Version Bump**
   - Update `__version__` to "0.9.0"
   - Update `pyproject.toml` version

### 8.2 Implementation Order

**Phase 1** (Immediate):
1. Add dependencies
2. Create stubs for external packages
3. Implement core `dag/` package (no adapters)

**Phase 2** (Week 2):
4. Windowing & partitioning
5. Contrib operators

**Phase 3** (Week 3):
6. Adapter layer (with conditional imports)
7. High-level API integration

**Phase 4** (Week 4):
8. Examples and documentation
9. Backpressure integration (if deps available)

### 8.3 Documentation Requirements

Create/update these files:

1. **`docs/DAG_RUNTIME.md`** - Architecture and usage
2. **`docs/PHASE_5_MIGRATION.md`** - Migration guide
3. **`README_PHASE5.md`** - Quick start (as suggested)
4. **`CHANGELOG.md`** - Version 0.9.0 entry
5. **Update `README.md`** - Add Phase 5.0 section
6. **`examples/README.md`** - Example descriptions

---

## 9. Pre-Implementation Checklist

Before starting implementation:

- [ ] ✅ Virtual environment activated
- [ ] Decision made on runtime API strategy
- [ ] Dependencies added to `pyproject.toml`
- [ ] Existing tests pass (123/123)
- [ ] Git branch created (`git checkout -b phase-5.0-dag-runtime`)
- [ ] This plan reviewed and approved
- [ ] External dependency strategy confirmed

---

## 10. Timeline Estimate

| Phase | Duration | Tasks | Tests |
|-------|----------|-------|-------|
| 5.0.1 Foundation | 15-20h | Core DAG | +15-20 |
| 5.0.2 Windowing | 10-15h | Windows, partitions | +10-15 |
| 5.0.3 Operators | 8-10h | Contrib operators | +8-12 |
| 5.0.4 Adapters | 12-15h | External integration | +5-8 |
| 5.0.5 API | 8-10h | High-level API | +5 |
| 5.0.6 Examples | 5-8h | Examples, polish | +3 |
| 5.0.7 Backpressure | 8-10h | Store integration | +5 |
| **TOTAL** | **66-88h** | ~30 files | **+51-68** |

**Calendar Time**: 3-4 weeks (2 hours/day) or 1.5-2 weeks (full-time)

---

## 11. Conclusion

### Final Verdict: ✅ **APPROVED - PROCEED WITH CAUTION**

**Viability**: **8.5/10**

**Strengths**:
- Well-designed architecture
- Complete scaffolding provided
- Opt-in approach (backward compatible)
- Builds on Phase 3.0 foundation
- Clear business value

**Required Actions**:
1. Resolve runtime API overlap
2. Add missing dependencies
3. Implement placeholder code
4. Create conditional import strategy
5. Complete comprehensive testing

**Timeline**: 3-4 weeks with careful execution

**Risk Level**: Medium - Manageable with proper planning

### Next Steps

1. **Review this plan** with stakeholders
2. **Make API decision** (runtime overlap)
3. **Create feature branch** (`phase-5.0-dag-runtime`)
4. **Begin Phase 5.0.1** (Foundation)

---

**Author**: AI Code Assistant  
**Date**: 2024-10-15  
**Version**: 1.0  
**Status**: AWAITING APPROVAL

