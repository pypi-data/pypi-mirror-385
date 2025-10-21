# Phase 11.0B Quick Start Guide

**Schema Registry Integration for Market Data Pipeline**

---

## Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
# Install with registry support
pip install -e ".[dev]"

# Verify installation
pip list | grep -E "core-registry-client|httpx"
```

### 2. Configure Environment

Create `.env` file (or set environment variables):

```bash
# Enable registry (Phase 3: Log-only validation)
REGISTRY_ENABLED=true
REGISTRY_URL=https://registry.openbb.co/api/v1
REGISTRY_TOKEN=  # Optional, for admin operations

# Cache settings
REGISTRY_CACHE_TTL=300  # 5 minutes
REGISTRY_TIMEOUT=30.0

# Schema preferences
SCHEMA_PREFER_TRACK=v2
SCHEMA_FALLBACK_TRACK=v1
```

### 3. Test Integration

```bash
# Run contract tests
pytest tests/contracts/test_registry_integration.py -v

# Fetch schemas from registry
python scripts/fetch_schemas.py --track v2
```

### 4. Use in Code

```python
from market_data_pipeline.schemas import RegistryConfig, SchemaManager

# Initialize schema manager
config = RegistryConfig()
async with SchemaManager(
    registry_url=config.url,
    enabled=config.enabled,
) as manager:
    # Validate payload
    is_valid, errors = await manager.validate_payload(
        "telemetry.FeedbackEvent",
        payload_dict,
    )
    print(f"Valid: {is_valid}, Errors: {errors}")
```

---

## Common Use Cases

### Use Case 1: Enable Registry in Production

```bash
# Set environment
export REGISTRY_ENABLED=true
export REGISTRY_URL=https://registry.openbb.co/api/v1

# Start pipeline
mdp run --config config.yaml
```

### Use Case 2: Fetch Schemas for CI/CD

```bash
# Fetch v2 schemas
python scripts/fetch_schemas.py \
  --output tests/contracts/schemas \
  --track v2

# Run contract tests
pytest tests/contracts/ -v
```

### Use Case 3: Monitor Validation

Query Prometheus metrics:
```promql
# Validation rate
rate(schema_validation_total[5m])

# Cache hit rate
schema_cache_hits_total / (schema_cache_hits_total + schema_cache_misses_total)
```

### Use Case 4: Disable Registry (Development)

```bash
# Disable for local development
export REGISTRY_ENABLED=false

# System will gracefully degrade
mdp run --config config.yaml
```

---

## Current State (Phase 3)

**Mode**: Log-Only Validation  
**Behavior**: Schemas are validated, failures logged, but processing continues

To see validation in action:
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export REGISTRY_ENABLED=true

# Run pipeline - watch for [registry] log messages
mdp run ...
```

---

## Troubleshooting

### Registry not available?
✅ **Graceful degradation**: System continues without validation

### Validation always passes?
🔍 Check: `REGISTRY_ENABLED=true` and schema manager is initialized

### Cache not working?
🔍 Check: `REGISTRY_CACHE_TTL` > 0 and monitor `schema_cache_hits_total`

---

## Next Steps

1. ✅ **Now**: Deploy with `REGISTRY_ENABLED=true` (log-only)
2. 🔄 **1-2 weeks**: Monitor validation failures
3. 🔜 **Phase 4**: Enable rejection mode (invalid payloads to DLQ)

---

## Resources

- [Implementation Complete](PHASE_11.0B_IMPLEMENTATION_COMPLETE.md)
- [Viability Assessment](PHASE_11.0B_VIABILITY_ASSESSMENT.md)
- [Executive Summary](PHASE_11.0B_EXECUTIVE_SUMMARY.md)

**Questions?** Check the full implementation guide above.

