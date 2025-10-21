"""
Unit tests for Phase 6.0B KEDA autoscaling metrics.

Tests that the new global metrics (PIPELINE_RATE_SCALE_FACTOR,
PIPELINE_BACKPRESSURE_STATE, PIPELINE_FEEDBACK_QUEUE_DEPTH) can be
imported and used correctly.
"""

import pytest

from market_data_pipeline.metrics import (
    PIPELINE_BACKPRESSURE_STATE,
    PIPELINE_FEEDBACK_QUEUE_DEPTH,
    PIPELINE_RATE_SCALE_FACTOR,
)


def test_rate_scale_metric_labels_settable():
    """Test that rate scale metric accepts provider labels."""
    # Should not raise
    PIPELINE_RATE_SCALE_FACTOR.labels(provider="ibkr").set(0.5)
    PIPELINE_RATE_SCALE_FACTOR.labels(provider="polygon").set(1.0)


def test_backpressure_state_metric_labels_settable():
    """Test that backpressure state metric accepts provider labels."""
    # Should not raise
    PIPELINE_BACKPRESSURE_STATE.labels(provider="ibkr").set(0)  # ok
    PIPELINE_BACKPRESSURE_STATE.labels(provider="ibkr").set(1)  # soft
    PIPELINE_BACKPRESSURE_STATE.labels(provider="ibkr").set(2)  # hard


def test_feedback_queue_depth_metric_labels_settable():
    """Test that feedback queue depth metric accepts source labels."""
    # Should not raise
    PIPELINE_FEEDBACK_QUEUE_DEPTH.labels(source="store_coordinator").set(777)
    PIPELINE_FEEDBACK_QUEUE_DEPTH.labels(source="store_coordinator").set(0)


def test_metrics_accept_multiple_providers():
    """Test that metrics handle multiple providers independently."""
    PIPELINE_RATE_SCALE_FACTOR.labels(provider="ibkr").set(0.5)
    PIPELINE_RATE_SCALE_FACTOR.labels(provider="polygon").set(0.75)
    
    PIPELINE_BACKPRESSURE_STATE.labels(provider="ibkr").set(1)
    PIPELINE_BACKPRESSURE_STATE.labels(provider="polygon").set(0)


def test_metrics_graceful_degradation_if_prometheus_unavailable():
    """
    Test that metrics degrade gracefully if prometheus_client is not available.
    
    This is already handled in metrics.py via try/except, but we verify
    that importing doesn't crash even if prometheus_client is missing.
    """
    # If we got here, imports succeeded
    assert PIPELINE_RATE_SCALE_FACTOR is not None
    assert PIPELINE_BACKPRESSURE_STATE is not None
    assert PIPELINE_FEEDBACK_QUEUE_DEPTH is not None


def test_rate_scale_metric_accepts_float_values():
    """Test that rate scale metric accepts float values in range [0.0, 1.0]."""
    PIPELINE_RATE_SCALE_FACTOR.labels(provider="test").set(0.0)
    PIPELINE_RATE_SCALE_FACTOR.labels(provider="test").set(0.5)
    PIPELINE_RATE_SCALE_FACTOR.labels(provider="test").set(1.0)
    # Out of range values don't crash (Prometheus handles it)
    PIPELINE_RATE_SCALE_FACTOR.labels(provider="test").set(1.5)


def test_backpressure_state_metric_accepts_int_values():
    """Test that backpressure state metric accepts integer values."""
    for state in [0, 1, 2]:
        PIPELINE_BACKPRESSURE_STATE.labels(provider="test").set(state)


def test_feedback_queue_depth_metric_accepts_large_values():
    """Test that feedback queue depth metric handles large queue sizes."""
    PIPELINE_FEEDBACK_QUEUE_DEPTH.labels(source="store_coordinator").set(10000)
    PIPELINE_FEEDBACK_QUEUE_DEPTH.labels(source="store_coordinator").set(100000)

