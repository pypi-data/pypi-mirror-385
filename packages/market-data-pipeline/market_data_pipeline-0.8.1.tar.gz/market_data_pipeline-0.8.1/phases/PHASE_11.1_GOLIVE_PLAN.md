# Phase 11.1 — Go-Live Plan: Pipeline Repository

**Date**: 2025-10-18  
**Repository**: `market_data_pipeline`  
**Phase**: 11.1 Enforcement & Drift Intelligence  
**Status**: ✅ **READY FOR GO-LIVE**

---

## Executive Summary

This document outlines the go-live plan for Phase 11.1 enforcement and drift intelligence in the Pipeline repository. The rollout follows a **fail-safe, gradual approach** with clear exit criteria and rollback procedures.

**Timeline**: 2 weeks  
**Risk Level**: Low (fail-open by default)  
**Current Status**: All prerequisites complete

---

## Prerequisites ✅

### Code & Configuration
- [x] ✅ Enforcement modes implemented (warn/strict)
- [x] ✅ SchemaValidationError exception
- [x] ✅ Configuration with `REGISTRY_ENFORCEMENT`
- [x] ✅ Metrics integration (Prometheus)
- [x] ✅ Pulse consumer DLQ integration
- [x] ✅ Tests (7/7 passing)

### Dependencies
- [x] ✅ `core-registry-client==0.2.0` specified
- [x] ✅ `market-data-core>=1.2.0`

### CI/CD
- [x] ✅ Enforcement matrix workflow
- [x] ✅ Contracts enforcement workflow
- [x] ✅ Nightly validation runs

### Documentation
- [x] ✅ Enforcement modes guide
- [x] ✅ Alert rules
- [x] ✅ Implementation docs

---

## Rollout Strategy (2 Weeks)

### Week 1: Warn Mode Everywhere

| Days | Stage | Action | Exit Criteria |
|------|-------|--------|---------------|
| **Day 1-3** | **Staging Deploy** | Deploy with `REGISTRY_ENFORCEMENT=warn` | - No errors in logs<br>- Metrics available<br>- Validation rate baseline established |
| **Day 4-5** | **Production Deploy** | Deploy with `REGISTRY_ENFORCEMENT=warn` | - Validation failure rate < 2%<br>- No user-facing issues<br>- 48h stable operation |
| **Day 6-7** | **CI Strict Mode** | Enable `REGISTRY_ENFORCEMENT=strict` in CI only | - CI green for 48 hours<br>- Test fixtures valid<br>- No unexpected failures |

### Week 2: Strict Mode in Production

| Days | Stage | Action | Exit Criteria |
|------|-------|--------|---------------|
| **Day 8-9** | **Pre-Strict Validation** | Verify warn mode metrics | - Failure rate < 0.5% for 72h<br>- All schemas passing<br>- DLQ monitoring active |
| **Day 10** | **Strict Mode (Staging)** | Enable strict in staging | - No unexpected rejections<br>- DLQ working correctly<br>- 24h stable |
| **Day 11-14** | **Strict Mode (Production)** | Enable strict in production | - Rejection rate < 0.1%<br>- DLQ depth normal<br>- No user impact |

---

## Configuration Changes

### Current (Phase 11.0B)
```bash
REGISTRY_ENABLED=false
REGISTRY_URL=https://registry.openbb.co/api/v1
REGISTRY_ENFORCEMENT=warn  # Not in use yet
```

### Week 1 (Go-Live)
```bash
REGISTRY_ENABLED=true
REGISTRY_URL=https://schema-registry-service.fly.dev
REGISTRY_TRACK=v1
REGISTRY_ENFORCEMENT=warn  # Log failures, continue
REGISTRY_POLL_SECONDS=60
```

### Week 2 (Strict Mode)
```bash
REGISTRY_ENABLED=true
REGISTRY_URL=https://schema-registry-service.fly.dev
REGISTRY_TRACK=v1
REGISTRY_ENFORCEMENT=strict  # Reject invalid payloads
REGISTRY_POLL_SECONDS=60
```

---

## Day-by-Day Checklist

### Day 1: Deploy to Staging (Warn Mode)

#### Pre-Deployment
- [ ] Verify `core-registry-client==0.2.0` installed
- [ ] Confirm registry service is accessible
- [ ] Review alert rules in Grafana
- [ ] Brief on-call team

#### Deployment
```bash
# Set environment
export REGISTRY_ENABLED=true
export REGISTRY_URL=https://schema-registry-service.fly.dev
export REGISTRY_TRACK=v1
export REGISTRY_ENFORCEMENT=warn
export REGISTRY_POLL_SECONDS=60

# Deploy
git pull origin base
pip install -e .
systemctl restart pipeline-service
```

#### Post-Deployment Validation
- [ ] Check service health: `curl http://localhost:8080/health`
- [ ] Verify metrics available:
  ```bash
  curl http://localhost:8080/metrics | grep schema_validation
  ```
- [ ] Review logs for registry connection:
  ```bash
  tail -f /var/log/pipeline.log | grep "\[registry\]"
  ```
- [ ] Monitor for 4 hours

#### Success Criteria
- ✅ Service starts successfully
- ✅ Registry connection established
- ✅ Metrics show validation attempts
- ✅ No errors in logs

---

### Days 2-3: Monitor Staging (Warn Mode)

#### Monitoring Queries
```promql
# Validation rate
rate(schema_validation_total[5m])

# Failure rate
rate(schema_validation_failures_total{mode="warn"}[5m])

# Cache performance
schema_cache_hits_total / (schema_cache_hits_total + schema_cache_misses_total)

# Registry errors
rate(schema_registry_errors_total[5m])
```

#### Daily Checks
- [ ] Review validation failure logs
- [ ] Check validation success rate (target: > 98%)
- [ ] Verify cache hit rate (target: > 95%)
- [ ] Document any schema mismatches

#### Exit Criteria
- ✅ Validation failure rate < 2% for 48 hours
- ✅ No registry connection issues
- ✅ Cache performing well (> 95% hit rate)
- ✅ Ready for production

---

### Days 4-5: Deploy to Production (Warn Mode)

#### Pre-Deployment
- [ ] Staging metrics reviewed and acceptable
- [ ] On-call engineer briefed
- [ ] Rollback plan reviewed
- [ ] Communication sent to team

#### Deployment (Low-Traffic Window)
```bash
# Deploy during low-traffic period
# Recommended: 2-4 AM UTC

export REGISTRY_ENABLED=true
export REGISTRY_URL=https://schema-registry-service.fly.dev
export REGISTRY_TRACK=v1
export REGISTRY_ENFORCEMENT=warn

# Deploy with canary
kubectl set env deployment/pipeline \
  REGISTRY_ENABLED=true \
  REGISTRY_ENFORCEMENT=warn

# Monitor canary for 30 minutes
kubectl rollout status deployment/pipeline
```

#### Post-Deployment (First 2 Hours)
- [ ] Monitor validation metrics every 15 minutes
- [ ] Check error rate (should be near zero)
- [ ] Verify DLQ is empty (warn mode doesn't use DLQ)
- [ ] Review user-facing metrics (no degradation)

#### Success Criteria
- ✅ Validation failure rate < 2%
- ✅ No increase in error rate
- ✅ User-facing metrics unchanged
- ✅ 48 hours stable operation

---

### Days 6-7: Enable Strict Mode in CI

#### Changes Required
Already done in `contracts_enforcement.yml`:
```yaml
strategy:
  matrix:
    mode: [warn, strict]  # Strict enabled in CI
```

#### Validation
- [ ] CI runs successfully with strict mode
- [ ] Test fixtures pass validation
- [ ] No unexpected failures
- [ ] 48 hours of green CI

#### Success Criteria
- ✅ CI green for 48 hours
- ✅ All test fixtures valid against registry schemas
- ✅ No schema version conflicts

---

### Day 8-9: Pre-Strict Validation

#### Metrics Review
```promql
# Must be < 0.5% for 72 hours
rate(schema_validation_failures_total{mode="warn"}[1h]) 
/ rate(schema_validation_total[1h])
```

#### Checklist
- [ ] Validation failure rate < 0.5% for 72 hours
- [ ] All identified issues fixed and deployed
- [ ] DLQ monitoring configured
- [ ] Alert rules tested
- [ ] Rollback plan ready

#### Go/No-Go Decision
**GO if**:
- ✅ Failure rate < 0.5%
- ✅ All schemas validating correctly
- ✅ Team ready and briefed

**NO-GO if**:
- ❌ Failure rate > 1%
- ❌ Unresolved schema issues
- ❌ Registry instability

---

### Day 10: Enable Strict Mode in Staging

#### Deployment
```bash
export REGISTRY_ENFORCEMENT=strict

# Restart service
systemctl restart pipeline-service
```

#### Intensive Monitoring (First 4 Hours)
```bash
# Watch rejections in real-time
watch -n 10 'curl -s http://localhost:8080/metrics | grep schema_validation_failures'

# Monitor DLQ
kubectl logs -f -l app=dlq-processor

# Check rejection rate
# Target: < 0.1%
```

#### Validation Checks
- [ ] Rejection rate < 0.1%
- [ ] DLQ receiving rejected messages correctly
- [ ] Valid messages processing normally
- [ ] No user-facing errors

#### Success Criteria
- ✅ Rejection rate < 0.1% for 24 hours
- ✅ DLQ functioning correctly
- ✅ No unexpected behavior

---

### Days 11-14: Enable Strict Mode in Production

#### Pre-Deployment Final Check
- [ ] Staging strict mode successful for 24+ hours
- [ ] Rejection rate acceptable (< 0.1%)
- [ ] DLQ capacity verified
- [ ] Team and on-call briefed
- [ ] Communication prepared

#### Deployment Strategy: Gradual Rollout
```bash
# Phase 1: 10% of pods (30 minutes)
kubectl patch deployment pipeline -p '{"spec":{"replicas":10}}'
# Set 1 pod to strict mode
kubectl set env deployment/pipeline REGISTRY_ENFORCEMENT=strict --dry-run
# Monitor for 30 min

# Phase 2: 50% of pods (1 hour)
# If Phase 1 successful, enable on 5 pods
# Monitor for 1 hour

# Phase 3: 100% of pods (2 hours)
# If Phase 2 successful, enable on all pods
kubectl set env deployment/pipeline REGISTRY_ENFORCEMENT=strict
```

#### Monitoring (24/7 for First 48 Hours)
```promql
# Critical metrics
rate(schema_validation_failures_total{mode="strict"}[15m])
rate(schema_enforcement_actions_total{severity="error"}[15m])

# Watch rejection rate
(
  rate(schema_validation_failures_total{mode="strict"}[30m]) 
  / rate(processed_messages_total[30m])
) > 0.001  # Alert if > 0.1%
```

#### Success Criteria (72 Hours)
- ✅ Rejection rate < 0.1%
- ✅ DLQ depth normal (< 100 messages)
- ✅ No user-facing issues
- ✅ Schema validation working as expected

---

## Rollback Procedures

### Level 1: Revert to Warn Mode (< 5 minutes)

**Trigger**: Rejection rate > 1% or user-facing errors

```bash
# Immediate action
export REGISTRY_ENFORCEMENT=warn
kubectl set env deployment/pipeline REGISTRY_ENFORCEMENT=warn

# Or via kubectl patch
kubectl patch deployment pipeline \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"pipeline","env":[{"name":"REGISTRY_ENFORCEMENT","value":"warn"}]}]}}}}'

# Verify
kubectl get pods -l app=pipeline -o json | jq '.items[].spec.containers[].env[] | select(.name=="REGISTRY_ENFORCEMENT")'
```

**Expected Result**: Rejections stop immediately, validation continues in log-only mode

---

### Level 2: Disable Registry (< 10 minutes)

**Trigger**: Registry service down or severe issues

```bash
# Disable registry entirely
export REGISTRY_ENABLED=false
kubectl set env deployment/pipeline REGISTRY_ENABLED=false

# Service falls back to no validation
```

**Expected Result**: System continues without validation, zero user impact

---

### Level 3: Full Rollback (< 30 minutes)

**Trigger**: Critical issues that can't be resolved with config changes

```bash
# Revert to previous deployment
kubectl rollout undo deployment/pipeline

# Or deploy previous tag
git checkout <previous-commit>
kubectl apply -f k8s/
```

---

## Metrics & Alerts

### Key Metrics to Monitor

| Metric | Warning Threshold | Critical Threshold |
|--------|-------------------|-------------------|
| Validation failure rate (warn) | > 2% | > 5% |
| Rejection rate (strict) | > 0.1% | > 1% |
| Registry errors | > 0 for 10min | > 10/sec |
| Cache hit rate | < 85% | < 70% |
| DLQ depth (strict mode) | > 100 | > 1000 |

### Alert Rules

See [PHASE_11.1_ALERT_RULES.md](PHASE_11.1_ALERT_RULES.md) for complete alert definitions.

---

## Synthetic Drills

### Drill 1: Benign Change (Pre-Production)
**Test**: Add optional field to FeedbackEvent

**Expected**:
- Registry emits `schema.published` event
- Pipeline validation continues to pass
- No rejections

**Run Before**: Week 2, Day 8

---

### Drill 2: Breaking Change (Staging Only)
**Test**: Remove required field in test schema

**Expected**:
- Validation fails in strict mode
- Messages sent to DLQ
- Clear error messages logged

**Run Before**: Week 2, Day 9

---

### Drill 3: Registry Outage (Staging)
**Test**: Block access to registry service

**Expected**:
- System falls back to cached schemas
- `schema_registry_errors_total` increases
- No user-facing impact
- Service continues processing

**Run Before**: Week 2, Day 10

---

## Communication Plan

### Pre-Launch (Day 0)
- [ ] Email to engineering team
- [ ] Slack announcement in #platform
- [ ] Update runbook

### Week 1 Launch (Day 4)
- [ ] Slack notification before deploy
- [ ] Status updates every 4 hours
- [ ] End-of-day summary

### Week 2 Strict Mode (Day 11)
- [ ] Advance notice (48h)
- [ ] Detailed status updates
- [ ] Success announcement

---

## Success Criteria Summary

### Week 1 (Warn Mode) ✅
- Validation failure rate < 2%
- No registry connection issues
- Cache hit rate > 95%
- 72 hours stable operation

### Week 2 (Strict Mode) ✅
- Rejection rate < 0.1%
- DLQ functioning correctly
- No user-facing issues
- 72 hours stable operation

---

## Sign-Off Checklist

### Before Week 1 Deploy
- [ ] Code reviewed and merged
- [ ] Tests passing (7/7)
- [ ] CI workflows green
- [ ] Staging environment ready
- [ ] On-call briefed
- [ ] Rollback plan tested

### Before Week 2 (Strict Mode)
- [ ] Week 1 success criteria met
- [ ] Validation issues resolved
- [ ] DLQ monitoring configured
- [ ] Team trained on rollback
- [ ] Go/No-Go meeting held

---

## References

- [Enforcement Modes Guide](PHASE_11.1_ENFORCEMENT_MODES.md)
- [Alert Rules](PHASE_11.1_ALERT_RULES.md)
- [Implementation Complete](PHASE_11.1_IMPLEMENTATION_COMPLETE.md)
- [Runbook](https://docs.openbb.co/runbooks/schema-enforcement)

---

**Status**: ✅ **READY FOR GO-LIVE**  
**Approved By**: Platform Team  
**Launch Date**: TBD (Week of 2025-10-21)

---

**End of Go-Live Plan**

