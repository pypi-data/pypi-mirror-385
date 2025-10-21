"""
Contract test: Protocol conformance.

Verifies that Pipeline implementations conform to Core protocols:
- RateController: Accepts RateAdjustment, applies throttling
- FeedbackPublisher: Publishes FeedbackEvent to subscribers

These are structural typing checks (duck typing), not runtime inheritance.
"""

import time

import pytest
from market_data_core.protocols import FeedbackPublisher, RateController
from market_data_core.telemetry import (
    BackpressureLevel,
    FeedbackEvent,
    RateAdjustment,
)


def test_protocols_conformance_smoke():
    """
    Smoke test: Verify protocol classes can be implemented.
    
    This doesn't test Pipeline's actual implementations (that's in integration tests).
    It verifies Core's protocols are structurally sound and can be implemented.
    """
    class FakeRate(RateController):
        """Minimal RateController implementation for testing."""
        async def apply(self, adj: RateAdjustment) -> None:
            pass
    
    class FakePub(FeedbackPublisher):
        """Minimal FeedbackPublisher implementation for testing."""
        async def publish(self, event: FeedbackEvent) -> None:
            pass
    
    # Protocol conformance via isinstance
    assert isinstance(FakeRate(), RateController)
    assert isinstance(FakePub(), FeedbackPublisher)


@pytest.mark.asyncio
async def test_rate_controller_signature():
    """
    Test RateController.apply() signature and contract.
    
    Core contract:
    - Method: apply(adjustment: RateAdjustment) -> None
    - Async: Yes
    - Side effects: Implementation-defined (store scale factor)
    """
    class TestRateController(RateController):
        def __init__(self):
            self.last_adjustment = None
        
        async def apply(self, adjustment: RateAdjustment) -> None:
            self.last_adjustment = adjustment
    
    controller = TestRateController()
    
    # Create RateAdjustment
    adjustment = RateAdjustment(
        provider="test",
        scale=0.5,
        reason=BackpressureLevel.soft,
        ts=time.time(),
    )
    
    # Apply should return None
    result = await controller.apply(adjustment)
    assert result is None
    
    # Verify side effect
    assert controller.last_adjustment is adjustment


@pytest.mark.asyncio
async def test_feedback_publisher_signature():
    """
    Test FeedbackPublisher.publish() signature and contract.
    
    Core contract:
    - Method: publish(event: FeedbackEvent) -> None
    - Async: Yes
    - Side effects: Implementation-defined (notify subscribers)
    """
    class TestFeedbackPublisher(FeedbackPublisher):
        def __init__(self):
            self.published_events = []
        
        async def publish(self, event: FeedbackEvent) -> None:
            self.published_events.append(event)
    
    publisher = TestFeedbackPublisher()
    
    # Create FeedbackEvent
    event = FeedbackEvent(
        coordinator_id="test_coord",
        queue_size=500,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time(),
    )
    
    # Publish should return None
    result = await publisher.publish(event)
    assert result is None
    
    # Verify side effect
    assert len(publisher.published_events) == 1
    assert publisher.published_events[0] is event


def test_feedback_event_required_fields():
    """
    Test FeedbackEvent has all required Core v1.1.0 fields.
    """
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=500,
        capacity=1000,
        level=BackpressureLevel.ok,
        source="store",
        ts=time.time(),
    )
    
    # Verify all fields accessible
    assert event.coordinator_id == "store_01"
    assert event.queue_size == 500
    assert event.capacity == 1000
    assert event.level == BackpressureLevel.ok
    assert event.source == "store"
    assert event.ts > 0


def test_rate_adjustment_required_fields():
    """
    Test RateAdjustment has all required Core v1.1.0 fields.
    """
    adjustment = RateAdjustment(
        provider="ibkr",
        scale=0.5,
        reason=BackpressureLevel.soft,
        ts=time.time(),
    )
    
    # Verify all fields accessible
    assert adjustment.provider == "ibkr"
    assert adjustment.scale == 0.5
    assert adjustment.reason == BackpressureLevel.soft
    assert adjustment.ts > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

