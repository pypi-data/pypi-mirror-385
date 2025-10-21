from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from loguru import logger

# Settings live next to this file to keep the surface area small.
from market_data_pipeline.settings.runtime_unified import UnifiedRuntimeSettings

# -------- Exceptions / State --------------------------------------------------

class UnifiedRuntimeError(RuntimeError):
    pass


class RuntimeMode(str, Enum):
    CLASSIC = "classic"
    DAG = "dag"


@dataclass(frozen=True)
class UnifiedRuntimeState:
    mode: RuntimeMode
    started: bool


# -------- Internal adapters (lazy-import to avoid hard deps) ------------------

class _ClassicFacade:
    """
    Thin wrapper around the existing Classic runtime pieces (PipelineService / Builder).
    We duck-type imports so older trees still work and tests can mock easily.
    """

    def __init__(self, settings: UnifiedRuntimeSettings) -> None:
        self._settings = settings
        self._service = None  # PipelineService
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        try:
            from market_data_pipeline.pipeline_builder import PipelineBuilder
            from market_data_pipeline.runners.service import PipelineService
        except Exception as exc:  # pragma: no cover
            msg = "Classic runtime dependencies not available (service/builder)."
            raise UnifiedRuntimeError(msg) from exc

        # Initialize service
        self._service = PipelineService(self._settings.classic.service or {})
        await self._service.start()
        self._builder = PipelineBuilder(self._settings.classic.builder or {})
        self._started = True
        logger.info("[UnifiedRuntime/Classic] started")

    async def stop(self) -> None:
        if not self._started:
            return
        try:
            await self._service.stop()  # type: ignore[attr-defined]
        finally:
            self._started = False
            logger.info("[UnifiedRuntime/Classic] stopped")

    async def run(self, name: str | None = None) -> str:
        """
        Create and start a pipeline from classic spec.
        Returns the pipeline id/handle from PipelineService.
        """
        if not self._started:
            msg = "Classic runtime not started"
            raise UnifiedRuntimeError(msg)

        spec: dict = self._settings.classic.spec or {}
        if not spec:
            msg = "Classic mode requires 'classic.spec' in settings"
            raise UnifiedRuntimeError(msg)

        # Build pipeline instance from spec via builder, then submit to service.
        pipeline = self._builder.create_pipeline(spec)  # type: ignore[attr-defined]
        result = await self._service.create_and_run_pipeline(  # type: ignore[attr-defined]
            pipeline=pipeline,
            name=name or spec.get("name", "classic-job"),
        )
        logger.info("[UnifiedRuntime/Classic] running pipeline: {}", result)
        return str(result)


class _DagFacade:
    """
    Wrapper around the DAG runtime orchestrator built in phase 5.0.x.
    """

    def __init__(self, settings: UnifiedRuntimeSettings) -> None:
        self._settings = settings
        self._runtime = None
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        try:
            from market_data_pipeline.orchestration.dag.builder import (
                build_dag_from_dict,
            )
            from market_data_pipeline.orchestration.dag.registry import (
                default_registry,
            )
            from market_data_pipeline.orchestration.dag.runtime import DagRuntime
            from market_data_pipeline.orchestration.runtime_orchestrator import (
                RuntimeOrchestrator,
            )
        except Exception as exc:  # pragma: no cover
            msg = "DAG runtime dependencies not available."
            raise UnifiedRuntimeError(msg) from exc

        # Build a Dag from the provided graph dict using builder and registry
        if isinstance(self._settings.dag, dict):
            dag_config = self._settings.dag
        else:
            dag_config = self._settings.dag.model_dump()

        if not dag_config or not dag_config.get("graph"):
            msg = "DAG mode requires 'dag.graph' in settings"
            raise UnifiedRuntimeError(msg)

        # Transform config: settings has dag.graph, builder expects dag with nodes/edges
        graph_spec = dag_config.get("graph", {})
        builder_config = {"dag": graph_spec}

        # Use the registry and builder
        self._registry = default_registry()
        self._dag = build_dag_from_dict(builder_config, self._registry)
        self._runtime = DagRuntime(self._dag)
        # Orchestrator remains available for helpers (providers/registry),
        # but not required to start.
        self._orchestrator = RuntimeOrchestrator()
        
        # Phase 8.0: Setup backpressure feedback with Core contracts if enabled
        self._feedback_handler = None
        if self._settings.feedback.enable_feedback:
            try:
                from market_data_pipeline.orchestration.coordinator import RateCoordinator
                from market_data_pipeline.orchestration.feedback import (
                    FeedbackHandler,
                    RateCoordinatorAdapter,
                    feedback_bus,
                )
                
                # Create or get RateCoordinator
                # NOTE: In a full implementation, this would be shared across the system
                # For now, create a minimal one for demonstration
                self._rate_coordinator = RateCoordinator()
                self._rate_coordinator.register_provider(
                    self._settings.feedback.provider_name,
                    capacity=100,
                    refill_rate=60
                )
                
                # Phase 8.0: Wrap coordinator in adapter for Core protocol compliance
                adapter = RateCoordinatorAdapter(self._rate_coordinator)
                
                # Create feedback handler with Core protocol adapter
                self._feedback_handler = FeedbackHandler(
                    rate=adapter,
                    provider=self._settings.feedback.provider_name,
                    policy=self._settings.feedback.get_policy()
                )
                
                # Subscribe to feedback bus
                feedback_bus().subscribe(self._feedback_handler.handle)
                
                logger.info(
                    "[UnifiedRuntime/DAG] Feedback enabled for provider: %s",
                    self._settings.feedback.provider_name
                )
            except Exception as exc:  # pragma: no cover
                logger.warning(
                    "[UnifiedRuntime/DAG] Failed to setup feedback: %s. Continuing without feedback.",
                    exc
                )
        
        self._started = True
        logger.info("[UnifiedRuntime/DAG] started")

    async def stop(self) -> None:
        if not self._started:
            return
        try:
            # DagRuntime does not maintain background tasks by default; if yours does,
            # ensure it has a proper shutdown method and call it here.
            pass
        finally:
            self._started = False
            logger.info("[UnifiedRuntime/DAG] stopped")

    async def run(self, name: str | None = None) -> str:
        if not self._started:
            msg = "DAG runtime not started"
            raise UnifiedRuntimeError(msg)

        job_name = name or (self._settings.dag.name or "dag-job")
        # Execute Dag runtime (blocking until completion if the graph is finite).
        stats = await self._runtime.start()  # type: ignore[attr-defined]
        logger.info(
            "[UnifiedRuntime/DAG] executed DAG job '{}' - Stats: {} tasks", 
            job_name, 
            len(stats.node_stats) if hasattr(stats, 'node_stats') else 0
        )
        return job_name


# -------- Public Facade ------------------------------------------------------

class UnifiedRuntime:
    """
    Facade over Classic and DAG runtimes with identical UX.

    Usage:
        settings = UnifiedRuntimeSettings(mode="classic", classic={...})
        async with UnifiedRuntime(settings) as rt:
            await rt.run("my_job")

        settings = UnifiedRuntimeSettings(mode="dag", dag={"graph": {...}})
        async with UnifiedRuntime(settings) as rt:
            await rt.run("dag_job")
    """

    def __init__(self, settings: UnifiedRuntimeSettings) -> None:
        self._settings = settings
        self._mode = RuntimeMode(self._settings.mode.value)
        self._impl: _ClassicFacade | _DagFacade | None = None
        self._state = UnifiedRuntimeState(mode=self._mode, started=False)

    # Async context manager
    async def __aenter__(self) -> UnifiedRuntime:
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.stop()

    # Lifecycle
    async def start(self) -> None:
        if self._state.started:
            return

        if self._mode == RuntimeMode.CLASSIC:
            self._impl = _ClassicFacade(self._settings)
        else:
            self._impl = _DagFacade(self._settings)

        await self._impl.start()
        
        # Phase 6.0B: Start standalone metrics server if configured
        if self._settings.metrics.enable and self._settings.metrics.standalone_port:
            try:
                from prometheus_client import start_http_server  # type: ignore

                port = int(self._settings.metrics.standalone_port)
                start_http_server(port)
                logger.info(
                    f"[UnifiedRuntime] Standalone Prometheus server started on port {port}"
                )
            except Exception as e:  # pragma: no cover
                logger.warning(
                    f"[UnifiedRuntime] Failed to start standalone Prometheus server: {e}"
                )
        
        self._state = UnifiedRuntimeState(mode=self._mode, started=True)

    async def stop(self) -> None:
        if not self._state.started or not self._impl:
            return
        await self._impl.stop()
        self._state = UnifiedRuntimeState(mode=self._mode, started=False)

    # Run
    async def run(self, name: str | None = None) -> str:
        if not self._impl or not self._state.started:
            msg = "Runtime not started; call start() or use 'async with'."
            raise UnifiedRuntimeError(msg)

        return await self._impl.run(name)

    # Introspection
    @property
    def state(self) -> UnifiedRuntimeState:
        return self._state

    @property
    def mode(self) -> RuntimeMode:
        return self._mode


# -------- Metrics Integration (Optional) ---------------------------------------

# Metrics integration (optional) - gracefully degrade if prometheus not available
try:
    from prometheus_client import Gauge

    _metric_runtime_up = Gauge("runtime_up", "Runtime health status", ["mode"])
    _metric_runtime_jobs = Gauge(
        "runtime_jobs_running", "Jobs currently active", ["mode"]
    )
    _METRICS_AVAILABLE = True
except Exception:  # pragma: no cover
    _metric_runtime_up = None
    _metric_runtime_jobs = None
    _METRICS_AVAILABLE = False


# Patch metrics into UnifiedRuntime methods
if _METRICS_AVAILABLE:
    _original_start = UnifiedRuntime.start

    async def _start_with_metrics(self: UnifiedRuntime) -> None:
        await _original_start(self)
        if _metric_runtime_up:
            _metric_runtime_up.labels(mode=self._mode.value).set(1)

    UnifiedRuntime.start = _start_with_metrics  # type: ignore[method-assign]

    _original_stop = UnifiedRuntime.stop

    async def _stop_with_metrics(self: UnifiedRuntime) -> None:
        await _original_stop(self)
        if _metric_runtime_up:
            _metric_runtime_up.labels(mode=self._mode.value).set(0)

    UnifiedRuntime.stop = _stop_with_metrics  # type: ignore[method-assign]

    _original_run = UnifiedRuntime.run

    async def _run_with_metrics(self: UnifiedRuntime, name: str | None = None) -> str:
        if _metric_runtime_jobs:
            _metric_runtime_jobs.labels(mode=self._mode.value).inc()
        try:
            return await _original_run(self, name)
        finally:
            if _metric_runtime_jobs:
                _metric_runtime_jobs.labels(mode=self._mode.value).dec()

    UnifiedRuntime.run = _run_with_metrics  # type: ignore[method-assign]
