"""
Contract test: FeedbackEvent ↔ RateAdjustment flow.

Tests the core data flow: FeedbackEvent from Store is transformed
into RateAdjustment for rate control. This validates DTO structure
and transformation logic.
"""

import time

import pytest
from market_data_core.telemetry import (
    BackpressureLevel,
    FeedbackEvent,
    RateAdjustment,
)


def to_rate_adjustment(evt: FeedbackEvent) -> RateAdjustment:
    """
    Convert FeedbackEvent to RateAdjustment.
    
    This is the core transformation policy:
    - ok → scale 1.0 (no throttling)
    - soft → scale 0.7 (30% throttle)
    - hard → scale 0.0 (full stop)
    """
    policy = {
        "ok": 1.0,
        "soft": 0.7,
        "hard": 0.0,
    }
    scale = policy[evt.level.value]
    return RateAdjustment(
        provider="test",
        scale=scale,
        reason=evt.level,
        ts=evt.ts,
    )


def test_feedback_event_roundtrip_and_transform():
    """
    Test FeedbackEvent → JSON → FeedbackEvent → RateAdjustment.
    
    This validates:
    1. FeedbackEvent can be created with Core v1.1.0 fields
    2. JSON serialization/deserialization works
    3. Transformation to RateAdjustment preserves data
    4. Scale mapping is correct
    """
    # Create FeedbackEvent
    evt = FeedbackEvent(
        coordinator_id="q",
        queue_size=70,
        capacity=100,
        level=BackpressureLevel.soft,
        ts=time.time(),
        source="store",
    )
    
    # Core JSON roundtrip (downstream sanity check)
    packed = evt.model_dump_json()
    restored = FeedbackEvent.model_validate_json(packed)
    assert restored.level == BackpressureLevel.soft
    assert restored.queue_size == 70
    
    # Transform to RateAdjustment
    adj = to_rate_adjustment(restored)
    assert 0.0 <= adj.scale <= 1.0
    assert adj.scale == 0.7  # soft → 0.7
    assert adj.reason == BackpressureLevel.soft
    assert adj.ts == evt.ts


@pytest.mark.parametrize("level,expected_scale", [
    (BackpressureLevel.ok, 1.0),
    (BackpressureLevel.soft, 0.7),
    (BackpressureLevel.hard, 0.0),
])
def test_level_to_scale_mapping(level, expected_scale):
    """
    Test backpressure level → scale factor mapping.
    
    This is the contract between Store feedback and Pipeline throttling.
    """
    evt = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=500,
        capacity=1000,
        level=level,
        source="store",
        ts=time.time(),
    )
    
    adj = to_rate_adjustment(evt)
    assert adj.scale == expected_scale


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

