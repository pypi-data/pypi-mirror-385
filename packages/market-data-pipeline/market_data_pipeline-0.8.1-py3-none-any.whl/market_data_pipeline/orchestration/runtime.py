"""
PipelineRuntime — high-level orchestrator that ties together the
registry, router, rate coordinator, and existing PipelineService.

This is the main opt-in orchestration API for market-data pipelines.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncIterator, Dict, List, Optional

from ..config import PipelineSettings
from ..runners.service import PipelineService, PipelineSpec
from ..types import Quote
from .coordinator import RateCoordinator
from .registry import SourceRegistry
from .router import SourceRouter

logger = logging.getLogger(__name__)


class PipelineRuntimeSettings:
    """Settings for PipelineRuntime orchestration.
    
    Extends base PipelineSettings with orchestration-specific configuration.
    
    Attributes:
        pipeline: Base pipeline settings
        orchestration_enabled: Enable orchestration features
        max_concurrent_pipelines: Maximum concurrent pipelines
        enable_rate_coordination: Enable global rate limiting
        circuit_breaker_threshold: Failures before circuit opens
        circuit_breaker_timeout_sec: Circuit open duration
        providers: Provider-specific settings (future)
    """

    def __init__(
        self,
        pipeline: Optional[PipelineSettings] = None,
        orchestration_enabled: bool = True,
        max_concurrent_pipelines: int = 10,
        enable_rate_coordination: bool = True,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout_sec: float = 60.0,
        providers: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize runtime settings.
        
        Args:
            pipeline: Base pipeline settings (uses defaults if None)
            orchestration_enabled: Enable orchestration features
            max_concurrent_pipelines: Max concurrent pipelines
            enable_rate_coordination: Enable global rate limiting
            circuit_breaker_threshold: Failures before circuit opens
            circuit_breaker_timeout_sec: Circuit open duration
            providers: Provider-specific settings dict
        """
        self.pipeline = pipeline or PipelineSettings()
        self.orchestration_enabled = orchestration_enabled
        self.max_concurrent_pipelines = max_concurrent_pipelines
        self.enable_rate_coordination = enable_rate_coordination
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout_sec = circuit_breaker_timeout_sec
        self.providers = providers or {}


class PipelineRuntime:
    """Opt-in orchestration entrypoint for market-data pipelines.
    
    Provides a unified API that coordinates multiple sources, manages
    rate limits, and orchestrates pipeline execution.
    
    Example:
        settings = PipelineRuntimeSettings()
        
        async with PipelineRuntime(settings) as runtime:
            # Stream quotes with automatic routing
            async for quote in runtime.stream_quotes(["AAPL", "MSFT"]):
                print(quote)
            
            # Or run a full pipeline
            spec = PipelineSpec(...)
            await runtime.run_pipeline(spec)
    """

    def __init__(self, settings: Optional[PipelineRuntimeSettings] = None) -> None:
        """Initialize pipeline runtime.
        
        Args:
            settings: Runtime settings (uses defaults if None)
        """
        self.settings = settings or PipelineRuntimeSettings()
        
        # Core orchestration components
        self.registry = SourceRegistry()
        self.rate_coordinator: Optional[RateCoordinator] = None
        self.router: Optional[SourceRouter] = None
        
        # Pipeline service for managing multiple pipelines
        self.service = PipelineService(self.settings.pipeline)
        
        # Runtime state
        self._initialized = False
        self._sources: Dict[str, Any] = {}
        
        # Phase 10.1: Pulse consumer task
        self._pulse_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize registry, sources, router, and rate controls.
        
        This method:
        1. Registers available sources
        2. Initializes rate coordinator
        3. Creates source router
        4. Starts pipeline service
        """
        if self._initialized:
            logger.warning("Runtime already initialized")
            return
        
        logger.info("Initializing PipelineRuntime...")
        
        # Register built-in sources
        await self._register_builtin_sources()
        
        # Discover external providers via entrypoints
        try:
            self.registry.discover_entrypoints()
        except Exception as e:
            logger.warning("Failed to discover entrypoints: %s", e)
        
        # Initialize rate coordinator if enabled
        if self.settings.enable_rate_coordination:
            self.rate_coordinator = RateCoordinator()
            await self._register_provider_rate_limits()
        
        # Start pipeline service
        await self.service.start()
        
        # Phase 10.1: Start Pulse feedback consumer
        await self._start_pulse_consumer()
        
        self._initialized = True
        logger.info("PipelineRuntime initialized successfully")

    async def _register_builtin_sources(self) -> None:
        """Register built-in source implementations."""
        try:
            from ..source.synthetic import SyntheticSource
            self.registry.register("synthetic", SyntheticSource)
            logger.debug("Registered synthetic source")
        except ImportError:
            logger.warning("SyntheticSource not available")
        
        try:
            from ..source.replay import ReplaySource
            self.registry.register("replay", ReplaySource)
            logger.debug("Registered replay source")
        except ImportError:
            logger.debug("ReplaySource not available")
        
        try:
            from ..source.ibkr import IBKRSource
            self.registry.register("ibkr", IBKRSource)
            logger.debug("Registered IBKR source")
        except ImportError:
            logger.debug("IBKRSource not available")

    async def _register_provider_rate_limits(self) -> None:
        """Register rate limits for known providers."""
        if not self.rate_coordinator:
            return
        
        # Register IBKR rate limits
        # IBKR has different limits for different data types
        # Market data: ~60 requests/sec, Historical: ~60 requests/10min
        self.rate_coordinator.register_provider(
            name="ibkr",
            capacity=60,  # Burst capacity
            refill_rate=60,  # 60/sec refill
            cooldown_sec=600,  # 10 min cooldown on pacing errors
            breaker_threshold=self.settings.circuit_breaker_threshold,
            breaker_timeout=self.settings.circuit_breaker_timeout_sec,
        )
        logger.info("Registered IBKR rate limits")

    async def _start_pulse_consumer(self) -> None:
        """Start Pulse feedback consumer if enabled (Phase 10.1)."""
        try:
            from ..pulse import PulseConfig, FeedbackConsumer
            from ..settings.feedback import PipelineFeedbackSettings
            from .feedback.consumer import RateCoordinatorAdapter
            
            pulse_cfg = PulseConfig()
            if not pulse_cfg.enabled:
                logger.info("[pulse] Disabled (PULSE_ENABLED=false)")
                return
            
            if not self.rate_coordinator:
                logger.warning("[pulse] No rate coordinator, skipping consumer")
                return
            
            # Setup feedback consumer
            feedback_settings = PipelineFeedbackSettings()
            rate_controller = RateCoordinatorAdapter(self.rate_coordinator)
            consumer = FeedbackConsumer(rate_controller, feedback_settings, pulse_cfg)
            
            # Start consumer task
            self._pulse_task = asyncio.create_task(consumer.run("pipeline_w1"))
            logger.info("[pulse] Feedback consumer started (backend=%s)", pulse_cfg.backend)
        
        except ImportError as e:
            logger.warning("[pulse] Import failed, consumer disabled: %s", e)
        except Exception as e:
            logger.error("[pulse] Failed to start consumer: %s", e)

    async def _stop_pulse_consumer(self) -> None:
        """Stop Pulse feedback consumer gracefully (Phase 10.1)."""
        if self._pulse_task:
            logger.info("[pulse] Stopping feedback consumer...")
            self._pulse_task.cancel()
            try:
                await self._pulse_task
            except asyncio.CancelledError:
                logger.info("[pulse] Feedback consumer stopped")
            except Exception as e:
                logger.error("[pulse] Error stopping consumer: %s", e)
            finally:
                self._pulse_task = None

    async def stream_quotes(
        self,
        symbols: List[str],
        source_priority: Optional[List[str]] = None,
    ) -> AsyncIterator[Quote]:
        """Unified quote stream API with automatic routing.
        
        This is a high-level API that automatically routes to available
        sources with fallback.
        
        Args:
            symbols: List of symbols to stream
            source_priority: Optional ordered list of sources to try
            
        Yields:
            Quote objects from available sources
            
        Example:
            async for quote in runtime.stream_quotes(["AAPL", "MSFT"]):
                print(f"{quote.symbol}: ${quote.price}")
        """
        if not self._initialized:
            await self.initialize()
        
        # Determine which sources to use
        sources = source_priority or ["synthetic"]  # Default to synthetic for now
        
        # Create source instances
        source_instances = []
        for source_name in sources:
            try:
                source_cls = self.registry.load(source_name)
                # TODO: Proper source configuration from settings
                # For now, create with minimal config
                if source_name == "synthetic":
                    from ..context import PipelineContext
                    ctx = PipelineContext(tenant_id="runtime", pipeline_id="stream")
                    source = source_cls(
                        symbols=symbols,
                        ticks_per_sec=10,
                        pacing_budget=(1000, 1000),
                        ctx=ctx,
                    )
                    source_instances.append(source)
                else:
                    logger.warning("Source %s needs configuration, skipping", source_name)
            except Exception as e:
                logger.warning("Failed to create source %s: %s", source_name, e)
        
        if not source_instances:
            raise RuntimeError("No sources available for streaming")
        
        # Create router
        router = SourceRouter(sources=source_instances, strategy="first")
        
        # Stream quotes
        try:
            async for quote in router.stream():
                # Apply rate limiting if enabled
                if self.rate_coordinator:
                    try:
                        await self.rate_coordinator.acquire("synthetic")  # TODO: dynamic provider
                    except Exception as e:
                        logger.warning("Rate limit error: %s", e)
                        continue
                
                yield quote
        finally:
            await router.close()

    async def run_pipeline(self, spec: PipelineSpec) -> str:
        """Run a pipeline spec using the underlying service.
        
        Args:
            spec: Pipeline specification
            
        Returns:
            Pipeline key
        """
        if not self._initialized:
            await self.initialize()
        
        return await self.service.create_pipeline(spec)

    async def list_pipelines(self) -> List[str]:
        """List all running pipelines.
        
        Returns:
            List of pipeline keys
        """
        return await self.service.list_pipelines()

    async def stop_pipeline(self, key: str) -> None:
        """Stop a running pipeline.
        
        Args:
            key: Pipeline key (tenant_id:pipeline_id)
        """
        await self.service.delete_pipeline(key)

    async def shutdown(self) -> None:
        """Gracefully stop all pipelines and cleanup."""
        logger.info("Shutting down PipelineRuntime...")
        
        # Phase 10.1: Stop Pulse consumer
        await self._stop_pulse_consumer()
        
        # Stop pipeline service
        await self.service.stop()
        
        # Close any active sources
        for source in self._sources.values():
            try:
                if hasattr(source, "close"):
                    await source.close()
            except Exception as e:
                logger.warning("Error closing source: %s", e)
        
        self._initialized = False
        logger.info("PipelineRuntime shutdown complete")

    async def __aenter__(self) -> PipelineRuntime:
        """Context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        """Context manager exit."""
        await self.shutdown()

