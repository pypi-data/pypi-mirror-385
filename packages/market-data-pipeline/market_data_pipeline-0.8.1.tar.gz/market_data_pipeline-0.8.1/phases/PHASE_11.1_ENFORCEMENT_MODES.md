# Phase 11.1 — Enforcement Modes: Developer Guide

**Date**: 2025-10-18  
**Repository**: `market_data_pipeline`  
**Phase**: 11.1 (Enforcement & Drift Intelligence)  
**Status**: ✅ **COMPLETE**

---

## Overview

Phase 11.1 adds **enforcement modes** to the schema registry integration, allowing controlled migration from soft validation (logging) to hard validation (rejection).

### Enforcement Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **warn** | Log validation failures, continue processing | Development, staging, gradual rollout |
| **strict** | Raise `SchemaValidationError`, fail to DLQ | Production enforcement, data quality |

---

## Configuration

### Environment Variables

```bash
# Enforcement mode (Phase 11.1)
REGISTRY_ENFORCEMENT=warn    # or 'strict'
```

### Full Registry Configuration

```bash
# Registry Integration (Phase 11.0B + 11.1)
REGISTRY_ENABLED=true
REGISTRY_URL=https://registry.openbb.co/api/v1
REGISTRY_TOKEN=optional_token
REGISTRY_CACHE_TTL=300
REGISTRY_TIMEOUT=30.0
SCHEMA_PREFER_TRACK=v2
SCHEMA_FALLBACK_TRACK=v1
REGISTRY_ENFORCEMENT=warn     # warn | strict
```

---

## Usage

### Warn Mode (Default)

**Behavior**: Validation failures logged but processing continues.

```python
from market_data_pipeline.schemas import RegistryConfig, SchemaManager

# Create manager in warn mode (default)
config = RegistryConfig(enforcement_mode="warn")
async with SchemaManager(
    registry_url=config.url,
    enforcement_mode=config.enforcement_mode,
) as manager:
    # Invalid payload
    is_valid, errors = await manager.validate_payload(
        "telemetry.FeedbackEvent",
        invalid_payload,
    )
    
    if not is_valid:
        logger.warning(f"Validation failed: {errors}")
        # Processing continues anyway
```

**Use Cases**:
- Development and testing
- Initial deployment to production (observe validation failures)
- Gradual schema migration (v1 → v2)
- Monitoring validation quality before enforcement

### Strict Mode

**Behavior**: Validation failures raise `SchemaValidationError`.

```python
from market_data_pipeline.errors import SchemaValidationError
from market_data_pipeline.schemas import SchemaManager

# Create manager in strict mode
async with SchemaManager(
    registry_url="https://registry.openbb.co/api/v1",
    enforcement_mode="strict",
) as manager:
    try:
        is_valid, errors = await manager.validate_payload(
            "telemetry.FeedbackEvent",
            payload,
        )
    except SchemaValidationError as e:
        # Validation failed - payload rejected
        logger.error(f"Schema: {e.schema_name}")
        logger.error(f"Errors: {e.errors}")
        logger.error(f"Track: {e.track}")
        # Send to DLQ or handle error
```

**Use Cases**:
- Production data quality enforcement
- Schema contract verification
- Preventing invalid data from propagating
- Compliance requirements

---

## Pulse Consumer Integration

### Automatic Enforcement Handling

The Pulse consumer automatically handles both enforcement modes:

```python
from market_data_pipeline.pulse.consumer import FeedbackConsumer
from market_data_pipeline.schemas import SchemaManager, RegistryConfig

# Setup schema manager
config = RegistryConfig()
schema_manager = SchemaManager(
    registry_url=config.url,
    enforcement_mode=config.enforcement_mode,  # warn or strict
)
await schema_manager.start()

# Create consumer with schema manager
consumer = FeedbackConsumer(
    rate_controller=controller,
    settings=settings,
    schema_manager=schema_manager,
)

# Run consumer
await consumer.run(consumer_name="pipeline_w1")
```

**Behavior**:
- **Warn Mode**: Invalid payloads logged, processing continues
- **Strict Mode**: Invalid payloads rejected, sent to DLQ

---

## Migration Path

### Recommended Rollout

#### Phase 1: Enable Registry (Warn Mode)
```bash
REGISTRY_ENABLED=true
REGISTRY_ENFORCEMENT=warn
```

**Duration**: 1-2 weeks

**Goals**:
- Monitor validation failure rates
- Identify schema mismatches
- Fix invalid payloads
- Tune cache settings

**Metrics to Watch**:
```promql
# Validation failure rate
rate(schema_validation_failures_total{mode="warn"}[5m])

# Enforcement actions
rate(schema_enforcement_actions_total{severity="warn"}[5m])
```

#### Phase 2: Fix Issues
- Update payloads to match v2 schemas
- Fix schema mismatches
- Deploy fixes
- Verify validation success rate improves

#### Phase 3: Enable Strict Mode
```bash
REGISTRY_ENFORCEMENT=strict
```

**Prerequisites**:
- Validation failure rate < 1%
- All critical schemas passing validation
- DLQ monitoring configured
- Runbook prepared for failures

**Rollout**:
1. Deploy to staging with strict mode
2. Run for 24-48 hours
3. Verify DLQ handling works
4. Deploy to production
5. Monitor closely for 1 week

---

## Metrics & Monitoring

### Key Metrics (Phase 11.1)

| Metric | Description | Labels |
|--------|-------------|--------|
| `schema_validation_failures_total` | Total validation failures by mode | `schema`, `mode` |
| `schema_enforcement_actions_total` | Total enforcement actions taken | `schema`, `severity`, `action` |

### Prometheus Queries

```promql
# Validation failure rate by mode
rate(schema_validation_failures_total[5m])

# Enforcement warnings (warn mode)
rate(schema_enforcement_actions_total{severity="warn"}[5m])

# Enforcement rejections (strict mode)
rate(schema_enforcement_actions_total{severity="error",action="rejected"}[5m])

# Warn mode success rate
sum(rate(schema_validation_total{outcome="success"}[5m])) 
/ sum(rate(schema_validation_total[5m]))
```

### Grafana Dashboard

Add panels for:

1. **Validation Outcomes by Mode**
   - Success vs. Failure rates
   - Grouped by enforcement mode

2. **Enforcement Actions**
   - Warnings logged (warn mode)
   - Rejections (strict mode)
   - By schema name

3. **Mode Distribution**
   - Services in warn vs. strict mode
   - Migration progress

4. **DLQ Depth** (strict mode)
   - Failed messages in dead letter queue
   - Schema validation failures

---

## Error Handling

### SchemaValidationError

```python
from market_data_pipeline.errors import SchemaValidationError

try:
    await manager.validate_payload(schema_name, payload)
except SchemaValidationError as e:
    print(f"Schema: {e.schema_name}")
    print(f"Errors: {e.errors}")
    print(f"Track: {e.track}")
    print(f"Mode: {e.enforcement_mode}")
    
    # Handle error
    if e.enforcement_mode == "strict":
        # Send to DLQ
        await dlq.publish(envelope, error=str(e))
```

### Pulse Consumer Error Handling

```python
# In Pulse consumer._handle():
try:
    await schema_manager.validate_payload(...)
except SchemaValidationError as e:
    # Strict mode: validation failed
    logger.error(f"STRICT MODE: Validation failed, failing to DLQ: {e.errors}")
    raise  # Re-raise to trigger DLQ processing
```

---

## Testing

### Run Enforcement Tests

```bash
# All enforcement tests
pytest tests/schemas/test_enforcement_modes.py -v

# Warn mode tests only
pytest tests/schemas/test_enforcement_modes.py -v -k "warn"

# Strict mode tests only
pytest tests/schemas/test_enforcement_modes.py -v -k "strict"
```

### CI Matrix Testing

The CI runs a full matrix of:
- **Tracks**: v1, v2
- **Modes**: warn, strict

```bash
# Trigger CI matrix
gh workflow run dispatch_enforcement_matrix.yml
```

---

## Troubleshooting

### Issue: High validation failure rate in warn mode

**Diagnosis**:
```promql
rate(schema_validation_failures_total{mode="warn"}[5m])
```

**Solution**:
1. Review validation error messages in logs
2. Identify problematic schemas
3. Update payloads to match schema requirements
4. Deploy fixes
5. Monitor until failure rate < 1%

### Issue: Strict mode causing too many DLQ messages

**Diagnosis**:
```promql
rate(schema_enforcement_actions_total{severity="error",action="rejected"}[5m])
```

**Solution**:
1. **Temporary**: Switch back to warn mode
   ```bash
   REGISTRY_ENFORCEMENT=warn
   ```
2. Investigate validation failures
3. Fix root cause (schema mismatch, payload format, etc.)
4. Re-enable strict mode when ready

### Issue: Validation always succeeds

**Check**:
- Is `REGISTRY_ENABLED=true`?
- Is schema manager initialized with correct mode?
- Check logs for registry errors

### Issue: Performance impact

**Check**:
```promql
# Cache hit rate (should be > 95%)
schema_cache_hits_total / (schema_cache_hits_total + schema_cache_misses_total)

# Validation latency
histogram_quantile(0.99, rate(schema_validation_duration_seconds_bucket[5m]))
```

**Tune**:
- Increase `REGISTRY_CACHE_TTL` (default: 300s)
- Preload critical schemas at startup
- Monitor registry response times

---

## API Reference

### SchemaManager

```python
class SchemaManager:
    def __init__(
        self,
        registry_url: str,
        token: str | None = None,
        enabled: bool = True,
        cache_ttl: int = 300,
        timeout: float = 30.0,
        enforcement_mode: str = "warn",  # Phase 11.1
    )
```

**Parameters**:
- `enforcement_mode`: `"warn"` or `"strict"`

**Raises**:
- `ValueError`: If enforcement_mode not in `("warn", "strict")`

### validate_payload

```python
async def validate_payload(
    schema_name: str,
    payload: dict[str, Any],
    prefer: str = "v2",
    fallback: str | None = "v1",
) -> tuple[bool, list[str]]:
```

**Behavior**:
- **Warn mode**: Returns `(False, errors)` on validation failure
- **Strict mode**: Raises `SchemaValidationError` on validation failure

**Returns**: `(is_valid, error_messages)`

**Raises**: `SchemaValidationError` (strict mode only)

---

## Best Practices

### 1. Start with Warn Mode
Always start with warn mode to observe validation patterns without impact.

### 2. Monitor Before Enforcing
Run warn mode for at least 1-2 weeks before switching to strict mode.

### 3. Fix Issues Incrementally
Don't enable strict mode with known validation failures.

### 4. Have a Rollback Plan
Be prepared to switch back to warn mode if issues arise.

### 5. Test in Staging First
Always test enforcement mode changes in staging before production.

### 6. Monitor DLQ
Set up alerts for DLQ depth in strict mode.

### 7. Document Schema Changes
Communicate schema changes to all consumers before enforcement.

---

## Examples

### Example 1: Gradual Migration

```bash
# Week 1-2: Observe
REGISTRY_ENABLED=true
REGISTRY_ENFORCEMENT=warn

# Week 3-4: Fix issues, continue monitoring
REGISTRY_ENFORCEMENT=warn

# Week 5: Enable strict mode (after < 1% failure rate)
REGISTRY_ENFORCEMENT=strict
```

### Example 2: Service-Specific Enforcement

```python
# Critical service: strict mode
if os.getenv("SERVICE_NAME") == "payment_processor":
    enforcement_mode = "strict"
else:
    enforcement_mode = "warn"

manager = SchemaManager(
    registry_url=config.url,
    enforcement_mode=enforcement_mode,
)
```

### Example 3: Schema-Specific Handling

```python
try:
    await manager.validate_payload("critical.PaymentEvent", payload)
except SchemaValidationError as e:
    # Critical schema: fail fast
    logger.error(f"CRITICAL SCHEMA FAILURE: {e.errors}")
    raise

try:
    await manager.validate_payload("telemetry.Log", payload)
except SchemaValidationError as e:
    # Non-critical schema: log and continue
    logger.warning(f"Non-critical validation failed: {e.errors}")
    # Continue processing
```

---

## Summary

Phase 11.1 enforcement modes provide:

✅ **Controlled Migration**: warn → strict  
✅ **Data Quality**: Strict validation enforcement  
✅ **Observability**: Comprehensive metrics  
✅ **Flexibility**: Schema-specific handling  
✅ **Safety**: Graceful degradation options

**Default**: Warn mode (safe for initial deployment)  
**Production**: Strict mode (after validation tuning)

---

## References

- [Phase 11.0B Implementation](PHASE_11.0B_IMPLEMENTATION_COMPLETE.md)
- [Phase 11.1 Implementation Plan](PHASE_11.1_IMPLEMENTATION_PLAN.md)
- [Schema Registry Documentation](../docs/SCHEMA_REGISTRY.md)

---

**Status**: ✅ **READY FOR USE**  
**Recommended**: Start with warn mode, migrate to strict after validation tuning

