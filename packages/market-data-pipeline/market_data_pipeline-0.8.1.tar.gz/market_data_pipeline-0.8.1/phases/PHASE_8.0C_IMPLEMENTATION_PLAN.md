# Phase 8.0C - Implementation Plan

**Repository**: `market_data_pipeline`  
**Target**: Cross-Repo Orchestration (Fan-Out & Matrix)  
**Date**: October 17, 2025  
**Status**: READY FOR EXECUTION  
**Est. Duration**: 2-3 hours

---

## 🎯 Implementation Overview

This plan details the step-by-step implementation of Phase 8.0C for the `market_data_pipeline` repository. The goal is to enable automatic contract testing whenever `market-data-core` publishes contract changes.

**Prerequisites Met** (from viability assessment):
- ✅ Core v1.1.0 dependency installed
- ✅ Python 3.11 configured
- ✅ Comprehensive contract tests exist in integration suite
- ✅ Protocol conformance implemented

---

## 📋 Implementation Checklist

### Phase 1: Setup Directory Structure ✓
- [ ] Create `.github/workflows/` directory
- [ ] Create `tests/contracts/` directory
- [ ] Create `tests/contracts/__init__.py`

### Phase 2: GitHub Actions Workflows ✓
- [ ] Create `.github/workflows/_contracts_reusable.yml`
- [ ] Create `.github/workflows/dispatch_contracts.yml`
- [ ] Create `.github/workflows/README.md` (documentation)

### Phase 3: Contract Test Suite ✓
- [ ] Create `tests/contracts/test_core_install.py`
- [ ] Create `tests/contracts/test_feedback_flow.py`
- [ ] Create `tests/contracts/test_protocol_conformance.py`
- [ ] Verify local test execution

### Phase 4: Configuration ⚠️ (Manual)
- [ ] Create GitHub Personal Access Token (PAT)
- [ ] Add `REPO_TOKEN` secret to repository
- [ ] Document secret rotation process

### Phase 5: Testing & Validation ✓
- [ ] Run contract tests locally
- [ ] Manual workflow trigger test
- [ ] Coordinate with Core team for integration test

### Phase 6: Documentation ✓
- [ ] Update main README.md
- [ ] Update CHANGELOG.md
- [ ] Add workflow documentation

---

## 📝 Detailed Implementation Steps

### PHASE 1: Directory Structure (5 min)

#### Step 1.1: Create GitHub Workflows Directory

```bash
mkdir -p .github/workflows
```

**Validation**: Directory exists at `.github/workflows/`

---

#### Step 1.2: Create Contracts Test Directory

```bash
mkdir -p tests/contracts
```

**Validation**: Directory exists at `tests/contracts/`

---

#### Step 1.3: Create Package Marker

**File**: `tests/contracts/__init__.py`

```python
"""
Contract tests for market-data-core v1.1.0+ compatibility.

These tests verify that market_data_pipeline maintains compatibility
with core protocol contracts and data transfer objects (DTOs).

Tests in this directory are automatically triggered by market-data-core
when contract schemas change.

Test Categories:
- test_core_install.py: Verifies Core package imports
- test_feedback_flow.py: Tests FeedbackEvent ↔ RateAdjustment flow
- test_protocol_conformance.py: Validates protocol implementations

These are a minimal, fast subset of the comprehensive integration tests.
"""
```

**Lines**: 17  
**Validation**: File exists with docstring

---

### PHASE 2: GitHub Actions Workflows (30 min)

#### Step 2.1: Create Reusable Workflow

**File**: `.github/workflows/_contracts_reusable.yml`

```yaml
name: _contracts_reusable

on:
  workflow_call:
    inputs:
      core_ref:
        description: "Git ref (tag/branch/SHA) of market-data-core to test against"
        required: true
        type: string

jobs:
  contracts:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout this repo
        uses: actions/checkout@v4
      
      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install core @ ref
        run: |
          pip install -U pip wheel
          pip install "git+https://github.com/mjdevaccount/market-data-core.git@${{ inputs.core_ref }}"
          pip freeze | grep market-data-core
      
      - name: Install project + dev deps
        run: |
          pip install -e ".[dev]"
      
      - name: Run contract tests
        run: |
          pytest tests/contracts/ -v --tb=short
```

**Key Customizations**:
1. Changed `requirements-dev.txt || true` to `pip install -e ".[dev]"` (uses pyproject.toml)
2. Added `--tb=short` to pytest for cleaner output
3. Added `pip freeze | grep market-data-core` to verify installed version

**Lines**: 35  
**Validation**: Valid YAML syntax

---

#### Step 2.2: Create Dispatch Handler

**File**: `.github/workflows/dispatch_contracts.yml`

```yaml
name: dispatch_contracts

on:
  workflow_dispatch:
    inputs:
      core_ref:
        description: "Core ref (tag/branch/SHA)"
        required: true
        type: string

jobs:
  run:
    uses: ./.github/workflows/_contracts_reusable.yml
    with:
      core_ref: ${{ inputs.core_ref }}
```

**Key Points**:
- Accepts `core_ref` input for manual/automatic triggers
- Delegates to reusable workflow
- No customizations needed from template

**Lines**: 16  
**Validation**: Valid YAML syntax

---

#### Step 2.3: Create Workflow Documentation

**File**: `.github/workflows/README.md`

```markdown
# GitHub Actions Workflows

## Overview

This directory contains CI/CD workflows for `market_data_pipeline`.

## Workflows

### dispatch_contracts.yml

**Purpose**: Cross-repo contract testing with `market-data-core`.

**Trigger**:
- Automatically: Triggered by `market-data-core` when Core contracts change
- Manually: Via GitHub Actions UI for testing

**What It Does**:
1. Installs a specific version of `market-data-core` (by ref)
2. Installs this project with dev dependencies
3. Runs contract tests in `tests/contracts/`
4. Reports pass/fail status

**Manual Execution**:
```bash
# Via GitHub UI:
1. Go to Actions → dispatch_contracts
2. Click "Run workflow"
3. Enter core_ref (e.g., "v1.1.0", "main", "abc123")
4. Click "Run workflow"
```

**Expected Behavior**:
- Duration: ~2 minutes
- Tests: 3 contract tests
- Result: ✅ All tests pass (if compatible)

**Troubleshooting**:
- If tests fail: Check Core version compatibility
- If workflow fails: Verify REPO_TOKEN secret exists
- If Core install fails: Check ref exists in market-data-core repo

---

### _contracts_reusable.yml

**Purpose**: Reusable workflow logic called by `dispatch_contracts.yml`.

**Internal Use Only**: Do not trigger directly.

**Parameters**:
- `core_ref` (required): Git ref of Core to test against

**Steps**:
1. Checkout pipeline code
2. Setup Python 3.11 with pip caching
3. Install market-data-core from git at specified ref
4. Install pipeline with dev dependencies
5. Run pytest on tests/contracts/

---

## Secrets

### REPO_TOKEN

**Required For**: dispatch_contracts.yml (when triggered by Core)

**Purpose**: Allows `market-data-core` repository to trigger workflows in this repo.

**Setup**:
1. Create GitHub Personal Access Token (PAT):
   - Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Name: `REPO_TOKEN`
   - Permissions: Actions (read/write), Contents (read), Workflows (read/write)
   - Expiration: 90 days
   
2. Add to this repository:
   - Repository → Settings → Secrets and variables → Actions
   - New repository secret: Name=`REPO_TOKEN`, Value=`ghp_...`

**Rotation**: PAT expires every 90 days. Set reminder to rotate.

---

## Local Testing

You can run contract tests locally without GitHub Actions:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run contract tests
pytest tests/contracts/ -v

# Test against specific Core version
pip install "git+https://github.com/mjdevaccount/market-data-core.git@v1.1.0"
pytest tests/contracts/ -v
```

---

## Phase 8.0C Context

These workflows are part of **Phase 8.0C: Cross-Repo Orchestration**.

**Architecture**:
```
market-data-core (upstream)
    │
    ├─ contracts.yml (runs on PR)
    │       ↓ (success)
    └─ fanout.yml (triggers downstream)
            │
            ├─► market_data_pipeline (this repo)
            │   └─ dispatch_contracts.yml ← YOU ARE HERE
            │
            ├─► market-data-store
            │   └─ dispatch_contracts.yml
            │
            └─► market-data-orchestrator
                └─ dispatch_contracts.yml
```

**Goal**: Ensure all downstream repos remain compatible with Core contract changes.

---

## Support

For issues or questions:
- Check [PHASE_8.0C_VIABILITY_ASSESSMENT.md](../../PHASE_8.0C_VIABILITY_ASSESSMENT.md)
- Review Core docs: [Phase 8.0 Migration Guide](../../docs/PHASE_8.0_MIGRATION_GUIDE.md)
- Contact: Pipeline maintainers
```

**Lines**: ~145  
**Validation**: Comprehensive documentation

---

### PHASE 3: Contract Test Suite (45 min)

#### Step 3.1: test_core_install.py

**File**: `tests/contracts/test_core_install.py`

```python
"""
Contract test: Core package installation and imports.

Verifies that market-data-core v1.1.0+ can be imported and
provides expected public interfaces.
"""

import pytest


def test_core_version_imports():
    """
    Verify Core v1.1.0 telemetry and protocol imports.
    
    This test ensures the pipeline can import all required Core DTOs
    and protocols. Failure indicates a breaking change in Core's public API.
    """
    # Import telemetry DTOs
    from market_data_core.telemetry import (
        BackpressureLevel,
        FeedbackEvent,
        RateAdjustment,
    )
    
    # Import protocols
    from market_data_core.protocols import FeedbackPublisher, RateController
    
    # Verify BackpressureLevel enum
    assert BackpressureLevel.ok.value == "ok"
    assert BackpressureLevel.soft.value == "soft"
    assert BackpressureLevel.hard.value == "hard"
    
    # Verify protocol classes exist
    assert RateController is not None
    assert FeedbackPublisher is not None
    
    # Verify DTOs are Pydantic models
    assert hasattr(FeedbackEvent, 'model_validate')
    assert hasattr(RateAdjustment, 'model_dump')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Lines**: 42  
**Source**: Extracted from `tests/integration/test_core_contract_conformance.py` lines 10-15, 249-260  
**Validation**: Run `pytest tests/contracts/test_core_install.py -v`

---

#### Step 3.2: test_feedback_flow.py

**File**: `tests/contracts/test_feedback_flow.py`

```python
"""
Contract test: FeedbackEvent ↔ RateAdjustment flow.

Tests the core data flow: FeedbackEvent from Store is transformed
into RateAdjustment for rate control. This validates DTO structure
and transformation logic.
"""

import time

import pytest
from market_data_core.telemetry import (
    BackpressureLevel,
    FeedbackEvent,
    RateAdjustment,
)


def to_rate_adjustment(evt: FeedbackEvent) -> RateAdjustment:
    """
    Convert FeedbackEvent to RateAdjustment.
    
    This is the core transformation policy:
    - ok → scale 1.0 (no throttling)
    - soft → scale 0.7 (30% throttle)
    - hard → scale 0.0 (full stop)
    """
    policy = {
        "ok": 1.0,
        "soft": 0.7,
        "hard": 0.0,
    }
    scale = policy[evt.level.value]
    return RateAdjustment(
        provider="test",
        scale=scale,
        reason=evt.level,
        ts=evt.ts,
    )


def test_feedback_event_roundtrip_and_transform():
    """
    Test FeedbackEvent → JSON → FeedbackEvent → RateAdjustment.
    
    This validates:
    1. FeedbackEvent can be created with Core v1.1.0 fields
    2. JSON serialization/deserialization works
    3. Transformation to RateAdjustment preserves data
    4. Scale mapping is correct
    """
    # Create FeedbackEvent
    evt = FeedbackEvent(
        coordinator_id="q",
        queue_size=70,
        capacity=100,
        level=BackpressureLevel.soft,
        ts=time.time(),
        source="store",
    )
    
    # Core JSON roundtrip (downstream sanity check)
    packed = evt.model_dump_json()
    restored = FeedbackEvent.model_validate_json(packed)
    assert restored.level == BackpressureLevel.soft
    assert restored.queue_size == 70
    
    # Transform to RateAdjustment
    adj = to_rate_adjustment(restored)
    assert 0.0 <= adj.scale <= 1.0
    assert adj.scale == 0.7  # soft → 0.7
    assert adj.reason == BackpressureLevel.soft
    assert adj.ts == evt.ts


@pytest.mark.parametrize("level,expected_scale", [
    (BackpressureLevel.ok, 1.0),
    (BackpressureLevel.soft, 0.7),
    (BackpressureLevel.hard, 0.0),
])
def test_level_to_scale_mapping(level, expected_scale):
    """
    Test backpressure level → scale factor mapping.
    
    This is the contract between Store feedback and Pipeline throttling.
    """
    evt = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=500,
        capacity=1000,
        level=level,
        source="store",
        ts=time.time(),
    )
    
    adj = to_rate_adjustment(evt)
    assert adj.scale == expected_scale


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Lines**: 106  
**Source**: Extracted from `tests/integration/test_core_contract_conformance.py` lines 103-161, 207-245  
**Validation**: Run `pytest tests/contracts/test_feedback_flow.py -v`

---

#### Step 3.3: test_protocol_conformance.py

**File**: `tests/contracts/test_protocol_conformance.py`

```python
"""
Contract test: Protocol conformance.

Verifies that Pipeline implementations conform to Core protocols:
- RateController: Accepts RateAdjustment, applies throttling
- FeedbackPublisher: Publishes FeedbackEvent to subscribers

These are structural typing checks (duck typing), not runtime inheritance.
"""

import time

import pytest
from market_data_core.protocols import FeedbackPublisher, RateController
from market_data_core.telemetry import (
    BackpressureLevel,
    FeedbackEvent,
    RateAdjustment,
)


def test_protocols_conformance_smoke():
    """
    Smoke test: Verify protocol classes can be implemented.
    
    This doesn't test Pipeline's actual implementations (that's in integration tests).
    It verifies Core's protocols are structurally sound and can be implemented.
    """
    class FakeRate(RateController):
        """Minimal RateController implementation for testing."""
        async def apply(self, adj: RateAdjustment) -> None:
            pass
    
    class FakePub(FeedbackPublisher):
        """Minimal FeedbackPublisher implementation for testing."""
        async def publish(self, event: FeedbackEvent) -> None:
            pass
    
    # Protocol conformance via isinstance
    assert isinstance(FakeRate(), RateController)
    assert isinstance(FakePub(), FeedbackPublisher)


@pytest.mark.asyncio
async def test_rate_controller_signature():
    """
    Test RateController.apply() signature and contract.
    
    Core contract:
    - Method: apply(adjustment: RateAdjustment) -> None
    - Async: Yes
    - Side effects: Implementation-defined (store scale factor)
    """
    class TestRateController(RateController):
        def __init__(self):
            self.last_adjustment = None
        
        async def apply(self, adjustment: RateAdjustment) -> None:
            self.last_adjustment = adjustment
    
    controller = TestRateController()
    
    # Create RateAdjustment
    adjustment = RateAdjustment(
        provider="test",
        scale=0.5,
        reason=BackpressureLevel.soft,
        ts=time.time(),
    )
    
    # Apply should return None
    result = await controller.apply(adjustment)
    assert result is None
    
    # Verify side effect
    assert controller.last_adjustment is adjustment


@pytest.mark.asyncio
async def test_feedback_publisher_signature():
    """
    Test FeedbackPublisher.publish() signature and contract.
    
    Core contract:
    - Method: publish(event: FeedbackEvent) -> None
    - Async: Yes
    - Side effects: Implementation-defined (notify subscribers)
    """
    class TestFeedbackPublisher(FeedbackPublisher):
        def __init__(self):
            self.published_events = []
        
        async def publish(self, event: FeedbackEvent) -> None:
            self.published_events.append(event)
    
    publisher = TestFeedbackPublisher()
    
    # Create FeedbackEvent
    event = FeedbackEvent(
        coordinator_id="test_coord",
        queue_size=500,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time(),
    )
    
    # Publish should return None
    result = await publisher.publish(event)
    assert result is None
    
    # Verify side effect
    assert len(publisher.published_events) == 1
    assert publisher.published_events[0] is event


def test_feedback_event_required_fields():
    """
    Test FeedbackEvent has all required Core v1.1.0 fields.
    """
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=500,
        capacity=1000,
        level=BackpressureLevel.ok,
        source="store",
        ts=time.time(),
    )
    
    # Verify all fields accessible
    assert event.coordinator_id == "store_01"
    assert event.queue_size == 500
    assert event.capacity == 1000
    assert event.level == BackpressureLevel.ok
    assert event.source == "store"
    assert event.ts > 0


def test_rate_adjustment_required_fields():
    """
    Test RateAdjustment has all required Core v1.1.0 fields.
    """
    adjustment = RateAdjustment(
        provider="ibkr",
        scale=0.5,
        reason=BackpressureLevel.soft,
        ts=time.time(),
    )
    
    # Verify all fields accessible
    assert adjustment.provider == "ibkr"
    assert adjustment.scale == 0.5
    assert adjustment.reason == BackpressureLevel.soft
    assert adjustment.ts > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Lines**: 162  
**Source**: Extracted from `tests/integration/test_core_contract_conformance.py` lines 26-98, 264-289  
**Validation**: Run `pytest tests/contracts/test_protocol_conformance.py -v`

---

### PHASE 4: Secret Configuration (Manual - 5 min)

#### Step 4.1: Create Personal Access Token

**Navigate to**: https://github.com/settings/tokens?type=beta

**Settings**:
- **Token name**: `REPO_TOKEN`
- **Expiration**: 90 days
- **Repository access**: 
  - Select: "All repositories" OR
  - Select: "Only select repositories" → `market_data_pipeline`, `market-data-core`, `market-data-store`, `market-data-orchestrator`
  
**Permissions**:
- ✅ **Actions**: Read and write
- ✅ **Contents**: Read
- ✅ **Metadata**: Read (auto-selected)
- ✅ **Workflows**: Read and write

**Click**: "Generate token"

**Copy**: Token value (starts with `ghp_...`)

---

#### Step 4.2: Add Secret to Repository

**Navigate to**: https://github.com/mjdevaccount/market_data_pipeline/settings/secrets/actions

**Click**: "New repository secret"

**Fields**:
- **Name**: `REPO_TOKEN`
- **Secret**: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` (paste token)

**Click**: "Add secret"

**Validation**: Secret appears in list as `REPO_TOKEN` (value hidden)

---

#### Step 4.3: Document Rotation

**Create Reminder**: Calendar event for Day 80 (10 days before expiration)

**Process**:
1. Generate new PAT (same settings)
2. Update secret in all repositories
3. Test workflow trigger
4. Delete old PAT

---

### PHASE 5: Testing & Validation (30 min)

#### Step 5.1: Local Test Execution

```bash
# Ensure you're in project root
cd c:\openbb\market_data_pipeline

# Install dev dependencies
pip install -e ".[dev]"

# Run contract tests
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
# =================== 10 passed in 0.5s ===================
```

**Success Criteria**:
- ✅ All 10 tests pass
- ✅ No import errors
- ✅ Execution time < 5 seconds

**If Failures**: 
- Check `market-data-core` version: `pip list | grep market-data-core`
- Should be `1.1.0` or higher
- If not: `pip install --upgrade market-data-core`

---

#### Step 5.2: Commit & Push Workflows

```bash
# Create feature branch
git checkout -b feat/phase-8.0c-cross-repo

# Add new files
git add .github/
git add tests/contracts/
git add PHASE_8.0C_VIABILITY_ASSESSMENT.md
git add PHASE_8.0C_IMPLEMENTATION_PLAN.md

# Commit
git commit -m "feat: Add Phase 8.0C cross-repo orchestration workflows

- Add GitHub Actions workflows for contract testing
- Add tests/contracts/ suite (10 tests)
- Enable automatic testing on Core contract changes
- Part of Phase 8.0C: Cross-Repo Orchestration"

# Push
git push origin feat/phase-8.0c-cross-repo
```

---

#### Step 5.3: Manual Workflow Trigger

**Navigate to**: https://github.com/mjdevaccount/market_data_pipeline/actions

**Select**: "dispatch_contracts" workflow (left sidebar)

**Click**: "Run workflow" (top right)

**Inputs**:
- **Use workflow from**: Branch `feat/phase-8.0c-cross-repo`
- **core_ref**: `v1.1.0` (or `820e06e` for current base)

**Click**: "Run workflow"

**Wait**: ~2 minutes for completion

**Expected Output**:
```
✅ run / contracts (dispatch_contracts)
   ✅ Checkout this repo
   ✅ Setup Python 3.11
   ✅ Install core @ ref
   ✅ Install project + dev deps
   ✅ Run contract tests
      10 passed in 1.2s
```

**If Failure**:
- Check workflow logs for specific error
- Verify `REPO_TOKEN` secret exists
- Verify `core_ref` exists in market-data-core repo
- Test locally first: `pytest tests/contracts/ -v`

---

#### Step 5.4: Core Team Coordination

**After manual test succeeds**:

**Email/Slack**: Core team

**Message**:
```
Subject: Pipeline Phase 8.0C Implementation Complete

Hi Core team,

market_data_pipeline has completed Phase 8.0C implementation:

✅ GitHub Actions workflows created
✅ Contract test suite ready (10 tests, ~2 min runtime)
✅ Manual trigger tested successfully
✅ Ready for automatic fan-out integration

Test details:
- Branch: feat/phase-8.0c-cross-repo
- Workflow: dispatch_contracts.yml
- Test Core ref: v1.1.0 (passed)

For integration testing:
1. Your fanout.yml can trigger our dispatch_contracts.yml
2. Use core_ref parameter to pass your commit SHA
3. Our contract tests will validate compatibility

Awaiting your fanout.yml implementation for end-to-end testing.

Thanks!
```

---

### PHASE 6: Documentation (15 min)

#### Step 6.1: Update README.md

**File**: `README.md`

**Location**: After line 920 (in "## 🧪 Testing" section)

**Add**:

```markdown
### Contract Tests

Contract tests verify compatibility with `market-data-core` protocol contracts:

```bash
# Run contract tests only
pytest tests/contracts/ -v

# Expected: 10 tests, ~0.5s duration
```

**Purpose**: These tests validate that Pipeline remains compatible with Core's
data transfer objects (DTOs) and protocols. They are automatically triggered
when Core publishes contract changes.

**Categories**:
- `test_core_install.py`: Core package imports and version compatibility
- `test_feedback_flow.py`: FeedbackEvent ↔ RateAdjustment transformations
- `test_protocol_conformance.py`: Protocol implementations (RateController, FeedbackPublisher)

**Note**: Contract tests are a minimal, fast subset of the full integration test suite.
See `tests/contracts/README.md` for details.

**Cross-Repo Testing**: These tests are triggered automatically by `market-data-core`
via GitHub Actions when Core's contract schemas change. See `.github/workflows/README.md`
for workflow documentation.
```

---

#### Step 6.2: Update CHANGELOG.md

**File**: `CHANGELOG.md`

**Location**: Top of file (after header, before existing entries)

**Add**:

```markdown
## [Unreleased]

### Added
- **Phase 8.0C: Cross-Repo Orchestration**
  - GitHub Actions workflows for automated contract testing
  - `.github/workflows/dispatch_contracts.yml`: Entry point for Core fan-out triggers
  - `.github/workflows/_contracts_reusable.yml`: Reusable workflow for contract tests
  - `tests/contracts/` test suite (10 tests) for Core v1.1.0 compatibility validation
  - Automatic testing triggered by `market-data-core` contract changes
  - Workflow documentation in `.github/workflows/README.md`

### Changed
- Reorganized contract tests from `tests/integration/` into dedicated `tests/contracts/` suite
- Contract tests now optimized for CI/CD speed (< 2 min execution)

### Documentation
- Added `PHASE_8.0C_VIABILITY_ASSESSMENT.md`: Detailed viability analysis
- Added `PHASE_8.0C_IMPLEMENTATION_PLAN.md`: Step-by-step implementation guide
- Updated README.md with contract testing documentation
```

---

#### Step 6.3: Create Contracts Test README

**File**: `tests/contracts/README.md`

```markdown
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
```

---

## ✅ Final Validation Checklist

### Pre-Commit Checks
- [ ] All contract tests pass locally: `pytest tests/contracts/ -v`
- [ ] All existing tests still pass: `pytest tests/ -v`
- [ ] No linter errors: `ruff check .`
- [ ] No type errors: `mypy src/`
- [ ] Git status clean (all files added)

### Post-Commit Checks
- [ ] Branch pushed successfully
- [ ] Manual workflow trigger succeeds
- [ ] Workflow logs show 10 tests passed
- [ ] Execution time < 3 minutes

### Documentation Checks
- [ ] README.md updated
- [ ] CHANGELOG.md updated
- [ ] Workflow README created
- [ ] Contract tests README created

### Configuration Checks
- [ ] `REPO_TOKEN` secret added to repository
- [ ] Secret rotation reminder set (Day 80)

### Integration Checks
- [ ] Core team notified
- [ ] Integration test coordinated
- [ ] Auto-trigger verified (once Core fanout is ready)

---

## 🚀 Completion Criteria

**Phase 8.0C is complete when**:

1. ✅ All files created and committed
2. ✅ Manual workflow trigger succeeds
3. ✅ Local tests pass (10/10)
4. ✅ Documentation complete
5. ✅ Secret configured
6. ✅ Core team coordinated

**Production ready when**:
7. ✅ Auto-trigger from Core works
8. ✅ PR merged to `base`
9. ✅ Other downstream repos (Store, Orchestrator) complete

---

## 📞 Support & Escalation

### Common Issues

**Issue**: Tests fail locally
- **Solution**: Check Core version: `pip list | grep market-data-core`
- **Should be**: 1.1.0 or higher
- **Fix**: `pip install --upgrade market-data-core`

**Issue**: Workflow not visible in Actions
- **Solution**: Push branch first: `git push origin feat/phase-8.0c-cross-repo`
- **Then**: Refresh Actions page

**Issue**: Workflow fails with "secret not found"
- **Solution**: Verify `REPO_TOKEN` secret in repo settings
- **Path**: Settings → Secrets and variables → Actions

**Issue**: Core install fails in workflow
- **Solution**: Verify `core_ref` parameter is valid
- **Test**: `git ls-remote https://github.com/mjdevaccount/market-data-core.git <ref>`

### Escalation Path
1. Check local tests first
2. Review workflow logs
3. Consult viability assessment document
4. Contact Core team for Core-side issues

---

**Implementation Plan Complete**  
**Ready for Execution**: ✅  
**Estimated Duration**: 2-3 hours  
**Risk Level**: LOW

