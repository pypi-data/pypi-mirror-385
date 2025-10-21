"""Source telemetry and metrics."""

from __future__ import annotations

import time
from typing import Optional
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry


class SourceTelemetry:
    """Uniform telemetry for all sources."""

    def __init__(self, registry: Optional[CollectorRegistry] = None) -> None:
        """Initialize source telemetry."""
        self.registry = registry or CollectorRegistry()

        # Core metrics
        self.items_total = Counter(
            "mdp_source_items_total",
            "Total items emitted by source",
            ["source", "tenant", "symbol"],
            registry=self.registry,
        )

        self.disconnects_total = Counter(
            "mdp_source_disconnects_total",
            "Total disconnections from source",
            ["source"],
            registry=self.registry,
        )

        self.reconnects_total = Counter(
            "mdp_source_reconnects_total",
            "Total reconnections to source",
            ["source"],
            registry=self.registry,
        )

        self.pacing_blocked_total = Counter(
            "mdp_source_pacing_blocked_total",
            "Total time spent blocked by pacing",
            ["source"],
            registry=self.registry,
        )

        self.loop_duration = Histogram(
            "mdp_source_loop_seconds",
            "Source iteration loop duration",
            ["source"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
            registry=self.registry,
        )

        self.lag_seconds = Gauge(
            "mdp_source_lag_seconds",
            "Time since last item (staleness)",
            ["source", "symbol"],
            registry=self.registry,
        )

        self.status = Gauge(
            "mdp_source_status",
            "Source connection status (1=connected, 0=disconnected)",
            ["source"],
            registry=self.registry,
        )

    def record_item(self, source: str, tenant: str, symbol: str) -> None:
        """Record an item emitted by source."""
        self.items_total.labels(source=source, tenant=tenant, symbol=symbol).inc()

    def record_disconnect(self, source: str) -> None:
        """Record a disconnection."""
        self.disconnects_total.labels(source=source).inc()

    def record_reconnect(self, source: str) -> None:
        """Record a reconnection."""
        self.reconnects_total.labels(source=source).inc()

    def record_pacing_blocked(self, source: str, blocked_time: float) -> None:
        """Record time spent blocked by pacing."""
        self.pacing_blocked_total.labels(source=source).inc(blocked_time)

    def record_loop_duration(self, source: str, duration: float) -> None:
        """Record loop iteration duration."""
        self.loop_duration.labels(source=source).observe(duration)

    def set_lag(self, source: str, symbol: str, lag_seconds: float) -> None:
        """Set lag for source/symbol."""
        self.lag_seconds.labels(source=source, symbol=symbol).set(lag_seconds)

    def set_status(self, source: str, connected: bool) -> None:
        """Set source connection status."""
        self.status.labels(source=source).set(1 if connected else 0)


# Global telemetry instance
_telemetry: Optional[SourceTelemetry] = None


def get_source_telemetry() -> SourceTelemetry:
    """Get the global source telemetry instance."""
    global _telemetry
    if _telemetry is None:
        _telemetry = SourceTelemetry()
    return _telemetry


def set_source_telemetry(telemetry: SourceTelemetry) -> None:
    """Set the global source telemetry instance."""
    global _telemetry
    _telemetry = telemetry
