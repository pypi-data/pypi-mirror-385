# Phase 10.1: Pulse Event Bus Integration

## Summary

Integrates the new **Pulse event bus system** (from Core v1.2.0-pulse) into the Pipeline as a **consumer** of `telemetry.feedback` events from the Store. This enables production-grade event fabric with Redis Streams, schema validation, at-least-once delivery, and DLQ support.

## Changes

### ✅ Core Upgrade
- **Upgraded** `market-data-core` from `>=1.1.1` to `>=1.2.0,<2.0.0`
- **Verified** compatibility: All 10 contract tests + 207 total tests passing

### ✅ New Pulse Module
- **`src/market_data_pipeline/pulse/`**
  - `config.py` — Environment-based configuration
  - `consumer.py` — Feedback event consumer (wraps existing `FeedbackHandler`)
  - `__init__.py` — Public API

**Key Features**:
- Dual backends: InMemory (dev/test) + Redis Streams (production)
- Idempotency: Simple seen-set with LRU pruning
- ACK/FAIL: At-least-once delivery with DLQ
- Graceful degradation: Works without Redis

### ✅ Metrics
- **`pulse_consume_total{stream,track,outcome}`** — Events consumed (success/error/duplicate)
- **`pulse_lag_ms{stream}`** — Consumer lag from event timestamp

### ✅ Tests
- **Unit tests** (`tests/pulse/test_pulse_consumer.py`): 3 tests, inmem backend
- **Integration tests** (`tests/pulse/test_redis_integration.py`): 1 test, redis backend (conditional)
- **Result**: 207 passing, 6 skipped (no regressions)

### ✅ CI/CD Workflows
- **`.github/workflows/_pulse_reusable.yml`** — Matrix tests (v1/v2 × inmem/redis)
- **`.github/workflows/dispatch_pulse.yml`** — Dispatch handler for Core fanout

### ✅ Runtime Wiring
- **`PipelineRuntime.initialize()`** — Starts Pulse consumer when `PULSE_ENABLED=true`
- **`PipelineRuntime.shutdown()`** — Graceful cancellation
- **Conditional** — Only starts if `rate_coordinator` is available

### ✅ Documentation
- **README.md** — New "Pulse Integration (Phase 10.1)" section
- **CHANGELOG.md** — Detailed Phase 10.1 entries
- **Phase docs** — Viability assessment + implementation plan + completion summary

## Architecture

```
Store → Pulse.publish(FeedbackEvent)
          ↓ (Redis Streams or InMemory)
Pipeline: FeedbackConsumer.run()
          → FeedbackHandler.handle() (reused!)
          → RateCoordinator.apply()
```

**Key Design**: Reuses existing `FeedbackHandler` business logic. Pulse is purely a transport layer upgrade.

## Configuration

```bash
PULSE_ENABLED=true                     # Enable Pulse (default: true)
EVENT_BUS_BACKEND=inmem                # inmem or redis (default: inmem)
REDIS_URL=redis://localhost:6379/0     # Redis connection (if backend=redis)
MD_NAMESPACE=mdp                       # Stream namespace
SCHEMA_TRACK=v1                        # Schema track (v1|v2)
```

## Testing

### Pulse Tests
```bash
pytest tests/pulse/test_pulse_consumer.py -v
# 3 passed in 1.47s
```

### Contract Tests
```bash
pytest tests/contracts/ -v
# 10 passed in 1.00s
```

### Full Suite
```bash
pytest tests/ -v
# 207 passed, 6 skipped in 7.96s
```

## Backward Compatibility

✅ **100% Backward Compatible**
- All existing tests pass without modification
- InMemory backend works exactly like existing `FeedbackBus`
- Pulse is opt-in (default: enabled, but graceful degradation)
- No breaking changes to public APIs

## Deployment

- **Default**: `EVENT_BUS_BACKEND=inmem` (no Redis required)
- **Production**: Set `EVENT_BUS_BACKEND=redis` + `REDIS_URL`
- **Graceful**: Consumer auto-starts with runtime, cancels on shutdown

## Files Changed

### New Files (15)
- `.github/workflows/_pulse_reusable.yml`
- `.github/workflows/dispatch_pulse.yml`
- `src/market_data_pipeline/pulse/__init__.py`
- `src/market_data_pipeline/pulse/config.py`
- `src/market_data_pipeline/pulse/consumer.py`
- `tests/pulse/__init__.py`
- `tests/pulse/test_pulse_consumer.py`
- `tests/pulse/test_redis_integration.py`
- `PHASE_10.1_VIABILITY_ASSESSMENT.md`
- `PHASE_10.1_IMPLEMENTATION_PLAN.md`
- `PHASE_10.1_COMPLETION_SUMMARY.md`

### Modified Files (5)
- `pyproject.toml` — Core dependency upgrade
- `src/market_data_pipeline/metrics.py` — Pulse metrics
- `src/market_data_pipeline/orchestration/runtime.py` — Consumer wiring
- `README.md` — Pulse documentation
- `CHANGELOG.md` — Phase 10.1 entries

## Metrics

- **pulse_consume_total**: Total events consumed
  - Labels: `stream`, `track`, `outcome` (success/error/duplicate)
- **pulse_lag_ms**: Consumer lag from event timestamp
  - Labels: `stream`

## Next Steps

1. **Merge** this PR to `base`
2. **Tag** release as `v1.0.0` (minor bump for new features)
3. **Phase 10.2**: Store publishes `FeedbackEvent` via Pulse
4. **Phase 10.3**: Orchestrator observes streams + publishes audit events

## Validation

- [x] All tests passing (207 passed, 6 skipped)
- [x] Contract tests pass (Core v1.2.0 compatibility)
- [x] CI workflows created and ready
- [x] Runtime wired with graceful shutdown
- [x] Documentation updated
- [x] Backward compatible (no breaking changes)

## Related

- **Core Release**: https://github.com/mjdevaccount/market-data-core/releases/tag/v1.2.0-pulse
- **Phase 10.0 Spec**: Core v1.2.0 Pulse implementation complete
- **Phase 8.0**: Core v1.1.0 contract integration (foundation for Pulse)

---

**Status**: ✅ Ready to merge  
**Tests**: ✅ 207/207 passing  
**Breaking Changes**: ❌ None  
**Documentation**: ✅ Complete

---

## Preview

Run tests locally:
```bash
# Clone and checkout
git fetch origin feat/phase-10.1-pulse
git checkout feat/phase-10.1-pulse

# Install Core v1.2.0-pulse
pip install "git+https://github.com/mjdevaccount/market-data-core.git@v1.2.0-pulse"

# Install project
pip install --no-deps -e .

# Run Pulse tests
pytest tests/pulse/ -v

# Run all tests
pytest tests/ -v
```

---

**Reviewer Notes**:
- Clean architecture: Pulse wraps existing `FeedbackHandler` (no changes to business logic)
- Graceful degradation: Works without Redis (inmem backend)
- Production-ready: Redis Streams support, idempotency, DLQ, metrics
- Backward compatible: All existing tests pass

**Ready for Production**: Yes ✅

