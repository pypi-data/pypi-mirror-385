# Phase 11.0B — Schema Registry Integration

## 📋 Summary

Integrates Schema Registry Service into the Market Data Pipeline for dynamic schema validation, version negotiation, and centralized schema management. This phase implements **log-only validation (Phase 3)** where schemas are validated but invalid payloads are logged and still processed.

**Status**: ✅ Ready for Production  
**Mode**: Phase 3 (Soft Validation - Log Only)  
**Impact**: Zero breaking changes, graceful degradation by default

---

## 🎯 Objectives

- ✅ Enable dynamic schema fetching from centralized registry
- ✅ Add version negotiation (prefer v2, fallback to v1)
- ✅ Integrate schema validation into Pulse consumer (log-only mode)
- ✅ Add monitoring metrics for validation and cache performance
- ✅ Create CI/CD scripts for schema fetching
- ✅ Ensure graceful degradation when registry unavailable

---

## 📦 What's New

### Core Implementation

#### 1. Schema Manager (`src/market_data_pipeline/schemas/`)
- **Schema Manager**: Core implementation with caching, validation, and version negotiation
  - TTL-based schema caching (default: 5 minutes)
  - Version negotiation (v2 preferred, v1 fallback)
  - JSON Schema validation (Draft 7)
  - Graceful degradation on registry errors
  - Comprehensive stats tracking

- **Configuration**: Environment-based registry configuration
  - `REGISTRY_ENABLED`: Enable/disable registry (default: `false`)
  - `REGISTRY_URL`: Registry service URL
  - `REGISTRY_CACHE_TTL`: Cache TTL in seconds
  - `SCHEMA_PREFER_TRACK`: Preferred track (v1/v2)

#### 2. Pulse Consumer Integration
- Added optional `schema_manager` parameter
- Log-only validation in message handler
- No functional impact on processing
- Validation failures logged with metrics

#### 3. Metrics
New Prometheus metrics for monitoring:
- `schema_validation_total`: Validation outcomes (success/failure/error)
- `schema_cache_hits_total`: Cache performance tracking
- `schema_cache_misses_total`: Registry fetch tracking
- `schema_registry_errors_total`: Error tracking by type
- `schema_cache_size`: Current cache size

### CI/CD Integration

#### 4. Schema Fetch Script (`scripts/fetch_schemas.py`)
- Fetches schemas from registry for contract testing
- Supports v1 and v2 tracks
- Environment-based configuration
- Used in GitHub workflows

#### 5. GitHub Workflows
- `_contracts_registry_reusable.yml`: Reusable registry-based contract testing
- `dispatch_contracts_registry.yml`: Manual workflow dispatch
- Fetches schemas from registry during CI
- Uploads schema artifacts for debugging

### Testing

#### 6. Contract Tests (`tests/contracts/test_registry_integration.py`)
Comprehensive test coverage:
- Configuration validation
- Manager initialization and lifecycle
- Schema caching with TTL
- Validation logic
- Graceful degradation
- Pulse consumer integration

---

## 📊 Changes Summary

### Files Changed
- **Modified**: 4 files
  - `pyproject.toml`: Added dependencies
  - `src/market_data_pipeline/metrics.py`: Added registry metrics
  - `src/market_data_pipeline/pulse/consumer.py`: Added validation
  - `env.example`: Added registry config

- **New**: 11 files
  - Schema manager implementation (3 files)
  - CI/CD scripts (1 file)
  - GitHub workflows (2 files)
  - Contract tests (1 file)
  - Documentation (4 files)

### Code Statistics
- **Lines Added**: ~1,800 total
  - Core implementation: ~500 lines
  - Tests: ~270 lines
  - Documentation: ~700 lines
  - CI/CD: ~260 lines

### Dependencies
- `core-registry-client>=0.1.0`: Registry client SDK
- `httpx>=0.24.0`: HTTP client for registry

---

## 🔧 Configuration

### Environment Variables (New)

```bash
# Schema Registry (Phase 11.0B)
REGISTRY_ENABLED=false              # Enable registry integration
REGISTRY_URL=https://registry.openbb.co/api/v1
REGISTRY_TOKEN=                     # Optional admin token
REGISTRY_CACHE_TTL=300              # Cache TTL in seconds
REGISTRY_TIMEOUT=30.0               # Request timeout
SCHEMA_PREFER_TRACK=v2              # Preferred track
SCHEMA_FALLBACK_TRACK=v1            # Fallback track
```

### Default Behavior
- Registry is **disabled by default** (`REGISTRY_ENABLED=false`)
- No impact on existing deployments
- Opt-in activation via environment variable

---

## 🚀 Usage

### Enable Registry Validation

```bash
# Set environment
export REGISTRY_ENABLED=true
export REGISTRY_URL=https://registry.openbb.co/api/v1

# Start pipeline (validation happens automatically)
mdp run --config config.yaml
```

### Programmatic Usage

```python
from market_data_pipeline.schemas import RegistryConfig, SchemaManager

# Initialize
config = RegistryConfig()
async with SchemaManager(
    registry_url=config.url,
    enabled=config.enabled,
) as manager:
    # Validate
    is_valid, errors = await manager.validate_payload(
        "telemetry.FeedbackEvent",
        payload_dict,
    )
    if not is_valid:
        logger.warning(f"Validation failed: {errors}")
```

### CI/CD Schema Fetching

```bash
# Fetch schemas for contract testing
python scripts/fetch_schemas.py --track v2

# Run contract tests
pytest tests/contracts/ -v
```

---

## 📈 Monitoring

### Key Metrics

Query validation performance:
```promql
# Validation success rate
sum(rate(schema_validation_total{outcome="success"}[5m])) 
/ sum(rate(schema_validation_total[5m]))

# Cache hit rate
sum(rate(schema_cache_hits_total[5m])) 
/ (sum(rate(schema_cache_hits_total[5m])) + sum(rate(schema_cache_misses_total[5m])))

# Registry error rate
rate(schema_registry_errors_total[5m])
```

### Grafana Dashboard

Add panels for:
- Validation outcomes over time
- Cache hit/miss ratio
- Registry error rates
- Cache size trends

---

## ✅ Testing

### Unit Tests
```bash
# Run all contract tests
pytest tests/contracts/ -v

# Run only registry tests
pytest tests/contracts/test_registry_integration.py -v
```

### Integration Tests
```bash
# Test with registry disabled (default)
export REGISTRY_ENABLED=false
pytest tests/contracts/ -v

# Test with registry enabled
export REGISTRY_ENABLED=true
export REGISTRY_URL=https://registry.test.openbb.co
pytest tests/contracts/test_registry_integration.py -v
```

### Linting
```bash
# No linter errors
ruff check src/market_data_pipeline/schemas/
mypy src/market_data_pipeline/schemas/
```

---

## 🛡️ Safety & Rollback

### Graceful Degradation
The implementation includes multiple safety layers:

1. **Disabled by Default**: `REGISTRY_ENABLED=false`
2. **Log-Only Mode**: Invalid payloads logged, not rejected
3. **Registry Unavailable**: Validation returns success with warning
4. **Schema Not Found**: Fallback track attempted
5. **Validation Error**: Treated as valid with warning

### Zero Breaking Changes
- No changes to existing APIs
- No changes to data flow
- Optional feature activation
- Backward compatible

### Rollback Options
```bash
# Option 1: Disable via environment
export REGISTRY_ENABLED=false

# Option 2: Revert commit
git revert <commit-hash>

# Option 3: Delete feature branch
git checkout base
```

---

## 🎯 Current Phase: Phase 3 (Soft Validation)

**Behavior**:
- ✅ Schemas fetched from registry
- ✅ Validation performed on all payloads
- ✅ Failures logged with metrics
- ✅ Processing continues regardless of validation

**NOT Implemented** (Phase 4 - Future):
- ❌ Rejection of invalid payloads
- ❌ DLQ integration
- ❌ Enforcement mode

---

## 📋 Checklist

### Pre-Merge
- [x] All tests passing
- [x] No linter errors
- [x] Documentation complete
- [x] Backward compatible
- [x] Graceful degradation tested
- [x] Metrics verified
- [x] CI/CD workflows tested

### Post-Merge
- [ ] Deploy to staging
- [ ] Enable `REGISTRY_ENABLED=true` in staging
- [ ] Monitor metrics for 24-48 hours
- [ ] Deploy to production
- [ ] Monitor validation failure rates
- [ ] Plan Phase 4 (enforcement mode)

---

## 📚 Documentation

Comprehensive documentation added:
- [Implementation Complete](PHASE_11.0B_IMPLEMENTATION_COMPLETE.md): Full implementation guide
- [Quick Start](PHASE_11.0B_QUICK_START.md): Quick setup guide
- [Changes Summary](PHASE_11.0B_CHANGES_SUMMARY.md): Detailed changes list
- [Viability Assessment](PHASE_11.0B_VIABILITY_ASSESSMENT.md): Initial assessment

---

## 🔜 Future Work (Phase 4)

Phase 4 will enable **full enforcement**:
1. Reject invalid payloads
2. Send failures to DLQ
3. Force v2 schema adoption
4. Deprecate v1 schemas

**Timeline**: 2-4 weeks after Phase 3 deployment and monitoring

---

## 🎉 Benefits

### Immediate (Phase 3)
- ✅ Schema validation visibility
- ✅ Centralized schema management
- ✅ Version negotiation (v2/v1)
- ✅ Monitoring and metrics

### Future (Phase 4)
- ✅ Schema enforcement
- ✅ Data quality guarantees
- ✅ Smooth v1 → v2 migration
- ✅ Breaking change prevention

---

## 🙏 Acknowledgments

Built on top of:
- Phase 10.1 (Pulse Integration)
- Core v1.2.0 (Pulse + Telemetry)
- Schema Registry Service

---

## 📞 Questions?

See documentation or reach out to the team.

**Ready to merge!** ✅

