# Phase 11.1 — Alert Rules for Enforcement & Drift Intelligence

**Repository**: `market_data_pipeline`  
**Phase**: 11.1 Go-Live  
**Purpose**: Prometheus alert rules for monitoring schema validation and enforcement

---

## Alert Rules

### 1. Schema Validation Failures (Warn Mode)

**Trigger**: High rate of validation failures in warn mode

```yaml
- alert: SchemaValidationFailuresHigh
  expr: |
    sum(rate(schema_validation_failures_total{mode="warn"}[15m])) > 50
  for: 15m
  labels:
    severity: warning
    component: schema-registry
    repo: pipeline
  annotations:
    summary: "High schema validation failure rate in warn mode"
    description: |
      Schema validation failures in warn mode: {{ $value }} failures/sec
      This indicates payloads are not matching registry schemas.
      Track: {{ $labels.track }}
      Schema: {{ $labels.schema }}
    runbook_url: "https://docs.openbb.co/runbooks/schema-validation-failures"
```

**Action**:
- Review validation error logs
- Identify problematic schemas
- Fix payload format issues
- DO NOT enable strict mode until failure rate < 1%

---

### 2. Schema Validation Rejections (Strict Mode)

**Trigger**: Validation failures in strict mode (payloads rejected)

```yaml
- alert: SchemaValidationRejectionsActive
  expr: |
    (
      rate(schema_validation_failures_total{mode="strict"}[30m]) 
      / 
      rate(processed_messages_total[30m])
    ) > 0.001
  for: 15m
  labels:
    severity: warning
    component: schema-registry
    repo: pipeline
  annotations:
    summary: "Schema validation rejection rate > 0.1%"
    description: |
      Strict mode is rejecting {{ $value | humanizePercentage }} of messages.
      Messages are being sent to DLQ.
      Schema: {{ $labels.schema }}
      Track: {{ $labels.track }}
    runbook_url: "https://docs.openbb.co/runbooks/schema-rejections"
```

**Action**:
- Check DLQ for rejected messages
- Review validation errors
- Consider temporary switch to warn mode if rate > 1%
- Fix root cause (payload format, schema mismatch)

---

### 3. Registry Connection Errors

**Trigger**: Registry service is unavailable or returning errors

```yaml
- alert: SchemaRegistryErrors
  expr: |
    sum(rate(schema_registry_errors_total[10m])) > 0
  for: 10m
  labels:
    severity: warning
    component: schema-registry
    repo: pipeline
  annotations:
    summary: "Schema Registry errors detected"
    description: |
      Registry errors: {{ $value }} errors/sec
      Error type: {{ $labels.error_type }}
      Schema: {{ $labels.schema }}
      System will fall back to cached schemas.
    runbook_url: "https://docs.openbb.co/runbooks/registry-errors"
```

**Action**:
- Check registry service health
- Verify network connectivity
- System auto-degrades to cached schemas (no immediate action needed)
- If sustained > 30min, investigate registry service

---

### 4. Registry Cache Degradation

**Trigger**: Cache hit rate is too low (excessive registry calls)

```yaml
- alert: SchemaRegistryCacheDegraded
  expr: |
    (
      sum(rate(schema_cache_hits_total[15m]))
      /
      (sum(rate(schema_cache_hits_total[15m])) + sum(rate(schema_cache_misses_total[15m])))
    ) < 0.85
  for: 15m
  labels:
    severity: info
    component: schema-registry
    repo: pipeline
  annotations:
    summary: "Schema cache hit rate below 85%"
    description: |
      Cache hit rate: {{ $value | humanizePercentage }}
      This indicates schemas are expiring too quickly or cache is cold.
      Consider increasing REGISTRY_CACHE_TTL.
    runbook_url: "https://docs.openbb.co/runbooks/cache-tuning"
```

**Action**:
- Increase `REGISTRY_CACHE_TTL` (current: 300s)
- Check if cache is being cleared frequently
- Monitor registry response times

---

### 5. Enforcement Mode Mismatch

**Trigger**: Strict mode active but high failure rate (configuration issue)

```yaml
- alert: EnforcementModeConfigurationIssue
  expr: |
    (
      sum(rate(schema_enforcement_actions_total{severity="error",action="rejected"}[5m]))
      > 10
    ) and (
      max(up{job="pipeline"}) == 1
    )
  for: 5m
  labels:
    severity: critical
    component: schema-registry
    repo: pipeline
  annotations:
    summary: "High rejection rate in strict mode - possible config issue"
    description: |
      Strict mode is rejecting {{ $value }} messages/sec
      This may indicate:
      - Strict mode enabled prematurely (failure rate too high)
      - Schema version mismatch
      - Payload format changed without schema update
      
      IMMEDIATE ACTION: Consider switching to warn mode.
    runbook_url: "https://docs.openbb.co/runbooks/enforcement-mode-issues"
```

**Action**:
- **IMMEDIATE**: Switch to warn mode
  ```bash
  export REGISTRY_ENFORCEMENT=warn
  ```
- Investigate validation failures
- Fix schema/payload mismatch
- Re-enable strict mode when ready

---

## Grafana Dashboard Queries

### Validation Failure Rate

```promql
# Overall validation failure rate
sum(rate(schema_validation_failures_total[5m])) by (mode, schema)
```

### Enforcement Actions

```promql
# Warnings vs Rejections
sum(rate(schema_enforcement_actions_total[5m])) by (severity, action)
```

### Cache Performance

```promql
# Cache hit rate percentage
100 * (
  sum(rate(schema_cache_hits_total[5m]))
  /
  (sum(rate(schema_cache_hits_total[5m])) + sum(rate(schema_cache_misses_total[5m])))
)
```

### Validation Success Rate

```promql
# Percentage of successful validations
100 * (
  sum(rate(schema_validation_total{outcome="success"}[5m]))
  /
  sum(rate(schema_validation_total[5m]))
)
```

### Registry Error Rate

```promql
# Registry errors by type
sum(rate(schema_registry_errors_total[5m])) by (error_type, schema)
```

---

## Alert Thresholds Summary

| Alert | Threshold | Duration | Severity | Action Required |
|-------|-----------|----------|----------|-----------------|
| Validation failures (warn) | > 50/15min | 15min | warning | Review logs, fix payloads |
| Validation rejections (strict) | > 0.1% | 15min | warning | Check DLQ, may revert to warn |
| Registry errors | > 0 | 10min | warning | Check registry health |
| Cache hit rate | < 85% | 15min | info | Tune cache TTL |
| Enforcement config issue | > 10 rejects/sec | 5min | **critical** | **Revert to warn mode** |

---

## Runbook: Emergency Rollback

### Symptoms
- High rejection rate (> 1%)
- DLQ filling rapidly
- User-facing errors

### Immediate Action (< 5 minutes)

```bash
# 1. Switch to warn mode (runtime)
export REGISTRY_ENFORCEMENT=warn

# 2. Or disable registry entirely (if registry is down)
export REGISTRY_ENABLED=false

# 3. Restart service
systemctl restart pipeline-service

# 4. Verify metrics
curl http://localhost:8080/metrics | grep schema_validation_failures
```

### Investigation (< 30 minutes)

1. **Check DLQ messages**
   ```bash
   # View rejected messages
   kubectl logs -l app=pipeline --tail=100 | grep "STRICT MODE"
   ```

2. **Review validation errors**
   ```promql
   # Top failing schemas
   topk(5, sum by (schema) (rate(schema_validation_failures_total[10m])))
   ```

3. **Compare schema versions**
   ```bash
   # Check registry schema version
   curl https://schema-registry-service.fly.dev/api/v1/schemas/v1/telemetry.FeedbackEvent
   
   # Compare with local fixtures
   cat tests/contracts/schemas/telemetry.FeedbackEvent.v1.json
   ```

### Root Cause & Fix (< 2 hours)

- **Schema mismatch**: Update payloads or schemas
- **Version mismatch**: Check track configuration (v1 vs v2)
- **Registry issues**: Wait for registry to recover (fail-open active)

### Re-enable Strict Mode (When Ready)

```bash
# Prerequisites:
# - Failure rate < 1% in warn mode for 72 hours
# - Root cause fixed and deployed
# - DLQ monitoring configured

export REGISTRY_ENFORCEMENT=strict
systemctl restart pipeline-service

# Monitor closely for 24 hours
watch -n 60 'curl -s http://localhost:8080/metrics | grep schema_validation'
```

---

## Monitoring Checklist

### Pre-Deployment
- [ ] Grafana dashboards imported
- [ ] Alert rules configured
- [ ] DLQ monitoring active
- [ ] Runbook accessible to on-call

### Week 1 (Warn Mode)
- [ ] Monitor validation failure rate daily
- [ ] Review validation error logs
- [ ] Identify and fix schema mismatches
- [ ] Achieve < 1% failure rate

### Week 2 (Strict Mode)
- [ ] Enable strict mode in staging first
- [ ] Monitor DLQ depth
- [ ] Track rejection rate (target: < 0.1%)
- [ ] Verify fail-open during registry outage

### Ongoing
- [ ] Weekly review of validation metrics
- [ ] Monthly cache performance tuning
- [ ] Quarterly schema health audit

---

## Integration with Other Repos

### Store (Drift Reporter)
Alert when Store detects drift:
```promql
schema_drift_active_total{repo="store"} > 0
```

### Orchestrator (Aggregator)
View aggregated drift across all repos:
```promql
sum(schema_drift_active_total) by (schema, track)
```

### Registry Service
Alert on registry sync issues:
```promql
registry_sync_age_seconds > 300
```

---

## References

- [Phase 11.1 Enforcement Guide](PHASE_11.1_ENFORCEMENT_MODES.md)
- [Phase 11.1 Go-Live Plan](PHASE_11.1_GOLIVE_PLAN.md)
- [Prometheus Alerting Best Practices](https://prometheus.io/docs/practices/alerting/)

---

**Status**: ✅ **Ready for Production**  
**Last Updated**: 2025-10-18  
**Owner**: Platform Team

