# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-10-18

### Added
- **Phase 10.1: Pulse Event Bus Integration**
  - New `pulse/` module for consuming `telemetry.feedback` events
  - Support for InMemory (dev/test) and Redis Streams (prod) backends
  - Idempotency, ACK/FAIL, DLQ support via Core event bus
  - CI matrix: schema track (v1/v2) × backend (inmem/redis)
  - Metrics: `pulse_consume_total`, `pulse_lag_ms`
  - `.github/workflows/_pulse_reusable.yml`: Matrix testing workflow
  - `.github/workflows/dispatch_pulse.yml`: Dispatch handler for Core fanout
  - Graceful consumer startup/shutdown in `PipelineRuntime`
  - `tests/pulse/`: Unit tests (inmem) + integration tests (redis)

### Changed
- **Core Dependency**: Upgraded from `>=1.1.1` to `>=1.2.0,<2.0.0` (Pulse support)
- Runtime automatically starts Pulse consumer when `PULSE_ENABLED=true`

### Documentation
- Added Pulse Integration section to README
- Added `PHASE_10.1_VIABILITY_ASSESSMENT.md`: Technical analysis and requirements
- Added `PHASE_10.1_IMPLEMENTATION_PLAN.md`: Complete implementation guide

## [0.10.0] - 2025-10-17

### Added
- **Phase 8.0C: Cross-Repo Orchestration**
  - GitHub Actions workflows for automated contract testing
  - `.github/workflows/dispatch_contracts.yml`: Entry point for Core fan-out triggers
  - `.github/workflows/_contracts_reusable.yml`: Reusable workflow for contract tests
  - `tests/contracts/` test suite (10 tests) for Core v1.1.0+ compatibility validation
  - Automatic testing triggered by `market-data-core` contract changes
  - Workflow documentation in `.github/workflows/README.md`
  - Contract tests README in `tests/contracts/README.md`

### Changed
- **Core Dependency**: Upgraded from `market-data-core>=1.1.0` to `>=1.1.1`
- Verified compatibility with Core v1.1.1 (all 10 contract tests pass)
- Reorganized contract tests from `tests/integration/` into dedicated `tests/contracts/` suite
- Contract tests now optimized for CI/CD speed (< 1 second execution)
- Organized all phase documentation into `phases/` directory

### Documentation
- Added `CORE_INTEGRATION_GUIDE_VIABILITY.md`: Core v1.1.1 integration guide compliance assessment
- Added `CORE_V1.1.1_UPGRADE_PLAN.md`: Core upgrade action plan
- Added `PHASE_8.0C_VIABILITY_ASSESSMENT.md`: Detailed viability analysis
- Added `PHASE_8.0C_IMPLEMENTATION_PLAN.md`: Step-by-step implementation guide
- Added `PHASE_8.0C_EXECUTIVE_SUMMARY.md`: High-level overview and recommendations
- Updated README.md with contract testing documentation section
- Created `phases/README.md` with complete documentation index

## [0.9.0] - 2025-10-17

### Added
- **Core v1.1.0 Integration**: Full adoption of market-data-core v1.1.0 telemetry & feedback contracts
- **Type-Safe Feedback System**: FeedbackEvent and RateAdjustment DTOs replace duck-typed events
- **Protocol Conformance**: RateController and FeedbackPublisher protocols from Core
- **Enum-Based Backpressure**: BackpressureLevel enum (ok/soft/hard) replaces string literals
- **RateCoordinatorAdapter**: Clean adapter implementing Core RateController protocol

### Changed
- **FeedbackHandler Signature**: Now accepts `FeedbackEvent` instead of `Any` (breaking change)
- **FeedbackBus Protocol**: Implements Core `FeedbackPublisher` protocol
- **Policy Mapping**: Uses `BackpressureLevel` enum keys instead of string keys
- **Metrics Labels**: Prometheus metrics now use Core enum values for consistency

### Removed
- **Local Protocol Definitions**: Replaced local `RateCoordinator` Protocol with Core version
- **Duck-Typed Events**: All feedback events now use Core DTOs

### Technical Details
- **Core Dependency**: Added `market-data-core>=1.1.0` as required dependency
- **Protocol-First Design**: Maintains clean separation via Protocol conformance
- **Backward Compatibility**: Phase 6.0 feedback system refactored to use Core contracts
- **Zero New Endpoints**: Pipeline remains consumer-only (no health/control surfaces)
- **Test Coverage**: All 176+ tests updated to use Core DTOs

### Migration Notes
- Update any code importing `RateCoordinator` Protocol to use Core version
- Replace mock `FeedbackEvent` objects with Core DTOs in tests
- Update string-based backpressure level comparisons to enum comparisons
- See `docs/PHASE_8.0_MIGRATION_GUIDE.md` for detailed migration path

### References
- Phase 8.0 Implementation Plan
- Core v1.1.0 Release: https://github.com/mjdevaccount/market-data-core/releases/tag/v1.1.0

---

## [0.1.0] - 2024-09-27

### Added
- **Initial Release**: Complete market data pipeline orchestration layer
- **Core Architecture**: Source → Operator → Batcher → Sink pipeline with event-time processing
- **Sources**: SyntheticSource, ReplaySource (stub), IBKRSource (stub)
- **Operators**: SecondBarAggregator with OHLCV/VWAP aggregation and out-of-order handling
- **Batchers**: HybridBatcher with size/byte/time thresholds and backpressure
- **Sinks**: StoreSink (TimescaleDB via AMDS), KafkaSink (stub)
- **Event-Time Processing**: Watermark-based windowing with configurable lateness tolerance
- **Flow Control**: Bounded queues, drop policies (oldest/newest), pacing compliance
- **Telemetry**: Comprehensive Prometheus metrics for observability
- **API**: FastAPI-based REST API for pipeline management
- **CLI**: Command-line interface for local pipeline execution
- **Testing**: Comprehensive unit and integration test suites
- **Docker**: Multi-stage containerization with health checks
- **Development Tooling**: Cross-platform development scripts (PowerShell/Bash/Makefile)
- **Documentation**: Complete README with architecture, usage, and deployment guides

### Features
- **Event-Time Correctness**: Proper handling of out-of-order ticks with watermarks
- **Bounded Memory**: At most 2 active windows per symbol to prevent memory leaks
- **Backpressure Handling**: Configurable drop policies and queue management
- **Retry Logic**: Exponential backoff for transient errors
- **Idempotent Writes**: Relies on downstream store guarantees for deduplication
- **Cross-Platform**: Windows PowerShell, Linux/macOS Bash, and Unix Makefile support
- **Production Ready**: Docker deployment, health checks, and comprehensive monitoring

### Technical Details
- **Python 3.11+**: Modern async/await patterns with asyncio
- **Type Safety**: Full MyPy type checking with strict configuration
- **Code Quality**: Black formatting, Ruff linting, comprehensive test coverage
- **Dependencies**: Pydantic, FastAPI, Prometheus, OpenTelemetry, Click, Structlog
- **Containerization**: Multi-stage Docker builds with non-root execution
- **Observability**: Prometheus metrics, structured logging, health endpoints

### Roadmap
- **v0.2**: ReplaySource implementation for CSV/Parquet historical data
- **v0.3**: IBKRSource with real error handling and pacing
- **v0.4**: OptionsChainOperator with Greeks calculation
- **v0.5**: KafkaSink for streaming fan-out
- **v0.6**: Autoscaling hooks (KEDA integration)
