# Core v1.1.1 Upgrade & Integration Plan

**Date**: October 17, 2025  
**Current**: Core v1.1.0  
**Target**: Core v1.1.1  
**Estimated Time**: 30-45 minutes  
**Risk**: VERY LOW

---

## 🎯 Bottom Line

**We're already 90% compliant with Core's integration guide!**

Only need to:
1. ✅ Upgrade Core from v1.1.0 → v1.1.1
2. ✅ Test enum comparison style compatibility
3. ✅ Verify all tests pass

Our implementation **exceeds** Core's minimum spec (10 tests vs their 6-7).

---

## 📋 Quick Action Checklist

### Phase 1: Version Upgrade & Testing (20 min)

- [ ] Upgrade Core to v1.1.1
- [ ] Test enum comparison styles
- [ ] Run all contract tests locally
- [ ] Verify tests pass

### Phase 2: Optional Improvements (15 min)

- [ ] Add explicit RateAdjustment roundtrip test (optional)
- [ ] Adjust enum assertions if needed (optional)
- [ ] Update documentation

### Phase 3: Validation (10 min)

- [ ] Test workflow with v1.1.1
- [ ] Coordinate with Core team
- [ ] Confirm fanout integration works

---

## 🔍 Key Findings

### What We Have (Already)

✅ **Workflows**: Compliant with Core's guide
- `.github/workflows/_contracts_reusable.yml` ✅
- `.github/workflows/dispatch_contracts.yml` ✅

✅ **Contract Tests**: More comprehensive than guide
- `test_core_install.py` ✅ (1 test, very thorough)
- `test_feedback_flow.py` ✅ (2 tests with parametrization = 4 test cases)
- `test_protocol_conformance.py` ✅ (5 tests)
- **Total**: 10+ test cases vs guide's 6-7

✅ **Structure**: Matches guide exactly
- `tests/contracts/` directory ✅
- All specified test files present ✅

### What Needs Attention

⚠️ **Version Mismatch**:
- Current: Core v1.1.0
- Guide States: Core v1.1.1
- Action: Upgrade (patch version, low risk)

⚠️ **Minor Test Differences**:
- Enum comparison: We use `.value`, guide uses direct comparison
- Need to test if both work in v1.1.1

⚠️ **Optional Test Addition**:
- Guide has explicit `test_rate_adjustment_roundtrip()`
- We test it implicitly, could add explicit test

---

## 🚀 Execution Plan

### Step 1: Test Current State (5 min)

**Verify baseline before upgrading**:

```bash
# Check current version
pip list | grep market-data-core
# Output: market-data-core  1.1.0

# Run tests with current version
pytest tests/contracts/ -v

# Expected: All 10 tests pass
```

---

### Step 2: Test Enum Compatibility (5 min)

**Test if Core v1.1.1 enum allows direct string comparison**:

```bash
python -c "
from market_data_core.telemetry import BackpressureLevel

print('=== Core v1.1.0 Enum Tests ===')
print()

# Test 1: Direct comparison (Core guide style)
try:
    result = (BackpressureLevel.ok == 'ok')
    print(f'✓ Direct comparison works: {result}')
except Exception as e:
    print(f'✗ Direct comparison failed: {e}')

# Test 2: .value comparison (our style)
try:
    result = (BackpressureLevel.ok.value == 'ok')
    print(f'✓ .value comparison works: {result}')
except Exception as e:
    print(f'✗ .value comparison failed: {e}')

print()
print('Enum details:')
print(f'  Type: {type(BackpressureLevel.ok)}')
print(f'  Value: {BackpressureLevel.ok.value}')
print(f'  String: {str(BackpressureLevel.ok)}')
print(f'  Repr: {repr(BackpressureLevel.ok)}')
"
```

**Record results for comparison after upgrade**.

---

### Step 3: Upgrade Core (5 min)

```bash
# Upgrade to v1.1.1
pip install --upgrade "market-data-core>=1.1.1"

# Verify upgrade
pip list | grep market-data-core
# Expected: market-data-core  1.1.1
```

---

### Step 4: Re-test Enum Compatibility (5 min)

**Run same enum test with v1.1.1**:

```bash
python -c "
from market_data_core.telemetry import BackpressureLevel

print('=== Core v1.1.1 Enum Tests ===')
print()

# Test 1: Direct comparison (Core guide style)
try:
    result = (BackpressureLevel.ok == 'ok')
    print(f'✓ Direct comparison works: {result}')
except Exception as e:
    print(f'✗ Direct comparison failed: {e}')

# Test 2: .value comparison (our style)  
try:
    result = (BackpressureLevel.ok.value == 'ok')
    print(f'✓ .value comparison works: {result}')
except Exception as e:
    print(f'✗ .value comparison failed: {e}')
"
```

**Decision Point**:
- If **both work**: Keep our `.value` style (more explicit)
- If **only direct comparison works**: Update our tests to match guide
- If **only .value works**: Our tests are correct, guide has typo

---

### Step 5: Run All Contract Tests (5 min)

```bash
# Run with v1.1.1
pytest tests/contracts/ -v

# Expected output:
# tests/contracts/test_core_install.py::test_core_version_imports PASSED
# tests/contracts/test_feedback_flow.py::test_feedback_event_roundtrip_and_transform PASSED
# tests/contracts/test_feedback_flow.py::test_level_to_scale_mapping[ok-1.0] PASSED
# tests/contracts/test_feedback_flow.py::test_level_to_scale_mapping[soft-0.7] PASSED
# tests/contracts/test_feedback_flow.py::test_level_to_scale_mapping[hard-0.0] PASSED
# tests/contracts/test_protocol_conformance.py::test_protocols_conformance_smoke PASSED
# tests/contracts/test_protocol_conformance.py::test_rate_controller_signature PASSED
# tests/contracts/test_protocol_conformance.py::test_feedback_publisher_signature PASSED
# tests/contracts/test_protocol_conformance.py::test_feedback_event_required_fields PASSED
# tests/contracts/test_protocol_conformance.py::test_rate_adjustment_required_fields PASSED
# ========================= 10 passed in ~4s =========================
```

**If all pass**: ✅ v1.1.1 is compatible!  
**If any fail**: Investigate and fix (unlikely for patch version)

---

### Step 6: Update Dependencies (5 min)

**If tests pass, update pyproject.toml**:

```toml
# pyproject.toml line 12
dependencies = [
    "market-data-core>=1.1.1",  # Changed from >=1.1.0
    ...
]
```

**Then regenerate requirements.txt** (if used):

```bash
pip-compile pyproject.toml
```

---

### Step 7: Optional - Add Explicit Test (10 min)

**Add to `tests/contracts/test_feedback_flow.py`** (after line 97):

```python
def test_rate_adjustment_roundtrip():
    """Test RateAdjustment JSON serialization/deserialization."""
    adj = RateAdjustment(
        provider="ibkr",
        scale=0.7,
        reason=BackpressureLevel.soft,
        ts=time.time(),
    )
    
    # Serialize to JSON
    packed = adj.model_dump_json()
    
    # Deserialize from JSON
    restored = RateAdjustment.model_validate_json(packed)
    
    # Verify fields match
    assert restored.provider == adj.provider
    assert restored.scale == adj.scale
    assert restored.reason == BackpressureLevel.soft
```

**Then test**:

```bash
pytest tests/contracts/test_feedback_flow.py::test_rate_adjustment_roundtrip -v
# Expected: PASSED
```

---

### Step 8: Test Workflow (10 min)

**Test GitHub Actions workflow with v1.1.1**:

```bash
# Manual trigger
gh workflow run dispatch_contracts.yml -f core_ref=v1.1.1

# Watch progress
gh run watch

# Expected: All tests pass in CI
```

---

### Step 9: Commit Changes (5 min)

**If changes were made**:

```bash
git add pyproject.toml requirements.txt tests/contracts/
git commit -m "chore: Upgrade market-data-core to v1.1.1

- Update Core dependency from >=1.1.0 to >=1.1.1
- Verify all contract tests pass with v1.1.1
- All 10 tests passing locally and in CI

Ref: Core Integration Guide compliance"

git push origin base
```

---

## 🎯 Success Criteria

**All must be true**:

- [x] Core v1.1.1 installed
- [x] All 10 contract tests pass locally
- [x] Workflow passes with Core v1.1.1
- [x] pyproject.toml updated
- [x] No breaking changes detected

---

## ⚠️ Potential Issues & Solutions

### Issue 1: Tests fail with v1.1.1

**Symptom**: Some contract tests fail after upgrade

**Solution**:
1. Check error message for clues
2. Compare v1.1.0 vs v1.1.1 changelog
3. Update test expectations to match new behavior
4. Contact Core team if breaking change detected

---

### Issue 2: Enum comparison doesn't work

**Symptom**: `BackpressureLevel.ok == "ok"` returns False or raises error

**Solution**:
- This means our `.value` approach is correct
- Keep our tests as-is
- Inform Core team their guide has incorrect example

---

### Issue 3: Workflow fails in CI but passes locally

**Symptom**: Tests pass locally but fail in GitHub Actions

**Possible Causes**:
- Cache issue (old Core version cached)
- Environment difference

**Solution**:
```yaml
# Add cache busting to workflow
- name: Clear pip cache
  run: pip cache purge
```

---

## 📊 Comparison Summary

| Aspect | Core Guide | Pipeline Current | Status |
|--------|-----------|------------------|--------|
| **Core Version** | v1.1.1 | v1.1.0 | ⚠️ NEED UPGRADE |
| **Workflows** | Specified | ✅ Implemented | ✅ COMPLIANT |
| **Test Structure** | Specified | ✅ Matches | ✅ COMPLIANT |
| **Test Count** | 6-7 tests | 10 tests | ✅ EXCEEDS |
| **Test Quality** | Minimal | Comprehensive | ✅ EXCEEDS |

**Overall**: ✅ **AHEAD OF SPEC** (just need version bump)

---

## 🎉 Expected Outcome

**After completion**:

1. ✅ Pipeline fully compliant with Core Integration Guide
2. ✅ Core v1.1.1 installed and tested
3. ✅ All contract tests passing (10/10)
4. ✅ Ready for Core team's fanout integration
5. ✅ More comprehensive tests than minimum spec

**Time Investment**: 30-45 minutes  
**Risk**: Very Low (patch version upgrade)  
**Confidence**: 95%

---

## 📚 Related Documents

- `CORE_INTEGRATION_GUIDE_VIABILITY.md` - Full viability assessment
- `phases/PHASE_8.0C_VIABILITY_ASSESSMENT.md` - Original Phase 8.0C assessment
- `.github/workflows/README.md` - Workflow documentation
- `tests/contracts/README.md` - Contract tests documentation

---

**Ready to proceed!** 🚀

The Pipeline is in excellent shape - just needs a minor version bump and verification.


