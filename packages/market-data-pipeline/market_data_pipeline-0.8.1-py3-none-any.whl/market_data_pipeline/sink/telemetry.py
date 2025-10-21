"""Sink telemetry and metrics."""

from __future__ import annotations

import time
from typing import Optional
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry


class SinkTelemetry:
    """Uniform telemetry for all sinks."""

    def __init__(self, registry: Optional[CollectorRegistry] = None) -> None:
        """Initialize sink telemetry."""
        self.registry = registry or CollectorRegistry()

        # Core metrics
        self.batches_in_total = Counter(
            "mdp_sink_batches_in_total",
            "Total batches accepted by write()",
            ["sink", "tenant", "pipeline"],
            registry=self.registry,
        )

        self.batches_committed_total = Counter(
            "mdp_sink_batches_committed_total",
            "Total successful commits",
            ["sink", "tenant", "pipeline"],
            registry=self.registry,
        )

        self.batches_failed_total = Counter(
            "mdp_sink_batches_failed_total",
            "Total failed commits",
            ["sink", "tenant", "pipeline"],
            registry=self.registry,
        )

        self.items_committed_total = Counter(
            "mdp_sink_items_committed_total",
            "Total items written",
            ["sink", "tenant", "pipeline"],
            registry=self.registry,
        )

        self.queue_depth = Gauge(
            "mdp_sink_queue_depth",
            "Current buffer size",
            ["sink", "tenant", "pipeline"],
            registry=self.registry,
        )

        self.commit_duration = Histogram(
            "mdp_sink_commit_seconds",
            "Latency histogram per-batch commit",
            ["sink", "tenant", "pipeline"],
            buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
            registry=self.registry,
        )

        self.retries_total = Counter(
            "mdp_sink_retries_total",
            "Total retry attempts",
            ["sink", "tenant", "pipeline"],
            registry=self.registry,
        )

        self.dropped_batches_total = Counter(
            "mdp_sink_dropped_batches_total",
            "Batches dropped due to backpressure",
            ["sink", "tenant", "pipeline", "reason"],
            registry=self.registry,
        )

    def record_batch_in(self, sink: str, tenant: str, pipeline: str) -> None:
        """Record a batch accepted by write()."""
        self.batches_in_total.labels(sink=sink, tenant=tenant, pipeline=pipeline).inc()

    def record_batch_committed(
        self, sink: str, tenant: str, pipeline: str, items: int = 0
    ) -> None:
        """Record a successful commit."""
        self.batches_committed_total.labels(
            sink=sink, tenant=tenant, pipeline=pipeline
        ).inc()

        if items > 0:
            self.items_committed_total.labels(
                sink=sink, tenant=tenant, pipeline=pipeline
            ).inc(items)

    def record_batch_failed(self, sink: str, tenant: str, pipeline: str) -> None:
        """Record a failed commit."""
        self.batches_failed_total.labels(
            sink=sink, tenant=tenant, pipeline=pipeline
        ).inc()

    def set_queue_depth(
        self, sink: str, tenant: str, pipeline: str, depth: int
    ) -> None:
        """Set current queue depth."""
        self.queue_depth.labels(sink=sink, tenant=tenant, pipeline=pipeline).set(depth)

    def record_commit_duration(
        self, sink: str, tenant: str, pipeline: str, duration: float
    ) -> None:
        """Record commit latency."""
        self.commit_duration.labels(
            sink=sink, tenant=tenant, pipeline=pipeline
        ).observe(duration)

    def record_retry(self, sink: str, tenant: str, pipeline: str) -> None:
        """Record a retry attempt."""
        self.retries_total.labels(sink=sink, tenant=tenant, pipeline=pipeline).inc()

    def record_dropped_batch(
        self, sink: str, tenant: str, pipeline: str, reason: str
    ) -> None:
        """Record a dropped batch."""
        self.dropped_batches_total.labels(
            sink=sink, tenant=tenant, pipeline=pipeline, reason=reason
        ).inc()


# Global telemetry instance
_telemetry: Optional[SinkTelemetry] = None


def get_sink_telemetry() -> SinkTelemetry:
    """Get the global sink telemetry instance."""
    global _telemetry
    if _telemetry is None:
        _telemetry = SinkTelemetry()
    return _telemetry


def set_sink_telemetry(telemetry: SinkTelemetry) -> None:
    """Set the global sink telemetry instance."""
    global _telemetry
    _telemetry = telemetry
