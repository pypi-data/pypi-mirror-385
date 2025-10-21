# Market Data Pipeline - Operations Scripts

This directory contains operational scripts for testing and validating the market data pipeline.

## Smoke Test Scripts

### `smoke_test.sh` (Linux/macOS)
Bash script for end-to-end validation of the pipeline API.

### `smoke_test.ps1` (Windows PowerShell)
PowerShell script for Windows compatibility.

## Usage

### 1. Start the services
```bash
docker compose up --build -d
```

### 2. Run smoke test

**Linux/macOS:**
```bash
./scripts/smoke_test.sh
```

**Windows PowerShell:**
```powershell
./scripts/smoke_test.ps1
```

### 3. Stop services
```bash
docker compose down
```

## What the smoke test validates

1. **Health Check** - API is responding
2. **Pipeline Creation** - Can create a synthetic pipeline
3. **Pipeline Management** - Can list and get pipeline status
4. **Pipeline Execution** - Pipeline runs for specified duration
5. **Pipeline Cleanup** - Pipeline completes and auto-removes
6. **Error Handling** - Graceful handling of completed pipelines

## Environment Variables

The docker-compose.yaml configures:
- `LOG_LEVEL`: INFO
- `PIPELINE_BATCH_SIZE`: 500
- `PIPELINE_FLUSH_MS`: 100
- `SINK_WORKERS`: 2
- `SINK_QUEUE_MAX`: 100
- `DROP_POLICY`: oldest
- `DATABASE_URL`: postgres://postgres:postgres@md_postgres:5432/market_data

## CI Integration

These scripts can be integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run smoke test
  run: |
    docker compose up --build -d
    ./scripts/smoke_test.sh
    docker compose down
```
