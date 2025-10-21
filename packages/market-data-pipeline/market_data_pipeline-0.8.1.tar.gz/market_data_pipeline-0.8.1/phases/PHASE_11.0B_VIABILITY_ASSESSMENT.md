# Phase 11.0B — Schema Registry Integration Viability Assessment

**Date**: 2025-10-18  
**Repo**: `market_data_pipeline`  
**Core Status**: v1.2.0-pulse + v1.2.1-registry-test (Phase 11.0B complete)  
**Pipeline Status**: v1.0.0 (Phase 10.1 complete)

---

## Executive Summary

**Verdict**: ⚠️ **VIABLE BUT DEFER**

Phase 11.0B integration is **technically viable** but should be **deferred** to allow:
1. ✅ Core Registry Service deployment and stabilization
2. ✅ Pipeline v1.0.0 production validation
3. ✅ Client SDK publication and availability
4. ✅ Store/Orchestrator to integrate first (they publish schemas)

**Recommended Timeline**: Start Phase 11.0B for Pipeline in **2-3 weeks** after:
- Registry Service is deployed and stable
- `core-registry-client` SDK is published
- At least one upstream service (Store or Orchestrator) has integrated

---

## Current State Analysis

### ✅ Pipeline Strengths

1. **Recent Phase 10.1 Success**
   - Just shipped v1.0.0 with Pulse integration
   - All 207 tests passing
   - Production-ready architecture
   - Strong contract testing foundation

2. **Existing Contract Infrastructure**
   - `tests/contracts/` suite (10 tests)
   - CI workflows for contract testing
   - Clear schema boundaries (FeedbackEvent, RateAdjustment)
   - GitHub Actions matrix testing

3. **Clean Architecture**
   - Well-defined DTOs from Core
   - Protocol-based interfaces
   - Graceful degradation patterns
   - Comprehensive metrics

### ⚠️ Current Gaps

1. **Registry Service Not Deployed**
   - No production Registry URL available
   - Test tag created, but service not live
   - Need `REGISTRY_URL` and `REGISTRY_TOKEN` secrets

2. **Client SDK Not Published**
   - `core-registry-client` not on PyPI
   - Would need git installation (like Core v1.2.0)
   - No versioned releases yet

3. **Just Shipped v1.0.0**
   - Need production validation period
   - Too soon for another major feature
   - Risk of destabilizing fresh release

4. **Dependency Order**
   - Store publishes FeedbackEvent → Should integrate first
   - Pipeline consumes → Should integrate after Store
   - Orchestrator observes → Can integrate in parallel

---

## Requirements Mapping

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Registry Service Deployed** | ❌ Not Ready | Test artifacts only, no live service |
| **Client SDK Available** | ⚠️ Partial | Code exists but not published |
| **CI/CD Patterns** | ✅ Ready | Have contract test workflows |
| **Runtime Validation** | ✅ Ready | Have validation patterns from Phase 8.0 |
| **Schema Caching** | ✅ Ready | Have caching patterns from Pulse |
| **Monitoring** | ✅ Ready | Have Prometheus metrics |
| **V1/V2 Migration** | ✅ Ready | Pulse already supports v1/v2 tracks |

---

## Technical Feasibility

### ✅ Technically Feasible

1. **Client SDK Integration**: Straightforward dependency addition
2. **CI Schema Fetch**: Similar to existing contract test patterns
3. **Runtime Manager**: Can reuse Pulse caching patterns
4. **Validation Middleware**: Standard FastAPI middleware (if needed)
5. **Monitoring**: Extend existing Prometheus metrics

### ⚠️ Blockers

1. **Registry Service URL**: No production endpoint
2. **Client SDK Package**: Not on PyPI yet
3. **Upstream Dependency**: Store hasn't published schemas to Registry yet
4. **Fresh Release**: v1.0.0 just shipped, need stabilization period

---

## Integration Effort Estimate

### If Started Today (with blockers)

| Task | Time | Difficulty | Blocked? |
|------|------|------------|----------|
| Install client SDK | 30 min | 🟢 Easy | ⚠️ Not published |
| Add configuration | 30 min | 🟢 Easy | ❌ No Registry URL |
| Create schema manager | 2 hours | 🟡 Medium | ❌ No service |
| Update CI/CD | 1 hour | 🟡 Medium | ❌ No schemas yet |
| Add contract tests | 2 hours | 🟡 Medium | ❌ Need Store schemas |
| Runtime integration | 2 hours | 🟡 Medium | ✅ Can prep |
| Testing & validation | 2 hours | 🟡 Medium | ❌ Need live Registry |
| Documentation | 1 hour | 🟢 Easy | ✅ Ready |
| **TOTAL** | **11 hours** | 🟡 **Medium** | **⚠️ 70% blocked** |

### When Ready (post-stabilization)

| Task | Time | Difficulty | Blocked? |
|------|------|------------|----------|
| Install client SDK | 15 min | 🟢 Easy | ✅ Published |
| Add configuration | 30 min | 🟢 Easy | ✅ Registry live |
| Create schema manager | 1.5 hours | 🟡 Medium | ✅ Service stable |
| Update CI/CD | 45 min | 🟢 Easy | ✅ Schemas available |
| Add contract tests | 1.5 hours | 🟡 Medium | ✅ Store integrated |
| Runtime integration | 2 hours | 🟡 Medium | ✅ Ready |
| Testing & validation | 1 hour | 🟢 Easy | ✅ E2E possible |
| Documentation | 1 hour | 🟢 Easy | ✅ Ready |
| **TOTAL** | **8.5 hours** | 🟡 **Medium** | **✅ 0% blocked** |

---

## Architecture Preview

### Proposed Integration

```
Pipeline Runtime
    │
    ├─ Startup
    │   ├─ Initialize SchemaRegistryManager
    │   ├─ Preload critical schemas:
    │   │   ├─ telemetry.FeedbackEvent (v2 preferred, v1 fallback)
    │   │   └─ telemetry.RateAdjustment (v2 preferred, v1 fallback)
    │   └─ Cache with 5-minute TTL
    │
    ├─ CI/CD
    │   ├─ Fetch schemas from Registry
    │   ├─ Run contract tests (v1 + v2 matrix)
    │   └─ Validate compatibility
    │
    └─ Runtime (Pulse Consumer)
        ├─ Receive FeedbackEvent from Pulse
        ├─ Validate against Registry schema (cached)
        ├─ Log validation results
        └─ Process event (existing logic)
```

### Files to Create

```
src/market_data_pipeline/
├── schemas/
│   ├── __init__.py
│   ├── registry_manager.py    # Schema fetch/cache/validation
│   └── cache.py                # Schema cache with TTL

scripts/
└── fetch_schemas.py            # CI schema fetch tool

tests/contracts/
├── test_registry_schemas.py    # Registry schema tests
└── fixtures/
    └── payloads/               # Sample payloads for testing

.github/workflows/
└── contract-registry-tests.yml # Registry-based contract tests
```

### Minimal Changes Required

- ✅ **No changes to existing FeedbackHandler** (already uses Core DTOs)
- ✅ **No changes to Pulse consumer** (validation is optional layer)
- ✅ **No changes to RateCoordinator** (protocol-based)
- ✅ **Additive only** (new module, no breaking changes)

---

## Risk Assessment

| Risk | Severity | Likelihood | Mitigation |
|------|----------|------------|------------|
| **Registry Service Downtime** | 🟡 Medium | 🟡 Medium | Graceful degradation to local schemas |
| **Schema Version Conflicts** | 🟢 Low | 🟢 Low | v1/v2 negotiation, fallback logic |
| **Performance Impact** | 🟢 Low | 🟢 Low | Aggressive caching, preload at startup |
| **Breaking v1.0.0** | 🔴 High | 🟢 Low | Wait for production stabilization |
| **Dependency on Store** | 🟡 Medium | 🟡 Medium | Store must integrate first |
| **Client SDK Issues** | 🟡 Medium | 🟡 Medium | Wait for SDK publication + validation |

---

## Recommendations

### ✅ DO NOW (Preparation)

1. **Monitor v1.0.0 in Production**
   - Collect metrics from Pulse integration
   - Validate stability over 1-2 weeks
   - Address any production issues

2. **Review Registry Integration Guide**
   - Understand patterns and best practices
   - Identify alignment with existing architecture
   - Plan integration approach

3. **Track Registry Service Deployment**
   - Watch for Registry production URL
   - Monitor `core-registry-client` PyPI publication
   - Track Store/Orchestrator integration progress

4. **Prepare Infrastructure**
   - Document current schema usage
   - Identify critical schemas (FeedbackEvent, RateAdjustment)
   - Plan caching strategy

### ❌ DON'T DO YET

1. **Don't Start Integration**
   - Registry Service not deployed
   - Client SDK not published
   - Too soon after v1.0.0 release

2. **Don't Add Dependencies**
   - `core-registry-client` not available yet
   - Would create broken build

3. **Don't Change Contract Tests**
   - Current tests work well
   - No regression needed

### ⏰ START WHEN (2-3 Weeks)

**Prerequisites Met**:
- ✅ Registry Service deployed and stable
- ✅ `core-registry-client` published to PyPI
- ✅ Pipeline v1.0.0 validated in production
- ✅ Store has integrated Registry (publishes FeedbackEvent schemas)
- ✅ At least 1 week of Registry uptime metrics

**Trigger Events**:
- Core team announces Registry production deployment
- Store team completes Phase 11.0B integration
- Client SDK v0.1.0 published

---

## Phased Rollout Plan (When Ready)

### Phase 1: CI/CD Only (Week 1)
**Goal**: Fetch schemas in CI, no runtime changes

```yaml
# Add to existing contract tests workflow
- name: Fetch schemas from Registry
  run: |
    pip install core-registry-client
    python scripts/fetch_schemas.py --track v2 --output tests/fixtures/schemas/

- name: Run contract tests
  run: pytest tests/contracts/ --track=v2
```

**Validation**:
- ✅ CI fetches schemas successfully
- ✅ Contract tests pass against Registry schemas
- ✅ No changes to runtime behavior

### Phase 2: Runtime Read-Only (Week 2)
**Goal**: Fetch schemas at startup, log validation results

```python
# Add to PipelineRuntime.initialize()
from ..schemas.registry_manager import schema_manager

# Preload critical schemas
await schema_manager.get_schema("telemetry.FeedbackEvent", prefer="v2", fallback="v1")
await schema_manager.get_schema("telemetry.RateAdjustment", prefer="v2", fallback="v1")
```

**Validation**:
- ✅ Schemas load at startup
- ✅ Cache populated
- ✅ No validation enforcement (log only)
- ✅ Monitor cache hit rates

### Phase 3: Soft Validation (Week 3)
**Goal**: Validate payloads, log failures, don't reject

```python
# In Pulse consumer
async def _handle(self, envelope):
    # Validate against Registry schema
    is_valid, errors = await schema_manager.validate_payload(
        "telemetry.FeedbackEvent",
        envelope.payload.model_dump(),
        prefer="v2",
        fallback="v1"
    )
    
    if not is_valid:
        logger.warning(f"Schema validation failed: {errors}")
        # Emit metric
        SCHEMA_VALIDATION_FAILURES.labels(schema="FeedbackEvent").inc()
    
    # Process anyway (existing logic)
    await self.handler.handle(envelope.payload)
```

**Validation**:
- ✅ All payloads validated
- ✅ Failures logged and metrics emitted
- ✅ No functional impact (still process invalid payloads)
- ✅ Monitor validation failure rates

### Phase 4: Full Enforcement (Week 4+)
**Goal**: Reject invalid payloads, force v2 adoption

```python
async def _handle(self, envelope):
    is_valid, errors = await schema_manager.validate_payload(...)
    
    if not is_valid:
        logger.error(f"Invalid schema, rejecting: {errors}")
        # FAIL to DLQ
        await self.bus.fail(stream, envelope.id, f"Schema validation failed: {errors}")
        return  # Don't process
    
    # Only process valid payloads
    await self.handler.handle(envelope.payload)
```

**Validation**:
- ✅ Invalid payloads rejected
- ✅ DLQ captures validation failures
- ✅ Strict v2 enforcement
- ✅ v1 deprecated (warn + metrics)

---

## Success Criteria (When Integrated)

- ✅ CI fetches schemas from Registry (not Core repo)
- ✅ Contract tests pass against Registry schemas (v1 + v2)
- ✅ Runtime validates payloads against v2 schemas
- ✅ Graceful fallback to v1 works
- ✅ Cache hit rate >95%
- ✅ Schema fetch latency <100ms (p95)
- ✅ No production incidents from schema changes
- ✅ <1% performance impact from validation

---

## Alternative Approaches

### Option A: Wait for Registry Service (RECOMMENDED)
**Timeline**: Start in 2-3 weeks  
**Pros**: Clean integration, no workarounds, proper testing  
**Cons**: Delayed benefits, miss early adopter insights

### Option B: Start with Local Schemas
**Timeline**: Start now  
**Pros**: Prepare codebase, test patterns  
**Cons**: Throwaway work, no real Registry integration, confusing

### Option C: Minimal CI-Only Integration
**Timeline**: Start in 1 week (when SDK published)  
**Pros**: Low risk, CI benefits only  
**Cons**: No runtime benefits, partial solution

---

## Dependencies

### Upstream (Blockers)
1. **Core Team**:
   - ❌ Deploy Registry Service to production
   - ❌ Publish `core-registry-client` to PyPI
   - ❌ Provide production `REGISTRY_URL`

2. **Store Team**:
   - ❌ Integrate Phase 11.0B (Store publishes FeedbackEvent schemas)
   - ❌ Validate Registry integration

### Downstream (Enabled By This)
- ✅ Orchestrator can integrate in parallel (observes, doesn't publish)
- ✅ Future services can follow same pattern

---

## Open Questions

1. **Registry Service Timeline**: When will production deployment happen?
2. **Client SDK Publication**: When will `core-registry-client` be on PyPI?
3. **Store Integration**: What's the Store team's timeline for Phase 11.0B?
4. **Schema Versions**: Are v2 schemas finalized or still in preview?
5. **Performance SLAs**: What are Registry Service latency guarantees?
6. **Fallback Strategy**: If Registry is down, use bundled schemas or fail?

---

## Conclusion

**Phase 11.0B integration is VIABLE but should be DEFERRED** until:

1. ✅ **Registry Service is deployed and stable** (production URL available)
2. ✅ **Client SDK is published** (`core-registry-client` on PyPI)
3. ✅ **Pipeline v1.0.0 is validated** (1-2 weeks in production)
4. ✅ **Store has integrated** (FeedbackEvent schemas available in Registry)

**Recommended Action**: 
- **Now**: Monitor v1.0.0, track Registry deployment, review integration guide
- **In 2-3 weeks**: Start Phase 11.0B integration when prerequisites met
- **Integration Time**: ~8.5 hours (when unblocked)

**Status**: ⚠️ **VIABLE BUT NOT READY** — Defer to allow ecosystem maturity

---

## Appendix: Integration Checklist (When Ready)

### Pre-Integration
- [ ] Registry Service deployed and accessible
- [ ] `REGISTRY_URL` secret configured in GitHub
- [ ] `core-registry-client` published to PyPI
- [ ] Store has published FeedbackEvent schemas to Registry
- [ ] Pipeline v1.0.0 stable in production (>1 week)

### Integration Phase 1 (CI/CD)
- [ ] Install `core-registry-client` in `pyproject.toml`
- [ ] Create `scripts/fetch_schemas.py`
- [ ] Update `.github/workflows/contract-registry-tests.yml`
- [ ] Add contract tests for Registry schemas
- [ ] CI fetches schemas and tests pass

### Integration Phase 2 (Runtime Prep)
- [ ] Create `src/market_data_pipeline/schemas/registry_manager.py`
- [ ] Add schema caching with TTL
- [ ] Preload schemas at startup
- [ ] Add monitoring metrics

### Integration Phase 3 (Soft Validation)
- [ ] Add validation to Pulse consumer (log only)
- [ ] Monitor validation results
- [ ] Tune cache TTL
- [ ] Verify no performance impact

### Integration Phase 4 (Full Enforcement)
- [ ] Enable validation rejection
- [ ] DLQ captures invalid payloads
- [ ] Deprecate v1 schemas
- [ ] Monitor production metrics

### Post-Integration
- [ ] Update documentation
- [ ] Create runbook for Registry issues
- [ ] Share lessons learned with Orchestrator team
- [ ] Tag release (v1.1.0)

---

**Next Steps**: Monitor Registry Service deployment and Client SDK publication. Revisit this assessment when prerequisites are met.

