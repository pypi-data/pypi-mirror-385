"""Source capabilities and SLA definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Flag, auto
from typing import List, Optional
from datetime import datetime


class SourceCapabilities(Flag):
    """Source capability flags."""

    TRADES = auto()
    QUOTES = auto()
    BOOK = auto()
    OPTIONS = auto()
    SNAPSHOTS = auto()


@dataclass(frozen=True)
class SourceHealth:
    """Machine-parsable source health information."""

    connected: bool
    last_error_at: Optional[datetime] = None
    last_item_ts: Optional[datetime] = None
    queued_msgs: int = 0
    pacing_blocked_count: int = 0
    detail: str = ""


@dataclass(frozen=True)
class SourceSLA:
    """Source Service Level Agreement contract."""

    # Ordering guarantees
    event_time_ordered: bool = True  # Non-decreasing by event time

    # Backpressure boundaries
    max_buffer_size: int = 1000  # Maximum items to buffer
    pacing_required: bool = True  # Must respect pacing limits

    # Cancellation guarantees
    max_close_time_ms: int = 1000  # Maximum time to close

    # Telemetry requirements
    metrics_required: bool = True  # Must export standard metrics
