# Phase 10.1 — Pulse Integration Viability Assessment

**Date**: 2025-10-18  
**Repo**: `market_data_pipeline`  
**Status**: ✅ VIABLE — Excellent foundation, clear upgrade path

---

## Executive Summary

Phase 10.1 integrates the new Pulse event bus system (from Core v1.2.0-pulse) into the Pipeline side as a **consumer** of `telemetry.feedback` events. This replaces the current simple in-memory pub-sub with a production-grade event fabric supporting Redis Streams, schema validation, at-least-once delivery, and DLQ.

**Verdict**: **HIGHLY VIABLE**
- ✅ Existing `FeedbackHandler` is production-ready and Core-compliant (Phase 8.0)
- ✅ Settings, metrics, and RateController integration already in place
- ✅ Clean separation: Pulse handles transport, FeedbackHandler handles business logic
- ✅ Backward compatible: InMemory backend works exactly like current `FeedbackBus`
- ⚠️ Minor: Need Core upgrade 1.1.1 → 1.2.0-pulse (non-breaking)

**Effort**: **2-3 hours**
- Core upgrade: 15 min
- Pulse module: 1 hour
- Tests: 1 hour
- CI/CD workflows: 30 min
- Documentation: 30 min

---

## Current State Analysis

### ✅ Strengths

1. **Phase 8.0 Foundation**
   - `FeedbackHandler` already uses Core DTOs (`FeedbackEvent`, `RateAdjustment`)
   - `RateCoordinatorAdapter` implements Core `RateController` protocol
   - `PipelineFeedbackSettings` provides complete policy configuration
   - Metrics already instrumented (`pulse_consume_total`, `rate_scale_current`)

2. **Clean Architecture**
   ```
   Current:  Store → FeedbackBus.publish() → FeedbackHandler.handle() → RateController.apply()
   Future:   Store → Pulse.publish()      → [same handler logic]  → [same controller]
   ```
   The business logic (`FeedbackHandler`) is **transport-agnostic** — perfect for Pulse integration.

3. **Existing Components to Reuse**
   - `src/market_data_pipeline/settings/feedback.py` — scales (ok/soft/hard)
   - `src/market_data_pipeline/orchestration/feedback/consumer.py` — transformation logic
   - `src/market_data_pipeline/orchestration/coordinator.py` — `RateCoordinator`

### ⚠️ Gaps to Address

1. **Pulse Integration Layer** (NEW)
   - Need `src/market_data_pipeline/pulse/` module with:
     - `config.py` — Environment-based Pulse configuration
     - `consumer.py` — Event bus subscriber that wraps `FeedbackHandler`

2. **Testing** (NEW)
   - `tests/pulse/test_pulse_consumer.py` — Unit tests (inmem backend)
   - `tests/pulse/test_redis_integration.py` — Integration tests (redis backend, skipped if no Redis)

3. **CI/CD** (NEW)
   - `.github/workflows/_pulse_reusable.yml` — Matrix tests (v1/v2 × inmem/redis)
   - `.github/workflows/dispatch_pulse.yml` — Dispatch handler for Core fanout

4. **Runtime Wiring** (MODIFY)
   - Wire `FeedbackConsumer.run()` into `PipelineRuntime` or `RuntimeOrchestrator`
   - Conditional start when `PULSE_ENABLED=true`

---

## Requirements Mapping

| Requirement | Status | Notes |
|-------------|--------|-------|
| **0) Core >=1.2.0** | ⚠️ TODO | Currently 1.1.1, need upgrade |
| **1) Pulse Config** | ✅ Scaffold | Env vars: `PULSE_ENABLED`, `EVENT_BUS_BACKEND`, `REDIS_URL`, `MD_NAMESPACE`, `SCHEMA_TRACK` |
| **2) Feedback Consumer** | ✅ Reuse | Wrap existing `FeedbackHandler` with Pulse subscriber loop |
| **3) Idempotency** | ⚠️ Simple | LRU cache or seen-set for `envelope.id` (best-effort) |
| **4) Metrics** | ✅ Existing | `pulse_consume_total`, `pulse_lag_ms`, `rate_scale_current` |
| **5) Tests** | ⚠️ TODO | Unit (inmem) + integration (redis, conditional) |
| **6) CI/CD** | ⚠️ TODO | Reusable + dispatch workflows, matrix (v1/v2 × inmem/redis) |
| **7) Runtime Wiring** | ⚠️ TODO | Start consumer task on `initialize()` |

---

## Technical Design

### Architecture

```
┌─────────────┐
│   Store     │  Publishes FeedbackEvent via Pulse
└──────┬──────┘
       │ (Redis Streams or InMemory)
       │ telemetry.feedback
       ▼
┌─────────────────────────────┐
│   Pipeline: FeedbackConsumer │
├─────────────────────────────┤
│ 1. Subscribe to stream      │
│ 2. Deserialize envelope     │
│ 3. Idempotency check        │
│ 4. Call FeedbackHandler     │  ← Reuse existing logic!
│ 5. ACK or FAIL              │
│ 6. Emit metrics (lag, count)│
└──────────┬──────────────────┘
           │
           ▼
    ┌───────────────┐
    │RateCoordinator│  Apply scale adjustment
    └───────────────┘
```

### Files to Create

```
src/market_data_pipeline/pulse/
├── __init__.py
├── config.py           # PulseConfig dataclass (env-based)
└── consumer.py         # FeedbackConsumer (wraps FeedbackHandler)

tests/pulse/
├── __init__.py
├── test_pulse_consumer.py         # Unit tests (inmem)
└── test_redis_integration.py      # Integration tests (redis, skipif)

.github/workflows/
├── _pulse_reusable.yml            # Matrix: schema_track × backend
└── dispatch_pulse.yml             # repository_dispatch handler
```

### Key Implementation Details

1. **PulseConfig** (`pulse/config.py`)
   ```python
   @dataclass(frozen=True)
   class PulseConfig:
       enabled: bool = os.getenv("PULSE_ENABLED", "true").lower() == "true"
       backend: str = os.getenv("EVENT_BUS_BACKEND", "inmem")
       redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
       ns: str = os.getenv("MD_NAMESPACE", "mdp")
       track: str = os.getenv("SCHEMA_TRACK", "v1")
   ```

2. **FeedbackConsumer** (`pulse/consumer.py`)
   - Wraps existing `FeedbackHandler` (no changes needed to handler!)
   - Adds idempotency via simple `seen_ids` set (LRU in prod)
   - Metrics: `pulse_consume_total{stream,track,outcome}`, `pulse_lag_ms`
   - ACK on success, FAIL on exception → DLQ

3. **Runtime Wiring** (modify `PipelineRuntime.initialize()`)
   ```python
   if PulseConfig().enabled:
       consumer = FeedbackConsumer(rate_controller, settings, cfg)
       self._pulse_task = asyncio.create_task(consumer.run("pipeline_w1"))
   ```

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Core upgrade breaks contracts** | 🟢 Low | v1.2.0 is backward-compatible (all additions), existing tests pass |
| **Redis unavailable in CI** | 🟡 Medium | Make Redis tests conditional (`pytest.mark.skipif`), matrix includes inmem |
| **Duplicate message processing** | 🟡 Medium | Simple idempotency (seen-set), RateController is idempotent by design (set scale) |
| **Lag spikes** | 🟡 Medium | Prometheus alerts, DLQ for failed messages, graceful degradation to inmem |
| **Runtime wiring complexity** | 🟢 Low | Clear entrypoint, asyncio task management, graceful shutdown |

---

## Testing Strategy

### Unit Tests (inmem backend)
- **test_pulse_consumer.py**
  - Given: FeedbackEvent published to inmem bus
  - When: Consumer processes event
  - Then: RateController.apply() called with correct scale
  - Assert: Idempotency (re-delivery doesn't double-apply)
  - Assert: Metrics incremented

### Integration Tests (redis backend)
- **test_redis_integration.py** (skipif no Redis)
  - Given: Redis running on localhost:6379
  - When: Publish FeedbackEvent via Pulse
  - Then: Consumer ACKs, DLQ remains empty
  - Assert: Lag < 100ms, scale applied

### CI Matrix
```yaml
matrix:
  schema_track: [v1, v2]
  bus_backend: [inmem, redis]
```
- 4 combinations per push
- Redis tests use `services: redis:7`

---

## Effort Estimation

| Task | Time | Difficulty |
|------|------|------------|
| 1. Core upgrade (1.1.1 → 1.2.0) | 15 min | 🟢 Trivial |
| 2. Create `pulse/config.py` | 10 min | 🟢 Trivial |
| 3. Create `pulse/consumer.py` | 30 min | 🟡 Moderate |
| 4. Unit tests (inmem) | 30 min | 🟡 Moderate |
| 5. Integration tests (redis) | 20 min | 🟡 Moderate |
| 6. CI workflows (_reusable + dispatch) | 30 min | 🟡 Moderate |
| 7. Runtime wiring | 20 min | 🟢 Easy |
| 8. Documentation (README, CHANGELOG) | 20 min | 🟢 Easy |
| **TOTAL** | **2h 35min** | 🟡 **Moderate** |

---

## Validation Checklist

### Pre-Implementation
- [x] Core v1.1.1 installed and working
- [x] Existing FeedbackHandler tests passing
- [x] RateCoordinator tests passing

### Implementation
- [ ] Core upgraded to v1.2.0-pulse
- [ ] `pulse/` module created with config + consumer
- [ ] Unit tests passing (inmem)
- [ ] Integration tests passing (redis, if available)
- [ ] CI workflows created and green
- [ ] Runtime wired with graceful shutdown

### Post-Implementation
- [ ] Dev: `EVENT_BUS_BACKEND=inmem` works (default)
- [ ] CI: Matrix passes (v1/v2 × inmem/redis)
- [ ] Staging: `EVENT_BUS_BACKEND=redis` works e2e
- [ ] Metrics: `pulse_lag_ms`, `pulse_consume_total` exported
- [ ] DLQ: Remains empty under normal operation

---

## Success Criteria

1. ✅ **Contracts preserved**: Existing tests pass after Core upgrade
2. ✅ **Transport agnostic**: InMemory works (dev/test), Redis works (prod)
3. ✅ **Metrics observable**: Lag, throughput, errors visible in Prometheus
4. ✅ **Idempotency**: Re-delivery doesn't cause double rate-adjustment
5. ✅ **CI green**: Matrix passes, fanout dispatch works
6. ✅ **Graceful degradation**: Pulse disabled → fallback to existing FeedbackBus

---

## Recommendations

### Immediate Actions
1. ✅ **Upgrade Core** → `market-data-core>=1.2.0,<2.0.0`
2. ✅ **Create Pulse module** → Scaffold config + consumer
3. ✅ **Add tests** → Unit (inmem) + integration (redis)
4. ✅ **Wire runtime** → Start consumer on `PipelineRuntime.initialize()`

### Future Enhancements (post-Phase 10.1)
- **Idempotency**: Replace seen-set with proper LRU cache (e.g., `cachetools`)
- **Fan-out**: Subscribe to multiple streams (e.g., `telemetry.audit`)
- **Rate publish**: Optionally publish `RateAdjustment` to `telemetry.rate_adjustment` for ops observability
- **Health checks**: Expose Pulse consumer health at `/health` endpoint

---

## Conclusion

**Phase 10.1 is HIGHLY VIABLE** with minimal risk. The existing Phase 8.0 architecture provides an excellent foundation — the business logic (`FeedbackHandler`, `RateController`) is transport-agnostic and production-ready. Pulse integration is a clean **wrapper** around existing components.

**Recommendation**: **PROCEED** with implementation. Expected completion: **1 session (2-3 hours)**.

---

**Next**: Create `PHASE_10.1_IMPLEMENTATION_PLAN.md` with detailed code scaffolds and step-by-step execution plan.

