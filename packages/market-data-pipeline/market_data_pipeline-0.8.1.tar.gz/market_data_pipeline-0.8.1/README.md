# 🚀 Market Data Pipeline

<div align="center">

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-176%20passing-success)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Version](https://img.shields.io/badge/version-0.9.0-blue)](https://github.com/mjdevaccount/market_data_pipeline/releases)

**Enterprise-grade streaming DAG engine for real-time and batch market data with adaptive autoscaling**

[Features](#-features) •
[Quick Start](#-quick-start) •
[Architecture](#-architecture) •
[Documentation](#-documentation) •
[Examples](#-examples)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Configuration](#%EF%B8%8F-configuration)
- [DAG Runtime](#-dag-runtime-phase-5)
- [KEDA Autoscaling](#-keda-autoscaling-phase-6)
- [Development](#-development)
- [Testing](#-testing)
- [Production Deployment](#-production-deployment)
- [Monitoring](#-monitoring--observability)
- [Extending](#-extending-the-pipeline)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Market Data Pipeline** is a production-grade orchestration system for real-time and batch market data processing. It provides a flexible, scalable platform for ingesting, transforming, and delivering market data from multiple sources (IBKR, replay, synthetic) to various sinks (TimescaleDB, Kafka, databases).

### What It Does

Moves data from **sources** → through **operators** → into **sinks** with:
- ✅ **Flow control** & backpressure management
- ✅ **Pacing compliance** for API rate limits
- ✅ **Event-time processing** with watermarks
- ✅ **Adaptive autoscaling** via KEDA
- ✅ **Comprehensive observability** (Prometheus, Grafana)
- ✅ **Production-ready** deployment patterns

### Use Cases

- Real-time market data ingestion from IBKR
- Historical data replay for backtesting
- High-frequency data aggregation (ticks → bars)
- Options chain processing with Greeks calculation
- Multi-provider data fusion and normalization
- Cost-optimized autoscaling deployments

---

## ✨ Features

### Core Capabilities

- **🔄 Dual Runtime Modes**
  - **Classic Mode**: Traditional pipeline orchestration
  - **DAG Mode**: Streaming directed acyclic graph engine

- **📊 Data Sources**
  - **IBKR**: Live market data with reconnection handling
  - **Replay**: Historical data from Parquet files
  - **Synthetic**: Predictable data generation for testing

- **⚙️ Operators**
  - **Bar Aggregation**: OHLCV bars with event-time correctness
  - **Options Processing**: Chain snapshots with Greeks
  - **Windowing**: Tumbling, sliding, and session windows
  - **Partitioning**: Hash-based data distribution
  - **Custom**: Extensible operator framework

- **📤 Sinks**
  - **Store**: TimescaleDB via `market_data_store`
  - **Kafka**: High-throughput streaming
  - **Database**: Direct SQL writes with retries
  - **Custom**: Pluggable sink architecture

### Advanced Features (Phase 5-6)

- **🎯 Streaming DAG Engine**
  - Compose operators into directed acyclic graphs
  - Event-time windowing with watermarks
  - Hash partitioning for parallelism
  - Channel-based backpressure

- **📈 Adaptive Autoscaling**
  - Dynamic rate adjustment based on downstream pressure
  - KEDA-based horizontal pod autoscaling
  - Prometheus metrics integration
  - Zero-touch operations in Kubernetes

- **🔧 Backpressure Feedback Loop**
  - Closed-loop control from store to pipeline
  - Policy-based scaling (OK/SOFT/HARD)
  - Graceful degradation under load

### Operational Excellence

- **🎛️ Flow Control**: Bounded queues, drop policies, hybrid batching
- **⏱️ Pacing**: Token-bucket rate limiting with provider-specific error codes
- **🔄 Retry Logic**: Exponential backoff for transient failures
- **📊 Observability**: 50+ Prometheus metrics, health checks, structured logs
- **🐳 Container-Native**: Multi-stage Docker builds, Kubernetes manifests
- **🧪 Comprehensive Testing**: 176 tests (unit + integration + load)

---

## 🛠️ Technology Stack

### Core Technologies

| Category | Technologies |
|----------|-------------|
| **Language** | Python 3.11+ |
| **Async Runtime** | asyncio, aiofiles, aiokafka |
| **Web Framework** | FastAPI, uvicorn |
| **Data Processing** | pandas, numpy, pyarrow |
| **Configuration** | Pydantic, pydantic-settings, YAML |
| **Observability** | Prometheus, OpenTelemetry, structlog |
| **Message Queue** | Kafka (aiokafka), MQTT |
| **Database** | TimescaleDB, PostgreSQL (via market_data_store) |

### Development Tools

| Category | Technologies |
|----------|-------------|
| **Testing** | pytest, pytest-asyncio, pytest-cov, freezegun |
| **Code Quality** | black, ruff, mypy |
| **CI/CD** | GitHub Actions, Docker, docker-compose |
| **Container** | Docker, Kubernetes, KEDA |
| **Deployment** | Helm (planned), docker-compose |

### Optional Dependencies

- **DAG Runtime**: `mmh3` for fast hash partitioning
- **IBKR**: `market_data_ibkr` for live data
- **Store**: `market_data_store` for persistence
- **Core**: `market_data_core` for data models

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker (optional, for full stack)
- Kubernetes cluster (optional, for KEDA autoscaling)

### Local Development Setup

```bash
# Clone the repository
git clone https://github.com/mjdevaccount/market_data_pipeline.git
cd market_data_pipeline

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Linux/macOS)
source .venv/bin/activate

# Install with development dependencies
pip install -e ".[dev,dag]"

# Run tests
pytest tests/ -v

# Start the API server
mdp run --config configs/dag/bars.yaml
```

### Docker Quick Start

```bash
# Start complete stack (pipeline + TimescaleDB)
docker compose up --build -d

# Run smoke test
./scripts/smoke_test.sh  # Linux/macOS
.\scripts\smoke_test.ps1  # Windows

# Check health
curl http://localhost:8083/health

# View metrics
curl http://localhost:8083/metrics

# Stop stack
docker compose down
```

### Simple Python Example

```python
from market_data_pipeline import create_pipeline

# Create a simple synthetic pipeline
pipeline = create_pipeline(
    tenant_id="demo",
    pipeline_id="quickstart",
    source="synthetic",
    symbols=["AAPL", "MSFT"],
    operator="bars",
    sink="store",
    duration_sec=30.0
)

# Run the pipeline
await pipeline.run()
await pipeline.close()
```

---

## 🏗️ Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Market Data Pipeline                           │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌────────────────────────────────────┐
        │     Unified Runtime (v0.8.1)       │
        │  ┌──────────────┬──────────────┐   │
        │  │ Classic Mode │  DAG Mode    │   │
        │  └──────────────┴──────────────┘   │
        └────────────────────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐    ┌───────────────┐
│   Sources     │     │   Operators   │    │    Sinks      │
│               │────▶│               │───▶│               │
│ • IBKR        │     │ • Bars        │    │ • Store       │
│ • Replay      │     │ • Options     │    │ • Kafka       │
│ • Synthetic   │     │ • Windows     │    │ • Database    │
│               │     │ • Partitions  │    │               │
└───────────────┘     └───────────────┘    └───────────────┘
        │                     │                     │
        └─────────────────────┴─────────────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │   Observability Layer    │
                │                          │
                │  • Prometheus Metrics    │
                │  • Health Checks         │
                │  • Structured Logs       │
                └──────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │   Kubernetes (KEDA Autoscaling)     │
        │                                     │
        │  ┌───────────┐    ┌──────────────┐ │
        │  │ Feedback  │───▶│ Rate         │ │
        │  │ Loop      │    │ Coordinator  │ │
        │  └───────────┘    └──────────────┘ │
        │         │                           │
        │         ▼                           │
        │  ┌────────────────────────────┐    │
        │  │ KEDA ScaledObject          │    │
        │  │ (Horizontal Autoscaling)   │    │
        │  └────────────────────────────┘    │
        └─────────────────────────────────────┘
```

### Data Flow

```
Sources          Operators         Batchers         Sinks
──────────       ─────────────     ────────────     ─────────
IBKR API    ──▶  SecondBar    ──▶  Hybrid      ──▶  Store
Replay File ──▶  Aggregator   ──▶  Batcher     ──▶  (TimescaleDB)
Synthetic   ──▶  Options      ──▶  (Row/Byte/  ──▶  Kafka
                 Chain            Time limits)
                 
                 ↓ Event Time
                 ↓ Watermarks
                 ↓ Windowing
```

### Phase 5: Streaming DAG Engine

```
┌────────────────────────────────────────────────────────────┐
│                    DAG Runtime (v0.8.0)                     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Provider ──▶ Channel ──▶ Operator ──▶ Channel ──▶ Sink   │
│     │            │           │            │          │     │
│     │            │           │            │          │     │
│  (IBKR)      (bounded)   (transform)  (bounded)  (persist) │
│                 ▲                         ▲                │
│                 │                         │                │
│            Backpressure              Watermarks            │
│                                                            │
│  Features:                                                 │
│  • Event-time windowing                                    │
│  • Hash partitioning                                       │
│  • Contrib operators (OHLC, dedupe, throttle, router)     │
│  • Provider adapters (IBKR → DAG)                          │
│  • Unified CLI (mdp run --config)                          │
└────────────────────────────────────────────────────────────┘
```

### Phase 6: Adaptive Autoscaling

```
┌────────────────────────────────────────────────────────────┐
│              Backpressure Feedback Loop (6.0A)              │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Store Queue  ──▶  FeedbackEvent  ──▶  FeedbackHandler    │
│  (9000/10000)      (level=HARD)        (scale=0.0)        │
│                                             │              │
│                                             ▼              │
│                                      RateCoordinator       │
│                                      (pause ingestion)     │
│                                                            │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                KEDA Autoscaling (6.0B)                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Metrics ──▶ Prometheus ──▶ KEDA ──▶ Kubernetes HPA       │
│  • queue_depth              Query     Scale: 1 → 8 pods   │
│  • backpressure_state       threshold                      │
│  • rate_scale_factor        (5000)                         │
│                                                            │
│  Result: Zero-touch horizontal scaling                     │
└────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Separation of Concerns**: Clean abstractions between sources, operators, and sinks
2. **Composability**: Any source ↔ operator ↔ sink combination works
3. **Resilience**: Built-in retry, backpressure, and graceful degradation
4. **Observability**: Metrics at every stage, health endpoints, clear bottleneck detection
5. **Performance**: Async I/O, bounded queues, efficient batching
6. **Type Safety**: Pydantic models, mypy validation

---

## 📦 Installation

### Standard Installation

```bash
# Basic installation
pip install -e .

# With development tools
pip install -e ".[dev]"

# With DAG runtime support
pip install -e ".[dag]"

# With all extras
pip install -e ".[dev,dag]"
```

### Optional Dependencies

```bash
# IBKR live data (separate repository)
pip install market-data-ibkr

# TimescaleDB persistence (separate repository)
pip install market-data-store

# Core data models (separate repository)
pip install market-data-core
```

### From Requirements

```bash
# Production dependencies (pinned versions)
pip install -r requirements.txt

# Development dependencies
pip install -r requirements.txt
pip install -e ".[dev,dag]"
```

### Docker Installation

```bash
# Build image
docker build -t mdp-pipeline:latest .

# Or use docker-compose
docker compose up --build
```

---

## 💻 Usage

### 1. CLI (mdp command)

#### Unified Runtime

```bash
# Run DAG mode with YAML config
mdp run --config configs/dag/bars.yaml

# Run classic mode
mdp run --config configs/classic/bars.yaml

# List available commands
mdp --help
```

#### Legacy CLI

```bash
# Simple synthetic pipeline
mdp-legacy run --tenant T1 --symbols AAPL,MSFT --rate 100 --duration 30

# Using JSON spec
mdp-legacy runspec --spec examples/synthetic.json

# Start API server
mdp-legacy api --port 8000
```

### 2. Python API

#### Simple API

```python
from market_data_pipeline import create_pipeline

# Quick start
pipeline = create_pipeline(
    tenant_id="demo",
    pipeline_id="simple",
    source="synthetic",
    symbols=["AAPL", "GOOGL"],
    operator="bars",
    sink="store",
    duration_sec=60.0
)

await pipeline.run()
```

#### Advanced Configuration

```python
from market_data_pipeline import PipelineBuilder, PipelineSpec, PipelineOverrides

builder = PipelineBuilder()
spec = PipelineSpec(
    tenant_id="production",
    pipeline_id="hft_bars",
    source="ibkr",
    symbols=["SPY", "QQQ", "IWM"],
    operator="bars",
    sink="store",
    overrides=PipelineOverrides(
        ticks_per_sec=1000,
        pacing_max_per_sec=5000,
        batch_size=2000,
        sink_workers=8,
        bar_window_sec=5,
        bar_allowed_lateness_sec=2
    )
)

pipeline = builder.build(spec)
await pipeline.run()
```

#### Unified Runtime API

```python
from market_data_pipeline.runtime import UnifiedRuntime
from market_data_pipeline.settings import UnifiedRuntimeSettings

# DAG mode
settings = UnifiedRuntimeSettings(
    mode="dag",
    dag={
        "graph": {
            "nodes": [
                {"id": "src", "type": "provider.ibkr.stream", "params": {...}},
                {"id": "op", "type": "operator.buffer", "params": {...}},
                {"id": "sink", "type": "operator.map", "params": {...}}
            ],
            "edges": [["src", "op"], ["op", "sink"]]
        }
    },
    feedback={"enable_feedback": True},
    metrics={"enable": True}
)

async with UnifiedRuntime(settings) as rt:
    await rt.run("my-job")
```

### 3. FastAPI Server

```bash
# Start server
uvicorn market_data_pipeline.runners.api:app --port 8083

# Health check
curl http://localhost:8083/health

# Create pipeline
curl -X POST http://localhost:8083/pipelines \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "T1",
    "pipeline_id": "test1",
    "source_type": "synthetic",
    "symbols": ["AAPL"],
    "rate": 100,
    "duration": 30
  }'

# Get metrics
curl http://localhost:8083/metrics
```

### 4. Docker Compose

```bash
# Start full stack
docker compose up -d

# View logs
docker compose logs -f pipeline

# Scale pipeline
docker compose up --scale pipeline=3

# Stop
docker compose down
```

---

## ⚙️ Configuration

### Configuration Methods

1. **Environment Variables** (`MDP_*` prefix)
2. **YAML Files** (`config.yaml`, custom configs)
3. **JSON Specs** (`examples/*.json`)
4. **Python Code** (PipelineOverrides, settings objects)

### Environment Variables

```bash
# Pipeline settings
export MDP_MODE=dag
export MDP_FB_ENABLE_FEEDBACK=true
export MDP_FB_PROVIDER_NAME=ibkr
export MDP_METRICS_ENABLE=true

# Database
export DATABASE_URL="postgresql://user:pass@localhost:5432/market_data"

# Kafka
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
export KAFKA_TOPIC="market_data"
```

### Example YAML Config

```yaml
# configs/dag/bars.yaml
mode: dag
dag:
  nodes:
    - id: ibkr_source
      type: provider.ibkr.stream
      params:
        stream: "bars"
        symbols: ["AAPL", "MSFT"]
        resolution: "5s"
    - id: buffer
      type: operator.buffer
      params:
        max_items: 500
    - id: store_sink
      type: operator.map
      params:
        fn_name: "store_bars"
  edges:
    - [ibkr_source, buffer]
    - [buffer, store_sink]
feedback:
  enable_feedback: true
  provider_name: ibkr
metrics:
  enable: true
```

### Configuration Overrides

```python
PipelineOverrides(
    # Source
    ticks_per_sec=500,
    pacing_max_per_sec=2000,
    
    # Operator
    bar_window_sec=5,
    bar_allowed_lateness_sec=1,
    
    # Batcher
    batch_size=1000,
    max_bytes=1024_000,
    flush_ms=50,
    drop_policy="oldest",
    
    # Sink
    sink_workers=4,
    sink_queue_max=500
)
```

---

## 🎯 DAG Runtime (Phase 5)

The DAG runtime provides a powerful streaming engine for composing data pipelines.

### Core Components

- **Channels**: Bounded queues with backpressure (high/low watermarks)
- **Operators**: Transform data (map, filter, buffer, window, partition)
- **Registry**: Component discovery and instantiation
- **Builder**: Graph construction from configuration

### Example DAG

```python
from market_data_pipeline.orchestration.dag import DagRuntime, Dag, Node, Edge

# Build DAG
dag = Dag()
dag.add_node(Node("source", meta={"type": "provider.ibkr.stream"}))
dag.add_node(Node("window", meta={"type": "operator.tumbling_window"}))
dag.add_node(Node("sink", meta={"type": "operator.map"}))
dag.add_edge(Edge("source", "window"))
dag.add_edge(Edge("window", "sink"))

# Run
runtime = DagRuntime(dag)
await runtime.run()
```

### Windowing

```python
from market_data_pipeline.orchestration.dag.windowing import (
    tumbling_window_event_time,
    TumblingWindowSpec
)

# 1-minute tumbling windows
async for frame in tumbling_window_event_time(
    source=data_stream,
    spec=TumblingWindowSpec(
        window_sec=60,
        watermark_lag_sec=5,
        allowed_lateness_sec=2
    )
):
    print(f"Window {frame.window_start} - {frame.window_end}: {len(frame.items)} items")
```

### Partitioning

```python
from market_data_pipeline.orchestration.dag.partitioning import hash_partition

# Partition by symbol
channels = await hash_partition(
    source=data_stream,
    key_fn=lambda item: item.symbol,
    num_partitions=4
)

# Process each partition
for i, channel in enumerate(channels):
    asyncio.create_task(process_partition(i, channel))
```

### Contrib Operators

```python
from market_data_pipeline.orchestration.dag.contrib.operators_contrib import (
    resample_ohlc,
    deduplicate,
    throttle,
    router
)

# OHLC resampling
bars = resample_ohlc(ticks, interval="1m")

# Deduplication
unique = deduplicate(stream, key_fn=lambda x: x.symbol, window_sec=10)

# Rate limiting
throttled = throttle(stream, max_per_sec=100)

# Routing
output_channels = router(stream, routes={
    "spy": lambda x: x.symbol == "SPY",
    "tech": lambda x: x.symbol in ["AAPL", "MSFT", "GOOGL"]
})
```

### Complete DAG Example

See `examples/run_dag_to_store.py` for a full example with IBKR → DAG operators → Store sink.

---

## 📈 KEDA Autoscaling (Phase 6)

### Phase 6.0A: Backpressure Feedback Loop

Dynamically adjusts pipeline ingestion rate based on downstream pressure.

```python
# Configuration
feedback:
  enable_feedback: true
  provider_name: ibkr
  policy:
    ok: 1.0    # Full rate
    soft: 0.5  # Half rate
    hard: 0.0  # Paused
```

**How It Works**:
1. Store queue fills → `FeedbackEvent` published
2. `FeedbackHandler` receives event → adjusts `RateCoordinator`
3. Pipeline slows ingestion → queue drains
4. Feedback returns to OK → rate restored

### Phase 6.0B: KEDA Horizontal Autoscaling

Automatically scales Kubernetes pods based on Prometheus metrics.

#### Metrics

```prometheus
# Queue depth (primary scaling metric)
pipeline_feedback_queue_depth{source="store_coordinator"}

# Backpressure state (0=ok, 1=soft, 2=hard)
pipeline_backpressure_state{provider="ibkr"}

# Rate scale factor (0.0-1.0)
pipeline_rate_scale_factor{provider="ibkr"}
```

#### Deployment

```bash
# Deploy to Kubernetes
kubectl apply -n market-data -f deploy/keda/deployment-pipeline.yaml
kubectl apply -n market-data -f deploy/keda/scaledobject-pipeline.yaml

# Watch scaling
kubectl get hpa -w
kubectl get pods -w
```

#### Scaling Behavior

| Condition | Queue | Backpressure | Pods |
|-----------|-------|--------------|------|
| **Idle** | < 2K | OK (0) | 1 |
| **Moderate** | 5-7K | SOFT (1) | 3-5 |
| **High** | 8-9K | SOFT (1) | 6-8 |
| **Critical** | 9K+ | HARD (2) | 10 (max) |

**Documentation**: See `docs/PHASE_6.0B_KEDA_AUTOSCALING.md` for complete guide.

---

## 🧑‍💻 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/mjdevaccount/market_data_pipeline.git
cd market_data_pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\Activate.ps1  # Windows

# Install with dev dependencies
pip install -e ".[dev,dag]"

# Setup pre-commit (optional)
pre-commit install
```

### Development Tools

```bash
# Code formatting
black src/ tests/
# or: ./scripts/dev.sh fmt

# Linting
ruff src/ tests/
# or: ./scripts/dev.sh lint

# Type checking
mypy src/

# Run tests
pytest tests/ -v
# or: ./scripts/dev.sh test

# Test coverage
pytest tests/ --cov=src --cov-report=html

# Clean caches
./scripts/dev.sh clean
```

### Project Structure

```
market_data_pipeline/
├── src/market_data_pipeline/   # Source code
│   ├── source/                 # Data sources (IBKR, Synthetic, Replay)
│   ├── operator/               # Transformations (Bars, Options)
│   ├── batcher/                # Flow control (HybridBatcher)
│   ├── sink/                   # Outputs (Store, Kafka, Database)
│   ├── orchestration/          # DAG runtime, RateCoordinator
│   │   ├── dag/                # DAG engine (Phase 5)
│   │   ├── feedback/           # Backpressure feedback (Phase 6.0A)
│   │   └── coordinator.py      # Rate coordination
│   ├── runtime/                # Unified runtime (Phase 5.0.5)
│   ├── cli/                    # CLI commands
│   ├── runners/                # Service runners (API, CLI)
│   ├── settings/               # Configuration management
│   └── metrics.py              # Prometheus metrics
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── load/                   # Load tests
├── examples/                   # Usage examples
├── docs/                       # Documentation
├── deploy/                     # Deployment manifests
│   └── keda/                   # KEDA autoscaling (Phase 6.0B)
├── scripts/                    # Development scripts
└── configs/                    # Configuration files
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests (requires database)
export DATABASE_URL="postgresql://user:pass@localhost:5432/market_data"
pytest tests/integration/ -v

# Load tests
pytest tests/load/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Contract tests (Core compatibility)
pytest tests/contracts/ -v
```

### Test Categories

- **Unit Tests** (`tests/unit/`): 150+ tests covering individual components
- **Integration Tests** (`tests/integration/`): End-to-end workflows
- **Load Tests** (`tests/load/`): Performance benchmarks
- **Contract Tests** (`tests/contracts/`): Core v1.1.0 compatibility validation

### Contract Tests

Contract tests verify compatibility with `market-data-core` protocol contracts:

```bash
# Run contract tests only
pytest tests/contracts/ -v

# Expected: 10 tests, ~4s duration
```

**Purpose**: These tests validate that Pipeline remains compatible with Core's
data transfer objects (DTOs) and protocols. They are automatically triggered
when Core publishes contract changes.

**Categories**:
- `test_core_install.py`: Core package imports and version compatibility
- `test_feedback_flow.py`: FeedbackEvent ↔ RateAdjustment transformations
- `test_protocol_conformance.py`: Protocol implementations (RateController, FeedbackPublisher)

**Note**: Contract tests are a minimal, fast subset of the full integration test suite.
See `tests/contracts/README.md` for details.

**Cross-Repo Testing**: These tests are triggered automatically by `market-data-core`
via GitHub Actions when Core's contract schemas change. See `.github/workflows/README.md`
for workflow documentation

### Pulse Integration (Phase 10.1)

The Pipeline subscribes to `telemetry.feedback` events from the Store via the Pulse event bus.

**Configuration**:

```bash
# Environment variables
PULSE_ENABLED=true                     # Enable Pulse (default: true)
EVENT_BUS_BACKEND=inmem                # inmem or redis (default: inmem)
REDIS_URL=redis://localhost:6379/0     # Redis connection (if backend=redis)
MD_NAMESPACE=mdp                       # Stream namespace
SCHEMA_TRACK=v1                        # Schema track (v1|v2)
```

**Running Pulse Tests**:

```bash
# Unit tests (inmem backend)
pytest tests/pulse/test_pulse_consumer.py -v

# Integration tests (redis backend, requires Redis)
EVENT_BUS_BACKEND=redis REDIS_URL=redis://localhost:6379/0 \
  pytest tests/pulse/test_redis_integration.py -v
```

**Metrics**:
- `pulse_consume_total{stream,track,outcome}` — Events consumed (success/error/duplicate)
- `pulse_lag_ms{stream}` — Consumer lag from event timestamp

### Key Test Files

```bash
tests/unit/
├── orchestration/
│   ├── test_coordinator_feedback.py     # Phase 6.0A (13 tests)
│   ├── test_feedback_handler.py         # Phase 6.0A (12 tests)
├── metrics/
│   └── test_pipeline_metrics.py         # Phase 6.0B (8 tests)
├── dag/
│   ├── test_channel_backpressure.py     # Phase 5.0.1
│   ├── test_windowing_event_time.py     # Phase 5.0.2
│   └── test_contrib_operators.py        # Phase 5.0.3
└── ...

tests/integration/
├── test_feedback_integration.py         # Phase 6.0A (5 tests)
├── test_e2e_synthetic_store.py          # End-to-end
└── ...
```

### Test Features

- ✅ **Async Support**: pytest-asyncio for async tests
- ✅ **Time Control**: freezegun for time-based testing
- ✅ **Windows-Safe**: Custom event loop fixtures
- ✅ **Optional Deps**: Graceful skipping when dependencies unavailable
- ✅ **Real Code Paths**: No mocks, tests exercise actual components

---

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build image
export REG="your-registry.example.com"
export TAG="0.8.1"
docker build -t $REG/mdp-pipeline:$TAG .
docker push $REG/mdp-pipeline:$TAG
```

### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace market-data

# Deploy pipeline
kubectl apply -n market-data -f deploy/keda/deployment-pipeline.yaml

# Deploy KEDA autoscaling
kubectl apply -n market-data -f deploy/keda/scaledobject-pipeline.yaml

# Deploy Prometheus ServiceMonitor
kubectl apply -n market-data -f deploy/keda/prometheus-servicemonitor.yaml

# Verify
kubectl -n market-data get pods
kubectl -n market-data get scaledobject
kubectl -n market-data get hpa
```

### Configuration

```bash
# Update deployment image
kubectl -n market-data set image deployment/mdp-pipeline \
  pipeline=$REG/mdp-pipeline:$TAG

# Update environment variables
kubectl -n market-data set env deployment/mdp-pipeline \
  MDP_FB_ENABLE_FEEDBACK=true \
  MDP_METRICS_ENABLE=true
```

### Rollback

```bash
# Quick rollback
kubectl -n market-data rollout undo deployment/mdp-pipeline

# Rollback to specific version
kubectl -n market-data rollout undo deployment/mdp-pipeline --to-revision=2
```

### Production Guides

- **Deployment**: See `PHASE_6.0_PRODUCTION_ROLLOUT.md`
- **Quick Reference**: See `PHASE_6.0_SHIP_IT_CHECKLIST.md`
- **Verification**: See `PHASE_6.0_VERIFICATION_REPORT.md`

---

## 📊 Monitoring & Observability

### Prometheus Metrics

50+ metrics exposed at `/metrics`:

```prometheus
# Source metrics
mdp_source_items_total{source,tenant,symbol}
mdp_source_status{source,tenant}
mdp_source_pacing_blocked_total{source,tenant}

# Operator metrics
operator_bars_generated_total{tenant,pipeline,operator}

# Batcher metrics
batcher_items_added_total{tenant,pipeline,batcher}
batcher_queue_depth{tenant,pipeline,batcher}

# Sink metrics
mdp_sink_batches_written_total{sink,tenant}
mdp_sink_commit_seconds{sink,tenant}
mdp_sink_queue_depth{sink,tenant}

# Phase 6.0B KEDA metrics
pipeline_rate_scale_factor{provider}
pipeline_backpressure_state{provider}
pipeline_feedback_queue_depth{source}
```

### Grafana Dashboard

```bash
# Import dashboard
kubectl -n monitoring apply -f monitoring/grafana-dashboard.json
```

**Panels**:
1. Queue Depth (time series)
2. Rate Scale Factor (gauge)
3. Backpressure State (stat)
4. Pod Count (stat)
5. Throughput (graph)
6. Latency (heatmap)

### Health Checks

```bash
# Application health
curl http://localhost:8083/health
# {"status":"healthy","service":"market-data-pipeline"}

# Kubernetes liveness
kubectl -n market-data get pods
# Shows READY 1/1

# Detailed status
curl http://localhost:8083/status
```

### Alerts

Recommended Prometheus alerts:

```yaml
# High queue depth
- alert: PipelineQueueHigh
  expr: pipeline_feedback_queue_depth > 8000
  for: 5m

# Hard backpressure
- alert: PipelineHardBackpressure
  expr: pipeline_backpressure_state == 2
  for: 2m

# Low rate scale
- alert: PipelineRateScaleLow
  expr: pipeline_rate_scale_factor < 0.3
  for: 10m
```

---

## 🔧 Extending the Pipeline

### Add a Custom Operator

```python
from market_data_pipeline.operator.base import StatefulOperator, EventTimePolicy

class VWAPOperator(StatefulOperator):
    def __init__(self, window_sec: int = 60):
        policy = EventTimePolicy(window_sec=window_sec)
        super().__init__(policy=policy)
        self._volume_prices = {}
        self._volumes = {}
        
    def _on_tick(self, tick: Quote) -> None:
        symbol = tick.symbol
        if symbol not in self._volume_prices:
            self._volume_prices[symbol] = 0.0
            self._volumes[symbol] = 0
            
        self._volume_prices[symbol] += tick.price * tick.size
        self._volumes[symbol] += tick.size
        
        # Check if window complete (via EventTimePolicy)
        if self._should_flush(tick.timestamp):
            vwap = self._volume_prices[symbol] / self._volumes[symbol]
            self._ready.append({"symbol": symbol, "vwap": vwap})
            self._volume_prices[symbol] = 0.0
            self._volumes[symbol] = 0
```

### Add a Custom Sink

```python
from market_data_pipeline.sink.base import Sink
from market_data_pipeline.sink.capabilities import SinkCapabilities

class S3Sink(Sink):
    def __init__(self, bucket: str, prefix: str):
        self.bucket = bucket
        self.prefix = prefix
        self.s3_client = None
        
    @property
    def capabilities(self) -> SinkCapabilities:
        return SinkCapabilities.BATCH_WRITES
        
    async def start(self) -> None:
        import aioboto3
        self.session = aioboto3.Session()
        self.s3_client = await self.session.client('s3')
        
    async def write(self, batch: List[Bar]) -> None:
        key = f"{self.prefix}/{batch[0].timestamp.date()}.parquet"
        df = pd.DataFrame([b.model_dump() for b in batch])
        buffer = io.BytesIO()
        df.to_parquet(buffer, engine='pyarrow')
        buffer.seek(0)
        
        await self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=buffer.getvalue()
        )
        
    async def close(self, drain: bool = True) -> None:
        if self.s3_client:
            await self.s3_client.close()
```

### Register Components

```python
from market_data_pipeline.orchestration.dag.registry import default_registry

registry = default_registry()
registry.register_operator("operator.vwap", VWAPOperator)
registry.register_sink("sink.s3", S3Sink)
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Run linters (`black .`, `ruff .`, `mypy src/`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards

- **Style**: Follow black formatting (88 char line length)
- **Linting**: Pass ruff checks
- **Type Hints**: Full type annotations (mypy strict mode)
- **Tests**: Add tests for new features (maintain >95% coverage)
- **Documentation**: Update README and docstrings

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `perf:` Performance improvements

### Pull Request Process

1. Update README.md with details of changes if applicable
2. Update documentation in `docs/` if needed
3. Add tests for new functionality
4. Ensure all tests pass
5. Request review from maintainers

---

## 📚 Documentation

### Core Documentation

- **[README.md](README.md)** - This file
- **[PIPELINE_BUILDER.md](docs/PIPELINE_BUILDER.md)** - Pipeline builder guide
- **[PRODUCTION.md](docs/PRODUCTION.md)** - Production deployment guide

### Phase Documentation

- **Phase 5: Streaming DAG Engine**
  - [Phase 5 Overview](PHASE_5_README.md)
  - [Phase 5.0.1: Core DAG Runtime](PHASE_5.0.1_IMPLEMENTATION_COMPLETE.md)
  - [Phase 5.0.2: Windowing & Partitioning](PHASE_5.0.2_IMPLEMENTATION_COMPLETE.md)
  - [Phase 5.0.3: Contrib Operators](PHASE_5.0.3_IMPLEMENTATION_COMPLETE.md)
  - [Phase 5.0.4: Provider Integration](PHASE_5.0.4_IMPLEMENTATION_COMPLETE.md)
  - [Phase 5.0.5: Unified Runtime](PHASE_5.0.5_IMPLEMENTATION_COMPLETE.md)

- **Phase 6: Adaptive Autoscaling**
  - [Phase 6.0A: Backpressure Feedback](PHASE_6.0A_IMPLEMENTATION_COMPLETE.md)
  - [Phase 6.0B: KEDA Autoscaling](PHASE_6.0B_IMPLEMENTATION_COMPLETE.md)
  - [KEDA Deployment Guide](docs/PHASE_6.0B_KEDA_AUTOSCALING.md)
  - [Production Rollout](PHASE_6.0_PRODUCTION_ROLLOUT.md)
  - [Ship It Checklist](PHASE_6.0_SHIP_IT_CHECKLIST.md)

### Examples

- **[examples/](examples/)** - Code examples
  - `run_dag_to_store.py` - Complete DAG example
  - `run_unified_runtime_basic.py` - Unified runtime example
  - `synthetic.json` - JSON spec example
  - And 15+ more examples

---

## 🗺️ Roadmap

### Completed ✅

- **v0.1-0.2**: Core abstractions, pipeline builder, JSON-spec
- **v0.7-0.8**: DAG runtime, unified runtime, adaptive autoscaling

### Current Version: v0.9.0

- ✅ Streaming DAG engine
- ✅ Event-time windowing
- ✅ Hash partitioning
- ✅ Backpressure feedback loop
- ✅ KEDA autoscaling
- ✅ 176 tests passing

### Future (v0.9+)

- **v0.9**: Enhanced IBKR integration
  - Reconnection handling
  - Pacing improvements
  - Error recovery

- **v1.0**: Multi-provider composite sources
  - Cross-exchange arbitrage
  - Provider failover
  - Data fusion

- **v1.1**: Advanced analytics
  - Volatility surfaces
  - Greeks aggregation
  - ML feature engineering

- **v1.2**: Horizontal scaling
  - Distributed DAG execution
  - Coordinator sharding
  - Cross-region deployment

---

## 🔗 Related Projects

- **[market_data_core](https://github.com/mjdevaccount/market_data_core)** - Core data models and provider SDKs
- **[market_data_store](https://github.com/mjdevaccount/market_data_store)** - TimescaleDB persistence layer
- **[market_data_ibkr](https://github.com/mjdevaccount/market_data_ibkr)** - IBKR provider implementation

---

## 📜 License

MIT License - see [LICENSE](LICENSE) for details

---

## 👥 Authors

- **Primary Developer** - [@mjdevaccount](https://github.com/mjdevaccount)

---

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **Prometheus** - Metrics collection
- **KEDA** - Kubernetes autoscaling
- **AsyncIO** - Asynchronous I/O

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/mjdevaccount/market_data_pipeline/issues)
- **Discussions**: [GitHub Discussions](https://github.com/mjdevaccount/market_data_pipeline/discussions)

---

<div align="center">

**Made with ❤️ for the trading community**

[⬆ Back to Top](#-market-data-pipeline)

</div>
