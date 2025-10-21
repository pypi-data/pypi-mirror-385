"""Unit tests for Pulse feedback consumer (inmem backend)."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from market_data_core.events import create_event_bus
from market_data_core.events.envelope import EventEnvelope, EventMeta
from market_data_core.protocols import RateController
from market_data_core.telemetry import BackpressureLevel, FeedbackEvent, RateAdjustment

from market_data_pipeline.pulse import FeedbackConsumer, PulseConfig
from market_data_pipeline.settings.feedback import PipelineFeedbackSettings


class MockRateController(RateController):
    """Mock RateController for testing."""
    
    def __init__(self) -> None:
        self.adjustments: list[RateAdjustment] = []
    
    async def apply(self, adjustment: RateAdjustment) -> None:
        """Record adjustment."""
        self.adjustments.append(adjustment)


@pytest.fixture
def rate_controller() -> MockRateController:
    """Provide mock rate controller."""
    return MockRateController()


@pytest.fixture
def settings() -> PipelineFeedbackSettings:
    """Provide feedback settings."""
    return PipelineFeedbackSettings(
        provider_name="test_provider",
        scale_ok=1.0,
        scale_soft=0.5,
        scale_hard=0.0,
    )


@pytest.fixture
def pulse_config() -> PulseConfig:
    """Provide Pulse config (inmem)."""
    return PulseConfig.__new__(
        PulseConfig,
        enabled=True,
        backend="inmem",
        redis_url="",
        ns="test",
        track="v1",
        publisher_token="unset",
    )


@pytest.mark.asyncio
async def test_consumer_processes_feedback_event(
    rate_controller: MockRateController,
    settings: PipelineFeedbackSettings,
    pulse_config: PulseConfig,
) -> None:
    """Test consumer processes feedback event and applies rate adjustment."""
    # Setup
    consumer = FeedbackConsumer(rate_controller, settings, pulse_config)
    bus = consumer.bus
    stream = f"{pulse_config.ns}.telemetry.feedback"
    
    # Publish event (bus will wrap in envelope)
    event = FeedbackEvent(
        coordinator_id="test_coord",
        queue_size=70,
        capacity=100,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time(),
    )
    await bus.publish(stream, event, key="test_coord")
    
    # Start consumer (run for short time)
    task = asyncio.create_task(consumer.run("test_consumer"))
    await asyncio.sleep(0.1)  # Let it process
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # Assert
    assert len(rate_controller.adjustments) == 1
    adj = rate_controller.adjustments[0]
    assert adj.provider == "test_provider"
    assert adj.scale == 0.5  # soft → 0.5
    assert adj.reason == BackpressureLevel.soft


@pytest.mark.asyncio
async def test_consumer_idempotency(
    rate_controller: MockRateController,
    settings: PipelineFeedbackSettings,
    pulse_config: PulseConfig,
) -> None:
    """Test consumer deduplicates redelivered messages."""
    # Setup
    consumer = FeedbackConsumer(rate_controller, settings, pulse_config)
    
    # Create event with fixed ID
    event = FeedbackEvent(
        coordinator_id="test_coord",
        queue_size=70,
        capacity=100,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time(),
    )
    envelope = EventEnvelope(
        id="fixed-id-123",
        key="test_coord",
        ts=time.time(),
        meta=EventMeta(schema_id="telemetry.FeedbackEvent", track="v1", headers={}),
        payload=event,
    )
    
    # Process twice
    await consumer._handle(envelope)
    await consumer._handle(envelope)
    
    # Assert: only one adjustment (idempotency)
    assert len(rate_controller.adjustments) == 1


@pytest.mark.asyncio
async def test_consumer_different_levels(
    rate_controller: MockRateController,
    settings: PipelineFeedbackSettings,
    pulse_config: PulseConfig,
) -> None:
    """Test consumer applies correct scale for each backpressure level."""
    consumer = FeedbackConsumer(rate_controller, settings, pulse_config)
    
    levels_and_scales = [
        (BackpressureLevel.ok, 1.0),
        (BackpressureLevel.soft, 0.5),
        (BackpressureLevel.hard, 0.0),
    ]
    
    for level, expected_scale in levels_and_scales:
        event = FeedbackEvent(
            coordinator_id="test_coord",
            queue_size=70,
            capacity=100,
            level=level,
            source="store",
            ts=time.time(),
        )
        envelope = EventEnvelope(
            id=f"id-{level.value}",
            key="test_coord",
            ts=time.time(),
            meta=EventMeta(schema_id="telemetry.FeedbackEvent", track="v1", headers={}),
            payload=event,
        )
        await consumer._handle(envelope)
    
    # Assert
    assert len(rate_controller.adjustments) == 3
    for i, (_, expected_scale) in enumerate(levels_and_scales):
        assert rate_controller.adjustments[i].scale == expected_scale

