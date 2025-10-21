"""
Protocol conformance tests for Phase 8.0 Core v1.1.0 integration.

Verifies that Pipeline implementations conform to Core protocols and contracts.
"""

import time

import pytest
from market_data_core.protocols import FeedbackPublisher, RateController
from market_data_core.telemetry import (
    BackpressureLevel,
    FeedbackEvent,
    RateAdjustment,
)

from market_data_pipeline.orchestration.coordinator import RateCoordinator
from market_data_pipeline.orchestration.feedback import (
    FeedbackBus,
    FeedbackHandler,
    RateCoordinatorAdapter,
)


@pytest.mark.integration
def test_rate_coordinator_adapter_implements_protocol():
    """Test that RateCoordinatorAdapter conforms to Core RateController protocol."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    adapter = RateCoordinatorAdapter(coord)
    
    # Protocol conformance check
    assert isinstance(adapter, RateController)


@pytest.mark.integration
def test_feedback_bus_implements_protocol():
    """Test that FeedbackBus conforms to Core FeedbackPublisher protocol."""
    bus = FeedbackBus()
    
    # Protocol conformance check
    assert isinstance(bus, FeedbackPublisher)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_rate_controller_apply_signature():
    """Test that RateController.apply() has correct signature and behavior."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    adapter = RateCoordinatorAdapter(coord)
    
    # Create Core RateAdjustment
    adjustment = RateAdjustment(
        provider="test",
        scale=0.5,
        reason=BackpressureLevel.soft,
        ts=time.time()
    )
    
    # apply() should accept RateAdjustment and return None
    result = await adapter.apply(adjustment)
    assert result is None
    
    # Verify adjustment was applied
    assert coord._scale_factors["test"] == 0.5


@pytest.mark.asyncio
@pytest.mark.integration
async def test_feedback_publisher_publish_signature():
    """Test that FeedbackPublisher.publish() has correct signature and behavior."""
    bus = FeedbackBus()
    published_events = []
    
    # Subscribe a handler that records events
    async def record_event(event: FeedbackEvent) -> None:
        published_events.append(event)
    
    bus.subscribe(record_event)
    
    # Create Core FeedbackEvent
    event = FeedbackEvent(
        coordinator_id="test_coord",
        queue_size=500,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    
    # publish() should accept FeedbackEvent and return None
    result = await bus.publish(event)
    assert result is None
    
    # Verify event was delivered
    assert len(published_events) == 1
    assert published_events[0] is event


@pytest.mark.asyncio
@pytest.mark.integration
async def test_feedback_event_to_rate_adjustment_roundtrip():
    """Test Core DTO roundtrip: FeedbackEvent → RateAdjustment."""
    handler = FeedbackHandler(
        rate=RateCoordinatorAdapter(RateCoordinator()),
        provider="test"
    )
    
    # Create FeedbackEvent
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=800,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    
    # Convert to RateAdjustment
    adjustment = handler._to_adjustment(event)
    
    # Verify DTO structure
    assert isinstance(adjustment, RateAdjustment)
    assert adjustment.provider == "test"
    assert adjustment.scale == 0.5  # Default policy for soft
    assert adjustment.reason == BackpressureLevel.soft
    assert adjustment.ts == event.ts


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("level,expected_scale", [
    (BackpressureLevel.ok, 1.0),
    (BackpressureLevel.soft, 0.5),
    (BackpressureLevel.hard, 0.0),
])
async def test_feedback_handler_level_to_scale_mapping(level, expected_scale):
    """
    Test that FeedbackHandler correctly maps BackpressureLevel to scale factors.
    
    Parametrized test as specified by expert guidance.
    """
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    adapter = RateCoordinatorAdapter(coord)
    handler = FeedbackHandler(adapter, "test")
    
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=500,
        capacity=1000,
        level=level,
        source="store",
        ts=time.time()
    )
    
    await handler.handle(event)
    
    # Verify scale mapping
    assert coord._scale_factors["test"] == expected_scale


@pytest.mark.asyncio
@pytest.mark.integration
async def test_concurrent_feedback_publish():
    """
    Test concurrent publish operations on FeedbackBus.
    
    As specified by expert guidance: test with 10 concurrent tasks.
    """
    bus = FeedbackBus()
    received_events = []
    
    async def collect_event(event: FeedbackEvent) -> None:
        received_events.append(event)
    
    bus.subscribe(collect_event)
    
    # Create 10 concurrent publish tasks
    tasks = []
    for i in range(10):
        event = FeedbackEvent(
            coordinator_id=f"coord_{i}",
            queue_size=i * 100,
            capacity=1000,
            level=BackpressureLevel.soft,
            source="store",
            ts=time.time()
        )
        tasks.append(bus.publish(event))
    
    # Execute concurrently
    import asyncio
    await asyncio.gather(*tasks)
    
    # Verify all events received
    assert len(received_events) == 10
    
    # Verify event ordering/uniqueness
    coordinator_ids = {e.coordinator_id for e in received_events}
    assert len(coordinator_ids) == 10  # All unique


@pytest.mark.asyncio
@pytest.mark.integration
async def test_core_dto_json_serialization():
    """Test that Core DTOs can be serialized/deserialized."""
    # Create FeedbackEvent
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=800,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    
    # Serialize to JSON
    json_data = event.model_dump_json()
    assert isinstance(json_data, str)
    assert "soft" in json_data
    
    # Deserialize back
    parsed = FeedbackEvent.model_validate_json(json_data)
    assert parsed.coordinator_id == event.coordinator_id
    assert parsed.level == event.level
    
    # Create RateAdjustment
    adjustment = RateAdjustment(
        provider="ibkr",
        scale=0.5,
        reason=BackpressureLevel.soft,
        ts=time.time()
    )
    
    # Serialize to JSON
    adj_json = adjustment.model_dump_json()
    assert isinstance(adj_json, str)
    
    # Deserialize back
    parsed_adj = RateAdjustment.model_validate_json(adj_json)
    assert parsed_adj.provider == adjustment.provider
    assert parsed_adj.scale == adjustment.scale
    assert parsed_adj.reason == adjustment.reason


@pytest.mark.integration
def test_backpressure_level_enum_values():
    """Verify BackpressureLevel enum has expected values."""
    assert BackpressureLevel.ok.value == "ok"
    assert BackpressureLevel.soft.value == "soft"
    assert BackpressureLevel.hard.value == "hard"
    
    # Test all enum members
    all_levels = list(BackpressureLevel)
    assert len(all_levels) == 3
    assert BackpressureLevel.ok in all_levels
    assert BackpressureLevel.soft in all_levels
    assert BackpressureLevel.hard in all_levels


@pytest.mark.integration
def test_core_dto_field_validation():
    """Test that Core DTOs validate field constraints."""
    # Valid FeedbackEvent
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=500,
        capacity=1000,
        level=BackpressureLevel.ok,
        source="store",
        ts=time.time()
    )
    assert event.queue_size == 500
    
    # Valid RateAdjustment
    adjustment = RateAdjustment(
        provider="ibkr",
        scale=0.5,
        reason=BackpressureLevel.soft,
        ts=time.time()
    )
    assert adjustment.scale == 0.5
    
    # Test that DTOs are Pydantic models
    assert hasattr(event, 'model_dump')
    assert hasattr(adjustment, 'model_validate')

