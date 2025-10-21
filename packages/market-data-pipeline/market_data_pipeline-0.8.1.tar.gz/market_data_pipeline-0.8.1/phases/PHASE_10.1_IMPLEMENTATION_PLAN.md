# Phase 10.1 — Pulse Integration Implementation Plan

**Date**: 2025-10-18  
**Repo**: `market_data_pipeline` (Consumer side)  
**Core Dependency**: `market-data-core>=1.2.0,<2.0.0`

---

## Overview

This plan details the step-by-step implementation of Pulse integration for the Pipeline as a **consumer** of `telemetry.feedback` events from the Store.

**Key Principle**: Reuse existing `FeedbackHandler` business logic. Pulse is just a new **transport layer**.

---

## Phase 1: Core Upgrade

### Step 1.1: Update dependency

**File**: `pyproject.toml`

```toml
dependencies = [
    "market-data-core>=1.2.0,<2.0.0",  # Was: >=1.1.1
    # ... rest unchanged
]
```

### Step 1.2: Reinstall and verify

```powershell
pip install -e ".[dev]"
pip list | Select-String "market-data-core"
```

Expected: `market-data-core 1.2.0` (or from git tag `v1.2.0-pulse`)

### Step 1.3: Run existing tests

```powershell
pytest tests/contracts/ -v
pytest tests/unit/orchestration/test_feedback_consumer.py -v
```

All tests should pass (v1.2.0 is backward-compatible).

---

## Phase 2: Create Pulse Module

### Step 2.1: Create `pulse/__init__.py`

**File**: `src/market_data_pipeline/pulse/__init__.py`

```python
"""
Pulse integration for Pipeline — Phase 10.1.

Consumer of telemetry.feedback events from Store via Core event bus.
"""

from .config import PulseConfig
from .consumer import FeedbackConsumer

__all__ = ["PulseConfig", "FeedbackConsumer"]
```

### Step 2.2: Create `pulse/config.py`

**File**: `src/market_data_pipeline/pulse/config.py`

```python
"""Pulse configuration (Phase 10.1)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PulseConfig:
    """
    Pulse event bus configuration.
    
    Environment Variables:
        PULSE_ENABLED: Enable Pulse integration (default: true)
        EVENT_BUS_BACKEND: Backend type (inmem|redis, default: inmem)
        REDIS_URL: Redis connection string (default: redis://localhost:6379/0)
        MD_NAMESPACE: Namespace prefix for streams (default: mdp)
        SCHEMA_TRACK: Schema track (v1|v2, default: v1)
        PUBLISHER_TOKEN: Optional auth token for publishers
    
    Example:
        cfg = PulseConfig()
        if cfg.enabled:
            bus = create_event_bus(backend=cfg.backend, redis_url=cfg.redis_url)
    """
    
    enabled: bool = os.getenv("PULSE_ENABLED", "true").lower() == "true"
    backend: str = os.getenv("EVENT_BUS_BACKEND", "inmem")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ns: str = os.getenv("MD_NAMESPACE", "mdp")
    track: str = os.getenv("SCHEMA_TRACK", "v1")
    publisher_token: str = os.getenv("PUBLISHER_TOKEN", "unset")
```

### Step 2.3: Create `pulse/consumer.py`

**File**: `src/market_data_pipeline/pulse/consumer.py`

```python
"""
Pulse feedback consumer — subscribes to telemetry.feedback and applies rate adjustments.

Phase 10.1: Wraps existing FeedbackHandler with Pulse event bus transport.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

from loguru import logger
from market_data_core.events import create_event_bus
from market_data_core.events.envelope import EventEnvelope
from market_data_core.telemetry import FeedbackEvent

from ..orchestration.feedback.consumer import FeedbackHandler

if TYPE_CHECKING:
    from market_data_core.protocols import RateController
    from ..settings.feedback import PipelineFeedbackSettings
    from .config import PulseConfig


STREAM = "telemetry.feedback"
GROUP = "pipeline"


class FeedbackConsumer:
    """
    Pulse consumer for Store feedback events.
    
    Subscribes to telemetry.feedback stream and applies rate adjustments
    via RateController using existing FeedbackHandler business logic.
    
    Features:
        - Idempotency: Deduplicate redelivered messages
        - Metrics: pulse_consume_total, pulse_lag_ms
        - ACK/FAIL: At-least-once delivery with DLQ
    
    Example:
        cfg = PulseConfig()
        settings = PipelineFeedbackSettings()
        consumer = FeedbackConsumer(rate_controller, settings, cfg)
        await consumer.run(consumer_name="pipeline_w1")
    """
    
    def __init__(
        self,
        rate_controller: RateController,
        settings: PipelineFeedbackSettings,
        cfg: PulseConfig | None = None,
    ) -> None:
        """
        Initialize Pulse feedback consumer.
        
        Args:
            rate_controller: Core RateController protocol implementation
            settings: Pipeline feedback settings (policy, provider)
            cfg: Pulse configuration (defaults to env-based)
        """
        self.cfg = cfg or PulseConfig()
        self.settings = settings
        
        # Reuse existing FeedbackHandler business logic
        self.handler = FeedbackHandler(
            rate=rate_controller,
            provider=settings.provider_name,
            policy=settings.get_policy(),
        )
        
        # Create event bus (inmem or redis)
        self.bus = create_event_bus(
            backend=self.cfg.backend,
            redis_url=self.cfg.redis_url if self.cfg.backend == "redis" else None,
        )
        
        # Idempotency: simple seen-set (LRU cache in production)
        self._seen_ids: set[str] = set()
        self._seen_lock = asyncio.Lock()
        
        # Metrics
        self._metrics_available = False
        try:
            from ...metrics import (
                PULSE_CONSUME_TOTAL,
                PULSE_LAG_MS,
            )
            self._metric_consume = PULSE_CONSUME_TOTAL
            self._metric_lag = PULSE_LAG_MS
            self._metrics_available = True
        except ImportError:
            logger.warning("Pulse metrics not available (prometheus-client not installed)")
    
    async def _is_seen(self, envelope_id: str) -> bool:
        """Check if envelope has been processed (idempotency)."""
        async with self._seen_lock:
            if envelope_id in self._seen_ids:
                return True
            self._seen_ids.add(envelope_id)
            
            # Simple LRU: keep only last 10k IDs
            if len(self._seen_ids) > 10000:
                # Remove oldest 1000 (approximation)
                to_remove = list(self._seen_ids)[:1000]
                for eid in to_remove:
                    self._seen_ids.discard(eid)
            
            return False
    
    async def _handle(self, envelope: EventEnvelope[FeedbackEvent]) -> None:
        """
        Handle a feedback event envelope.
        
        Args:
            envelope: Event envelope with FeedbackEvent payload
        """
        # Idempotency check
        if await self._is_seen(envelope.id):
            logger.debug(f"[pulse] Skipping duplicate envelope: {envelope.id}")
            if self._metrics_available:
                self._metric_consume.labels(
                    stream=STREAM,
                    track=self.cfg.track,
                    outcome="duplicate",
                ).inc()
            return
        
        # Delegate to existing FeedbackHandler
        await self.handler.handle(envelope.payload)
    
    async def run(self, consumer_name: str) -> None:
        """
        Start the Pulse consumer loop.
        
        Subscribes to telemetry.feedback and processes events until cancelled.
        
        Args:
            consumer_name: Consumer identifier for this worker (e.g., "pipeline_w1")
        
        Raises:
            asyncio.CancelledError: On graceful shutdown
        """
        stream = f"{self.cfg.ns}.{STREAM}"
        logger.info(
            f"[pulse] Starting feedback consumer: stream={stream} group={GROUP} consumer={consumer_name}"
        )
        
        try:
            async for envelope in self.bus.subscribe(stream, group=GROUP, consumer=consumer_name):
                t0 = time.time()
                
                try:
                    # Process event
                    await self._handle(envelope)
                    
                    # ACK successful processing
                    await self.bus.ack(stream, envelope.id)
                    
                    # Metrics: success
                    if self._metrics_available:
                        self._metric_consume.labels(
                            stream=STREAM,
                            track=self.cfg.track,
                            outcome="success",
                        ).inc()
                
                except Exception as e:
                    # Log and FAIL to DLQ
                    logger.exception(f"[pulse] Error processing envelope {envelope.id}")
                    await self.bus.fail(stream, envelope.id, str(e))
                    
                    # Metrics: error
                    if self._metrics_available:
                        self._metric_consume.labels(
                            stream=STREAM,
                            track=self.cfg.track,
                            outcome="error",
                        ).inc()
                
                finally:
                    # Metrics: lag
                    if self._metrics_available:
                        lag_ms = int((time.time() - envelope.ts) * 1000)
                        self._metric_lag.labels(stream=STREAM).set(lag_ms)
        
        except asyncio.CancelledError:
            logger.info("[pulse] Feedback consumer cancelled (graceful shutdown)")
            raise
        except Exception:
            logger.exception("[pulse] Feedback consumer crashed")
            raise
```

---

## Phase 3: Add Metrics

### Step 3.1: Update `src/market_data_pipeline/metrics.py`

Add new Pulse metrics:

```python
# Existing imports...
from prometheus_client import Counter, Gauge, Histogram

# ... existing metrics ...

# ── Phase 10.1: Pulse Metrics ──
PULSE_CONSUME_TOTAL = Counter(
    "pulse_consume_total",
    "Total Pulse events consumed",
    ["stream", "track", "outcome"],  # outcome: success|error|duplicate
)

PULSE_LAG_MS = Gauge(
    "pulse_lag_ms",
    "Pulse consumer lag (ms) from event timestamp",
    ["stream"],
)

# If publishing rate adjustments (optional Phase 10.1+):
# PULSE_PUBLISH_TOTAL = Counter(
#     "pulse_publish_total",
#     "Total Pulse events published",
#     ["stream", "track", "outcome"],
# )
```

---

## Phase 4: Tests

### Step 4.1: Create `tests/pulse/__init__.py`

```python
"""Tests for Pulse integration (Phase 10.1)."""
```

### Step 4.2: Create `tests/pulse/test_pulse_consumer.py`

```python
"""Unit tests for Pulse feedback consumer (inmem backend)."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from market_data_core.events import create_event_bus
from market_data_core.events.envelope import EventEnvelope, EventMeta
from market_data_core.protocols import RateController
from market_data_core.telemetry import BackpressureLevel, FeedbackEvent, RateAdjustment

from market_data_pipeline.pulse import FeedbackConsumer, PulseConfig
from market_data_pipeline.settings.feedback import PipelineFeedbackSettings


class MockRateController(RateController):
    """Mock RateController for testing."""
    
    def __init__(self) -> None:
        self.adjustments: list[RateAdjustment] = []
    
    async def apply(self, adjustment: RateAdjustment) -> None:
        """Record adjustment."""
        self.adjustments.append(adjustment)


@pytest.fixture
def rate_controller() -> MockRateController:
    """Provide mock rate controller."""
    return MockRateController()


@pytest.fixture
def settings() -> PipelineFeedbackSettings:
    """Provide feedback settings."""
    return PipelineFeedbackSettings(
        provider_name="test_provider",
        scale_ok=1.0,
        scale_soft=0.5,
        scale_hard=0.0,
    )


@pytest.fixture
def pulse_config() -> PulseConfig:
    """Provide Pulse config (inmem)."""
    return PulseConfig.__new__(
        PulseConfig,
        enabled=True,
        backend="inmem",
        redis_url="",
        ns="test",
        track="v1",
        publisher_token="unset",
    )


@pytest.mark.asyncio
async def test_consumer_processes_feedback_event(
    rate_controller: MockRateController,
    settings: PipelineFeedbackSettings,
    pulse_config: PulseConfig,
) -> None:
    """Test consumer processes feedback event and applies rate adjustment."""
    # Setup
    consumer = FeedbackConsumer(rate_controller, settings, pulse_config)
    bus = consumer.bus
    stream = f"{pulse_config.ns}.telemetry.feedback"
    
    # Publish event
    event = FeedbackEvent(
        coordinator_id="test_coord",
        queue_size=70,
        capacity=100,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time(),
    )
    envelope = EventEnvelope(
        id="",
        key="test_coord",
        ts=time.time(),
        meta=EventMeta(schema_id="telemetry.FeedbackEvent", track="v1", headers={}),
        payload=event,
    )
    await bus.publish(stream, envelope, key="test_coord")
    
    # Start consumer (run for short time)
    task = asyncio.create_task(consumer.run("test_consumer"))
    await asyncio.sleep(0.1)  # Let it process
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # Assert
    assert len(rate_controller.adjustments) == 1
    adj = rate_controller.adjustments[0]
    assert adj.provider == "test_provider"
    assert adj.scale == 0.5  # soft → 0.5
    assert adj.reason == BackpressureLevel.soft


@pytest.mark.asyncio
async def test_consumer_idempotency(
    rate_controller: MockRateController,
    settings: PipelineFeedbackSettings,
    pulse_config: PulseConfig,
) -> None:
    """Test consumer deduplicates redelivered messages."""
    # Setup
    consumer = FeedbackConsumer(rate_controller, settings, pulse_config)
    
    # Create event with fixed ID
    event = FeedbackEvent(
        coordinator_id="test_coord",
        queue_size=70,
        capacity=100,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time(),
    )
    envelope = EventEnvelope(
        id="fixed-id-123",
        key="test_coord",
        ts=time.time(),
        meta=EventMeta(schema_id="telemetry.FeedbackEvent", track="v1", headers={}),
        payload=event,
    )
    
    # Process twice
    await consumer._handle(envelope)
    await consumer._handle(envelope)
    
    # Assert: only one adjustment (idempotency)
    assert len(rate_controller.adjustments) == 1


@pytest.mark.asyncio
async def test_consumer_different_levels(
    rate_controller: MockRateController,
    settings: PipelineFeedbackSettings,
    pulse_config: PulseConfig,
) -> None:
    """Test consumer applies correct scale for each backpressure level."""
    consumer = FeedbackConsumer(rate_controller, settings, pulse_config)
    
    levels_and_scales = [
        (BackpressureLevel.ok, 1.0),
        (BackpressureLevel.soft, 0.5),
        (BackpressureLevel.hard, 0.0),
    ]
    
    for level, expected_scale in levels_and_scales:
        event = FeedbackEvent(
            coordinator_id="test_coord",
            queue_size=70,
            capacity=100,
            level=level,
            source="store",
            ts=time.time(),
        )
        envelope = EventEnvelope(
            id=f"id-{level.value}",
            key="test_coord",
            ts=time.time(),
            meta=EventMeta(schema_id="telemetry.FeedbackEvent", track="v1", headers={}),
            payload=event,
        )
        await consumer._handle(envelope)
    
    # Assert
    assert len(rate_controller.adjustments) == 3
    for i, (_, expected_scale) in enumerate(levels_and_scales):
        assert rate_controller.adjustments[i].scale == expected_scale
```

### Step 4.3: Create `tests/pulse/test_redis_integration.py`

```python
"""Integration tests for Pulse (redis backend) — skipped if Redis unavailable."""

import asyncio
import os
import time

import pytest
from market_data_core.events import create_event_bus
from market_data_core.events.envelope import EventEnvelope, EventMeta
from market_data_core.protocols import RateController
from market_data_core.telemetry import BackpressureLevel, FeedbackEvent, RateAdjustment

from market_data_pipeline.pulse import FeedbackConsumer, PulseConfig
from market_data_pipeline.settings.feedback import PipelineFeedbackSettings


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_AVAILABLE = os.getenv("EVENT_BUS_BACKEND") == "redis"


class MockRateController(RateController):
    """Mock rate controller."""
    
    def __init__(self) -> None:
        self.adjustments: list[RateAdjustment] = []
    
    async def apply(self, adjustment: RateAdjustment) -> None:
        self.adjustments.append(adjustment)


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available (set EVENT_BUS_BACKEND=redis)")
@pytest.mark.asyncio
async def test_redis_feedback_flow() -> None:
    """Test full feedback flow with Redis backend."""
    # Setup
    cfg = PulseConfig.__new__(
        PulseConfig,
        enabled=True,
        backend="redis",
        redis_url=REDIS_URL,
        ns="test_redis",
        track="v1",
        publisher_token="unset",
    )
    settings = PipelineFeedbackSettings(provider_name="test", scale_soft=0.7)
    rate_controller = MockRateController()
    
    consumer = FeedbackConsumer(rate_controller, settings, cfg)
    bus = create_event_bus(backend="redis", redis_url=REDIS_URL)
    
    stream = f"{cfg.ns}.telemetry.feedback"
    
    # Publish event
    event = FeedbackEvent(
        coordinator_id="redis_test",
        queue_size=80,
        capacity=100,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time(),
    )
    envelope = EventEnvelope(
        id="",
        key="redis_test",
        ts=time.time(),
        meta=EventMeta(schema_id="telemetry.FeedbackEvent", track="v1", headers={}),
        payload=event,
    )
    await bus.publish(stream, envelope, key="redis_test")
    
    # Start consumer
    task = asyncio.create_task(consumer.run("test_redis_consumer"))
    await asyncio.sleep(0.5)  # Let it process
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # Assert
    assert len(rate_controller.adjustments) >= 1
    assert rate_controller.adjustments[0].scale == 0.7
```

---

## Phase 5: CI/CD Workflows

### Step 5.1: Create `.github/workflows/_pulse_reusable.yml`

```yaml
name: _pulse_reusable

on:
  workflow_call:
    inputs:
      core_ref:
        description: "Git ref (tag/branch/SHA) of market-data-core"
        required: true
        type: string
      schema_track:
        description: "Schema track (v1|v2)"
        required: true
        type: string
      bus_backend:
        description: "Event bus backend (inmem|redis)"
        required: true
        type: string

jobs:
  pulse:
    runs-on: ubuntu-latest
    
    services:
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install Core @ ${{ inputs.core_ref }}
        run: |
          pip install -U pip wheel
          pip install "git+https://github.com/mjdevaccount/market-data-core.git@${{ inputs.core_ref }}"
          pip freeze | grep market-data-core
      
      - name: Install project + dev deps
        run: |
          pip install -e ".[dev]"
      
      - name: Run Pulse tests
        env:
          PULSE_ENABLED: "true"
          EVENT_BUS_BACKEND: ${{ inputs.bus_backend }}
          REDIS_URL: redis://localhost:6379/0
          SCHEMA_TRACK: ${{ inputs.schema_track }}
        run: |
          pytest tests/pulse/ -v --tb=short
      
      - name: Summary
        run: |
          echo "✅ Pulse tests passed"
          echo "- Core ref: ${{ inputs.core_ref }}"
          echo "- Schema track: ${{ inputs.schema_track }}"
          echo "- Backend: ${{ inputs.bus_backend }}"
```

### Step 5.2: Create `.github/workflows/dispatch_pulse.yml`

```yaml
name: dispatch_pulse

on:
  workflow_dispatch:
    inputs:
      core_ref:
        description: "Core ref (tag/branch/SHA)"
        required: true
        type: string

jobs:
  matrix:
    strategy:
      matrix:
        schema_track: [v1, v2]
        bus_backend: [inmem, redis]
    
    uses: ./.github/workflows/_pulse_reusable.yml
    with:
      core_ref: ${{ inputs.core_ref }}
      schema_track: ${{ matrix.schema_track }}
      bus_backend: ${{ matrix.bus_backend }}
```

---

## Phase 6: Runtime Wiring

### Step 6.1: Wire into `PipelineRuntime` (Option A)

**File**: `src/market_data_pipeline/orchestration/runtime.py`

In `PipelineRuntime.initialize()`:

```python
async def initialize(self) -> None:
    """Initialize runtime including Pulse consumer (Phase 10.1)."""
    if self._initialized:
        return
    
    # ... existing initialization ...
    
    # Phase 10.1: Start Pulse feedback consumer
    from ..pulse import PulseConfig, FeedbackConsumer
    from ..settings.feedback import PipelineFeedbackSettings
    
    pulse_cfg = PulseConfig()
    if pulse_cfg.enabled and self.rate_coordinator:
        feedback_settings = PipelineFeedbackSettings()
        
        # Wrap rate_coordinator with adapter if needed
        from ..orchestration.feedback.consumer import RateCoordinatorAdapter
        rate_controller = RateCoordinatorAdapter(self.rate_coordinator)
        
        consumer = FeedbackConsumer(rate_controller, feedback_settings, pulse_cfg)
        self._pulse_task = asyncio.create_task(consumer.run("pipeline_w1"))
        logger.info("[pulse] Feedback consumer started")
    
    self._initialized = True
```

In `PipelineRuntime.shutdown()` or `__aexit__`:

```python
async def shutdown(self) -> None:
    """Graceful shutdown including Pulse consumer."""
    # Cancel Pulse task
    if hasattr(self, "_pulse_task") and self._pulse_task:
        logger.info("[pulse] Cancelling feedback consumer...")
        self._pulse_task.cancel()
        try:
            await self._pulse_task
        except asyncio.CancelledError:
            pass
    
    # ... existing shutdown logic ...
```

### Step 6.2: Or wire into `RuntimeOrchestrator` (Option B)

**File**: `src/market_data_pipeline/orchestration/runtime_orchestrator.py`

Similar approach — start Pulse consumer task on initialization, cancel on shutdown.

---

## Phase 7: Documentation

### Step 7.1: Update `README.md`

Add Pulse section after Contract Tests:

```markdown
## Pulse Integration (Phase 10.1)

The Pipeline subscribes to `telemetry.feedback` events from the Store via the Pulse event bus.

### Configuration

Environment variables:
```bash
PULSE_ENABLED=true                     # Enable Pulse (default: true)
EVENT_BUS_BACKEND=inmem                # inmem or redis (default: inmem)
REDIS_URL=redis://localhost:6379/0     # Redis connection (if backend=redis)
MD_NAMESPACE=mdp                       # Stream namespace
SCHEMA_TRACK=v1                        # Schema track (v1|v2)
```

### Running Tests

```bash
# Unit tests (inmem backend)
pytest tests/pulse/test_pulse_consumer.py -v

# Integration tests (redis backend, requires Redis)
EVENT_BUS_BACKEND=redis REDIS_URL=redis://localhost:6379/0 \
  pytest tests/pulse/test_redis_integration.py -v
```

### Metrics

- `pulse_consume_total{stream,track,outcome}` — Events consumed (success/error/duplicate)
- `pulse_lag_ms{stream}` — Consumer lag from event timestamp
```

### Step 7.2: Update `CHANGELOG.md`

```markdown
## [Unreleased]

### Added
- **Phase 10.1**: Pulse event bus integration
  - New `pulse/` module for consuming `telemetry.feedback` events
  - Support for InMemory (dev/test) and Redis Streams (prod) backends
  - Idempotency, ACK/FAIL, DLQ support
  - CI matrix: schema track (v1/v2) × backend (inmem/redis)
  - Metrics: `pulse_consume_total`, `pulse_lag_ms`

### Changed
- Upgraded `market-data-core` from `>=1.1.1` to `>=1.2.0,<2.0.0`

### Dependencies
- `market-data-core>=1.2.0,<2.0.0` (Pulse support)
```

---

## Phase 8: Validation

### Step 8.1: Local Testing

```powershell
# 1. Activate venv
.\.venv\Scripts\activate

# 2. Install with Pulse support
pip install -e ".[dev]"

# 3. Run unit tests (inmem)
pytest tests/pulse/test_pulse_consumer.py -v

# 4. Run integration tests (requires Redis)
$env:EVENT_BUS_BACKEND="redis"
$env:REDIS_URL="redis://localhost:6379/0"
pytest tests/pulse/test_redis_integration.py -v

# 5. Run all tests
pytest tests/ -v
```

### Step 8.2: CI Validation

```powershell
# Trigger dispatch workflow
gh workflow run dispatch_pulse.yml -f core_ref=v1.2.0-pulse

# Watch run
gh run watch
```

Expected: 4 jobs pass (v1/inmem, v1/redis, v2/inmem, v2/redis)

### Step 8.3: Checklist

- [ ] Core upgraded to v1.2.0-pulse
- [ ] `pulse/` module created (config.py, consumer.py)
- [ ] Metrics added to `metrics.py`
- [ ] Unit tests pass (inmem)
- [ ] Integration tests pass (redis, if available)
- [ ] CI workflows created and green
- [ ] Runtime wired with graceful shutdown
- [ ] README updated
- [ ] CHANGELOG updated

---

## Phase 9: Release

### Step 9.1: Version Bump

Update `pyproject.toml`:

```toml
version = "1.0.0"  # Minor bump for Phase 10.1 features
```

### Step 9.2: Commit and Tag

```powershell
git add .
git commit -m "feat: Phase 10.1 - Pulse integration (feedback consumer)"
git tag v1.0.0
git push origin feat/phase-10.1-pulse
git push origin v1.0.0
```

### Step 9.3: Create PR

**Title**: `feat: Phase 10.1 - Pulse Integration (Feedback Consumer)`

**Description**: See template below.

---

## PR Description Template

```markdown
## Phase 10.1: Pulse Integration (Feedback Consumer)

### Summary
Integrates the new Pulse event bus system (Core v1.2.0) for consuming `telemetry.feedback` events from the Store.

### Changes
- ✅ Upgraded `market-data-core` to v1.2.0-pulse
- ✅ New `pulse/` module:
  - `config.py` — Environment-based configuration
  - `consumer.py` — Feedback event consumer (wraps existing `FeedbackHandler`)
- ✅ Metrics: `pulse_consume_total`, `pulse_lag_ms`
- ✅ Tests:
  - Unit tests (inmem backend)
  - Integration tests (redis backend, conditional)
- ✅ CI/CD:
  - `_pulse_reusable.yml` — Matrix tests (v1/v2 × inmem/redis)
  - `dispatch_pulse.yml` — Dispatch handler for Core fanout
- ✅ Runtime wiring with graceful shutdown

### Architecture
```
Store → Pulse.publish()
          ↓ (Redis Streams or InMemory)
Pipeline: FeedbackConsumer.run()
          → FeedbackHandler.handle() (reused!)
          → RateCoordinator.apply()
```

### Testing
- Unit tests: `pytest tests/pulse/test_pulse_consumer.py -v`
- Integration: `EVENT_BUS_BACKEND=redis pytest tests/pulse/test_redis_integration.py -v`
- CI matrix: All 4 combinations pass (v1/v2 × inmem/redis)

### Backward Compatibility
- ✅ 100% backward compatible
- ✅ InMemory backend works exactly like existing `FeedbackBus`
- ✅ All existing tests pass

### Deployment
- Default: `EVENT_BUS_BACKEND=inmem` (no Redis required)
- Production: Set `EVENT_BUS_BACKEND=redis` + `REDIS_URL`

### Metrics
- `pulse_consume_total{stream,track,outcome}` — Events consumed
- `pulse_lag_ms{stream}` — Consumer lag

### Docs
- Updated README with Pulse configuration and testing instructions
- Updated CHANGELOG with Phase 10.1 features
```

---

## Troubleshooting

### Issue: Core v1.2.0 not on PyPI

**Solution**: Install from git tag:
```powershell
pip install "git+https://github.com/mjdevaccount/market-data-core.git@v1.2.0-pulse"
```

### Issue: Redis tests fail in CI

**Check**: Redis service health in workflow (should be `healthy`)
**Fix**: Ensure `redis_url` matches service port mapping

### Issue: Metrics not exported

**Check**: `prometheus-client` installed?
**Fix**: Consumer gracefully degrades if metrics unavailable

### Issue: Consumer not starting

**Check**: `PULSE_ENABLED=true`?
**Check**: Runtime initialization wiring correct?
**Logs**: Look for `[pulse] Starting feedback consumer`

---

## Next Steps (Post-10.1)

1. **Phase 10.2**: Store publishes `FeedbackEvent` via Pulse (currently uses simple bus)
2. **Phase 10.3**: Orchestrator observes streams + publishes audit events
3. **Phase 11.0**: Schema registry service for drift detection

---

**Status**: Ready for implementation. All scaffolds provided. Estimated time: **2-3 hours**.

