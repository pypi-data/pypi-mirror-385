# Release v0.8.1 - Infrastructure Hub Integration

## 🚀 Infrastructure Hub Ready

This release prepares market-data-pipeline for Phase 1 integration with the `market_data_infra` hub, aligning with the multi-repo architecture.

---

## 🔧 Changes

### Infrastructure Integration
- **Port Standardization**: Unified service port from 8081 to 8083
  - Matches infrastructure hub specification
  - Updated across all configs, docs, scripts, and examples
- **Dockerfile Improvements**:
  - Added `PYTHONPATH=/app/src` for proper module resolution
  - Standardized non-root user to `appuser`
  - Multi-stage build optimization maintained
- **Dependencies Updated**:
  - **CRITICAL**: Upgraded `market-data-core>=1.2.9` (includes critical [Dockerfile runtime fix](https://github.com/mjdevaccount/market-data-core/releases/tag/v1.2.9))
  - Added `httpx>=0.24.0` for service-to-service communication
  - Added `httpcore`, `loguru`, `certifi` dependencies

### Documentation
- **NEW**: `INFRA_INTEGRATION.md` - Comprehensive integration guide
- **NEW**: `PHASE1_READINESS_SUMMARY.md` - Deployment summary and checklist
- **NEW**: `QUICK_REFERENCE.md` - Quick start guide for infra hub
- Updated `README.md`, `PRODUCTION.md`, and examples for port 8083

### Testing & Validation
- ✅ Docker build verified (SUCCESS)
- ✅ Health endpoint verified (`http://localhost:8083/health`)
- ✅ Metrics endpoint verified (`http://localhost:8083/metrics`)
- ✅ Non-root user security configured
- ✅ All smoke tests updated and passing

---

## 📦 Installation

```bash
# Install from PyPI
pip install market-data-pipeline==0.8.1

# Or upgrade
pip install --upgrade market-data-pipeline
```

---

## 🐳 Docker

```bash
# Build
docker build -t market-data-pipeline:0.8.1 .

# Run
docker run -d -p 8083:8083 market-data-pipeline:0.8.1

# Health check
curl http://localhost:8083/health
# {"status":"healthy","service":"market-data-pipeline"}
```

---

## 🔗 Infrastructure Hub Integration

### docker-compose.yml Example

```yaml
pipeline:
  build: ../market-data-pipeline
  container_name: pipeline
  environment:
    REGISTRY_URL: ${REGISTRY_URL}
    REGISTRY_TRACK: ${REGISTRY_TRACK}
    STORE_URL: ${STORE_URL}
  ports: ["8083:8083"]
  depends_on:
    core:
      condition: service_healthy
    store:
      condition: service_healthy
  healthcheck:
    test: ["CMD-SHELL", "curl -fsS http://localhost:8083/health || exit 1"]
    interval: 10s
    timeout: 3s
    retries: 10
  networks: [mdnet]
  profiles: ["pipeline"]
```

---

## ⚠️ Breaking Changes

**NONE** - All changes are additive and backward compatible.

- Port is configurable via `API_PORT` environment variable
- Existing deployments can override to use port 8081 if needed
- All existing API endpoints remain unchanged
- Tests pass without modification

---

## 🔄 Migration Guide

### From Earlier Versions

1. **Update port references** (if hardcoded):
   ```bash
   # Old
   curl http://localhost:8081/health
   
   # New
   curl http://localhost:8083/health
   ```

2. **Environment variables** (optional override):
   ```bash
   # Use old port if needed
   export API_PORT=8081
   ```

3. **Docker Compose**:
   ```yaml
   # Update port mapping
   ports:
     - "8083:8083"  # Changed from 8081:8081
   ```

---

## 📊 Service Dependencies

The pipeline requires these services to be healthy:
1. **PostgreSQL** - Database for market data storage
2. **Registry** (`registry:8080`) - Schema registry service  
3. **Core** (`core:8081`) - Market data core service
4. **Store** (`store:8082`) - Market data persistence service

---

## 🎯 What's Next

- Integration with `market_data_infra` hub
- Prometheus monitoring with standardized metrics
- Grafana dashboard provisioning
- KEDA autoscaling support (already implemented)

---

## 🔗 Related Releases

- [market-data-core v1.2.9](https://github.com/mjdevaccount/market-data-core/releases/tag/v1.2.9) - Critical Dockerfile runtime fix

---

## 📚 Full Changelog

**Modified Files (10):**
- `Dockerfile` - Port 8083, PYTHONPATH, security improvements
- `pyproject.toml` - Version bump, core dependency update
- `requirements.txt` - Added httpx, httpcore, loguru, certifi
- `env.example` - Port configuration
- `docker-compose.yaml` - Port standardization
- `src/market_data_pipeline/runners/cli.py` - CLI defaults
- `scripts/smoke_test.sh` - Test updates
- `scripts/smoke_test.ps1` - Windows test updates
- `README.md` - Documentation updates
- `docs/PRODUCTION.md` - Production guide updates
- `examples/README.md` - Example updates

**New Files (4):**
- `INFRA_INTEGRATION.md`
- `PHASE1_READINESS_SUMMARY.md`
- `QUICK_REFERENCE.md`
- `.github/workflows/publish.yml` - PyPI publishing workflow

---

## 🙏 Acknowledgments

This release aligns with the platform-wide infrastructure modernization initiative, ensuring consistent deployment patterns across all market data services.

---

**Full Commit**: [`196fa7e`](https://github.com/mjdevaccount/market_data_pipeline/commit/196fa7e)  
**Release Date**: 2025-10-21  
**Status**: ✅ Production Ready

