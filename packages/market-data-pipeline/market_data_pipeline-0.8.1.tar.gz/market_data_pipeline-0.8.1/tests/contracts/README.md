# Contract Tests

**Purpose**: Verify compatibility with `market-data-core` v1.1.0+ contracts.

---

## Overview

Contract tests ensure that `market_data_pipeline` remains compatible with
`market-data-core` protocol contracts and data transfer objects (DTOs).

These tests are:
- ✅ **Fast**: < 5 seconds locally, < 2 min in CI
- ✅ **Minimal**: Focus on critical compatibility checks only
- ✅ **Automated**: Triggered by Core when contracts change

---

## Test Files

### test_core_install.py
**What**: Verifies Core package can be imported and provides expected interfaces.

**Tests**:
- Import telemetry DTOs (FeedbackEvent, RateAdjustment, BackpressureLevel)
- Import protocols (RateController, FeedbackPublisher)
- Verify enum values (ok/soft/hard)
- Verify Pydantic models

**Fails When**: Core changes public API structure.

---

### test_feedback_flow.py
**What**: Tests FeedbackEvent → RateAdjustment transformation flow.

**Tests**:
- FeedbackEvent creation with v1.1.0 fields
- JSON serialization/deserialization roundtrip
- Transformation to RateAdjustment
- Backpressure level → scale factor mapping (ok=1.0, soft=0.7, hard=0.0)

**Fails When**: 
- Core changes FeedbackEvent or RateAdjustment fields
- Backpressure levels change

---

### test_protocol_conformance.py
**What**: Validates protocol implementations conform to Core contracts.

**Tests**:
- RateController protocol structure
- FeedbackPublisher protocol structure
- Protocol method signatures (apply, publish)
- DTO required fields

**Fails When**: 
- Core changes protocol method signatures
- Core adds/removes required DTO fields

---

## Running Tests

### Locally
```bash
# All contract tests
pytest tests/contracts/ -v

# Specific file
pytest tests/contracts/test_core_install.py -v

# With coverage
pytest tests/contracts/ --cov=src/market_data_pipeline --cov-report=term
```

### Via GitHub Actions
```bash
# Manual trigger:
1. Go to Actions → dispatch_contracts
2. Click "Run workflow"
3. Enter core_ref (e.g., "v1.1.0")
4. Click "Run workflow"

# Automatic trigger:
- Core team triggers via fanout.yml when contracts change
```

---

## Test Strategy

### What These Tests ARE
- ✅ Compatibility checks with Core contracts
- ✅ Smoke tests for critical data flows
- ✅ Fast CI/CD gates (< 2 min)

### What These Tests ARE NOT
- ❌ Comprehensive integration tests (see `tests/integration/`)
- ❌ Unit tests for Pipeline components (see `tests/unit/`)
- ❌ Performance benchmarks (see `tests/load/`)

**Relationship to Integration Tests**:
- Contract tests are **extracted** from `test_core_contract_conformance.py`
- Integration tests remain comprehensive (290 lines, 12 tests)
- Contract tests are minimal subset for CI speed

---

## Maintenance

### When Core Updates
1. Core publishes new contract version (e.g., v1.2.0)
2. Core's fanout triggers our dispatch_contracts.yml
3. Tests run against new Core version
4. **If tests fail**: Pipeline needs updates to match new contracts
5. **If tests pass**: No action needed

### Adding New Tests
- Add tests only for **critical** contract compatibility
- Keep tests fast (< 1 second each)
- Avoid testing Pipeline internals (use integration tests)
- Document what the test validates and when it should fail

### Test Failure Response
1. Check Core changelog for breaking changes
2. Review Core migration guide
3. Update Pipeline code to match new contracts
4. Verify all tests pass locally
5. Commit fix and re-run CI

---

## Phase 8.0C Context

These tests are part of **Phase 8.0C: Cross-Repo Orchestration**.

**Architecture**:
```
market-data-core
  ├─ Defines: DTOs (FeedbackEvent, RateAdjustment)
  ├─ Defines: Protocols (RateController, FeedbackPublisher)
  └─ Triggers: Fan-out to downstream repos on contract change

market_data_pipeline (downstream)
  ├─ Implements: RateController (RateCoordinatorAdapter)
  ├─ Implements: FeedbackPublisher (FeedbackBus)
  └─ Validates: Compatibility via contract tests ← YOU ARE HERE
```

**Goal**: Catch breaking changes in Core before they reach production.

---

## Questions?

See:
- [Phase 8.0C Viability Assessment](../../PHASE_8.0C_VIABILITY_ASSESSMENT.md)
- [Phase 8.0C Implementation Plan](../../PHASE_8.0C_IMPLEMENTATION_PLAN.md)
- [GitHub Workflows README](../../.github/workflows/README.md)
- [Core Migration Guide](../../docs/PHASE_8.0_MIGRATION_GUIDE.md)

