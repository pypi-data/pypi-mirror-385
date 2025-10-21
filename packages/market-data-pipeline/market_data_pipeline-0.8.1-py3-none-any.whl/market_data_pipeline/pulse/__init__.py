"""
Pulse integration for Pipeline — Phase 10.1.

Consumer of telemetry.feedback events from Store via Core event bus.
"""

from .config import PulseConfig
from .consumer import FeedbackConsumer

__all__ = ["PulseConfig", "FeedbackConsumer"]

