"""
Feedback system for backpressure coordination (Phase 8.0).

Phase 8.0: Updated to use Core v1.1.0 DTOs and protocols.

Provides a handler that translates backpressure events from downstream
components (e.g., WriteCoordinator) into rate adjustments for upstream
providers (e.g., IBKR).
"""

from .bus import FeedbackBus, feedback_bus, reset_feedback_bus
from .consumer import FeedbackHandler, RateCoordinatorAdapter

__all__ = [
    "FeedbackHandler",
    "RateCoordinatorAdapter",
    "FeedbackBus",
    "feedback_bus",
    "reset_feedback_bus",
]

