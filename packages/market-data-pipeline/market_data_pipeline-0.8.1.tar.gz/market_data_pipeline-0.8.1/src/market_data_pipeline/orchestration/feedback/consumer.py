"""
FeedbackHandler: Translates backpressure events into rate adjustments.

Phase 8.0 implementation using Core v1.1.0 contracts.
Refactored from Phase 6.0A to use Core telemetry DTOs and protocols.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from loguru import logger
from market_data_core.protocols import RateController
from market_data_core.telemetry import (
    BackpressureLevel,
    FeedbackEvent,
    RateAdjustment,
)

if TYPE_CHECKING:
    from typing import Any
    from typing import Protocol
    
    # Legacy interface for backward compatibility
    class _LegacyRateCoordinator(Protocol):
        """Legacy RateCoordinator interface from Phase 6.0."""
        async def set_global_pressure(self, provider: str, level: str) -> None: ...
        async def set_budget_scale(self, provider: str, scale: float) -> None: ...


class RateCoordinatorAdapter(RateController):
    """
    Adapter that wraps legacy RateCoordinator to implement Core RateController protocol.
    
    This allows gradual migration from Phase 6.0 to Phase 8.0 by adapting
    the old set_global_pressure/set_budget_scale interface to Core's apply() method.
    
    Example:
        legacy_coordinator = RateCoordinator()  # Phase 6.0 instance
        adapter = RateCoordinatorAdapter(legacy_coordinator)
        adjustment = RateAdjustment(provider="ibkr", scale=0.5, reason=BackpressureLevel.soft, ts=time.time())
        await adapter.apply(adjustment)
    """
    
    def __init__(self, coordinator: _LegacyRateCoordinator) -> None:
        """
        Initialize adapter with legacy coordinator.
        
        Args:
            coordinator: Legacy RateCoordinator with set_global_pressure/set_budget_scale methods
        """
        self.coordinator = coordinator
    
    async def apply(self, adjustment: RateAdjustment) -> None:
        """
        Apply rate adjustment using Core RateController protocol.
        
        Translates Core RateAdjustment to legacy coordinator method calls.
        
        Args:
            adjustment: Core RateAdjustment DTO with provider, scale, reason, ts
        """
        # Convert BackpressureLevel enum to string for legacy interface
        level_str = adjustment.reason.value
        
        # Call legacy methods
        await self.coordinator.set_global_pressure(adjustment.provider, level_str)
        await self.coordinator.set_budget_scale(adjustment.provider, adjustment.scale)


class FeedbackHandler:
    """
    Translates store FeedbackEvent into pipeline-level rate signals.
    
    Phase 8.0: Now uses Core v1.1.0 DTOs and protocols.
    
    Policy (enum-based):
      - BackpressureLevel.ok   → scale 1.0 (full rate)
      - BackpressureLevel.soft → scale 0.5 (half rate)
      - BackpressureLevel.hard → scale 0.0 (paused)
    
    Example:
        from market_data_core.protocols import RateController
        from market_data_core.telemetry import FeedbackEvent, BackpressureLevel
        
        # Phase 8.0 (with Core protocol)
        rate_controller = RateCoordinatorAdapter(legacy_coordinator)
        handler = FeedbackHandler(rate=rate_controller, provider="ibkr")
        
        event = FeedbackEvent(
            coordinator_id="store_01",
            queue_size=800,
            capacity=1000,
            level=BackpressureLevel.soft,
            source="store",
            ts=time.time()
        )
        await handler.handle(event)
    """

    def __init__(
        self,
        rate: RateController,
        provider: str,
        policy: dict[BackpressureLevel, float] | dict[str, float] | None = None,
    ) -> None:
        """
        Initialize feedback handler.
        
        Args:
            rate: RateController implementing Core protocol
            provider: Provider name (e.g., "ibkr", "polygon")
            policy: Optional custom scale policy mapping BackpressureLevel → scale factor.
                   Also accepts legacy string keys for backward compatibility.
        """
        self.rate_controller = rate
        self.provider = provider
        
        # Normalize policy to use BackpressureLevel enum keys
        if policy is None:
            self.policy: dict[BackpressureLevel, float] = {
                BackpressureLevel.ok: 1.0,
                BackpressureLevel.soft: 0.5,
                BackpressureLevel.hard: 0.0,
            }
        elif all(isinstance(k, BackpressureLevel) for k in policy.keys()):
            self.policy = dict(policy)  # Already enum-based
        else:
            # Convert string keys to enum for backward compatibility
            self.policy = {
                BackpressureLevel[k]: v for k, v in policy.items()
            }
        
        # Optional metrics
        try:
            from prometheus_client import Counter
            self._metric_events = Counter(
                "feedback_events_processed_total",
                "Feedback events processed",
                ["provider", "level"]
            )
            self._metrics_available = True
        except Exception:  # pragma: no cover
            self._metric_events = None
            self._metrics_available = False
    
    def _to_adjustment(self, event: FeedbackEvent) -> RateAdjustment:
        """
        Convert Core FeedbackEvent to RateAdjustment DTO.
        
        Applies policy mapping from BackpressureLevel to scale factor.
        
        Args:
            event: Core FeedbackEvent DTO from store
            
        Returns:
            RateAdjustment DTO with provider, scale, reason, ts
        """
        scale = self.policy.get(event.level, 1.0)
        
        return RateAdjustment(
            provider=self.provider,
            scale=scale,
            reason=event.level,
            ts=event.ts,
        )

    async def handle(self, event: FeedbackEvent) -> None:
        """
        Handle a feedback event from the store.
        
        Phase 8.0: Now accepts Core FeedbackEvent DTO (typed).
        
        Args:
            event: Core FeedbackEvent with coordinator_id, queue_size, capacity, level, source, ts
        """
        # Create RateAdjustment from event
        adjustment = self._to_adjustment(event)
        
        # Log feedback
        logger.debug(
            f"[feedback] provider={self.provider} level={event.level.value} "
            f"scale={adjustment.scale} queue={event.queue_size}/{event.capacity}"
        )
        
        # Phase 6.0B: Echo queue depth to pipeline metrics for KEDA
        try:
            from ...metrics import PIPELINE_FEEDBACK_QUEUE_DEPTH
            PIPELINE_FEEDBACK_QUEUE_DEPTH.labels(source="store_coordinator").set(
                float(event.queue_size)
            )
        except Exception:  # pragma: no cover
            pass  # Graceful degradation
        
        # Apply adjustment via Core protocol
        await self.rate_controller.apply(adjustment)
        
        # Update metrics (using enum value for label)
        if self._metrics_available and self._metric_events:
            self._metric_events.labels(
                provider=self.provider,
                level=event.level.value  # Use enum.value for string label
            ).inc()

