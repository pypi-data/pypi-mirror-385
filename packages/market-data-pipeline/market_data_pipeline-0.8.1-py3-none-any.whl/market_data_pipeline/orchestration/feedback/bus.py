"""
Minimal FeedbackBus interface for pipeline (Phase 8.0).

Phase 8.0: Now implements Core v1.1.0 FeedbackPublisher protocol.

This provides a simple pub-sub bus for feedback events. In production:
- If market_data_store is available, use its FeedbackBus
- Otherwise, use this standalone implementation

Usage:
    from market_data_core.telemetry import FeedbackEvent, BackpressureLevel
    
    # Subscribe to feedback
    feedback_bus().subscribe(handler.handle)
    
    # Publish feedback (from store or tests)
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=800,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    await feedback_bus().publish(event)
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from market_data_core.protocols import FeedbackPublisher
from market_data_core.telemetry import FeedbackEvent


class FeedbackBus(FeedbackPublisher):
    """
    Simple pub-sub bus for backpressure feedback events.
    
    Phase 8.0: Implements Core FeedbackPublisher protocol.
    
    This is a minimal implementation for when market_data_store's
    FeedbackBus is not available. The Core protocol ensures type safety
    and cross-repository compatibility.
    """

    def __init__(self) -> None:
        self._subscribers: list[Callable[[FeedbackEvent], Awaitable[None]]] = []

    def subscribe(self, fn: Callable[[FeedbackEvent], Awaitable[None]]) -> None:
        """
        Subscribe to feedback events.
        
        Args:
            fn: Async callable that accepts a Core FeedbackEvent DTO
        """
        self._subscribers.append(fn)

    async def publish(self, event: FeedbackEvent) -> None:
        """
        Publish a feedback event to all subscribers.
        
        Implements Core FeedbackPublisher protocol.
        
        Args:
            event: Core FeedbackEvent DTO with coordinator_id, queue_size, capacity, level, source, ts
        """
        for fn in self._subscribers:
            try:
                await fn(event)
            except Exception as e:  # pragma: no cover
                # Don't let one subscriber break others
                import logging
                logging.error(f"Feedback subscriber error: {e}")


# Global bus instance
_global_bus: FeedbackBus | None = None


def feedback_bus() -> FeedbackBus:
    """
    Get the global feedback bus.
    
    This will use market_data_store's FeedbackBus if available,
    otherwise falls back to the local implementation.
    
    Returns:
        FeedbackBus instance
    """
    global _global_bus
    
    # Try to import from store first
    try:
        from market_data_store.coordinator.feedback import feedback_bus as store_bus
        return store_bus()
    except ImportError:
        # Fall back to local implementation
        if _global_bus is None:
            _global_bus = FeedbackBus()
        return _global_bus


def reset_feedback_bus() -> None:
    """
    Reset the global feedback bus.
    
    This is primarily for testing to ensure a clean state between tests.
    """
    global _global_bus
    _global_bus = None

