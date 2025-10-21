"""Sink capabilities and SLA definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Flag, auto
from typing import Optional
from datetime import datetime


class SinkCapabilities(Flag):
    """Sink capability flags."""

    BATCH_WRITES = auto()
    TRANSACTIONS = auto()
    EXACTLY_ONCE = auto()
    COMPRESSION = auto()
    SCHEMA_REGISTRY = auto()


@dataclass(frozen=True)
class SinkHealth:
    """Machine-parsable sink health information."""

    connected: bool
    queue_depth: int = 0
    in_flight_batches: int = 0
    last_commit_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    retry_count: int = 0
    detail: str = ""


@dataclass(frozen=True)
class SinkSLA:
    """Sink Service Level Agreement contract."""

    # Ordering guarantees
    batch_ordering: bool = True  # Single write(batch) persisted in-order
    cross_batch_ordering: bool = False  # Cross-batch ordering is best-effort

    # Delivery guarantees
    at_least_once: bool = True  # Retries may happen, downstream must be idempotent

    # Memory bounds
    bounded_memory: bool = True  # Must expose bounded buffer or backpressure

    # Lifecycle guarantees
    graceful_drain: bool = True  # close() drains in-flight work
    max_drain_time_ms: int = 5000  # Maximum time to drain

    # Observability requirements
    metrics_required: bool = True  # Must export standard metrics
