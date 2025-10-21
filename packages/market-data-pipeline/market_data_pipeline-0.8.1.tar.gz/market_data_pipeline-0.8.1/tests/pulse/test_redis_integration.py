"""Integration tests for Pulse (redis backend) — skipped if Redis unavailable."""

import asyncio
import os
import time

import pytest
from market_data_core.events import create_event_bus
from market_data_core.events.envelope import EventEnvelope, EventMeta
from market_data_core.protocols import RateController
from market_data_core.telemetry import BackpressureLevel, FeedbackEvent, RateAdjustment

from market_data_pipeline.pulse import FeedbackConsumer, PulseConfig
from market_data_pipeline.settings.feedback import PipelineFeedbackSettings


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_AVAILABLE = os.getenv("EVENT_BUS_BACKEND") == "redis"


class MockRateController(RateController):
    """Mock rate controller."""
    
    def __init__(self) -> None:
        self.adjustments: list[RateAdjustment] = []
    
    async def apply(self, adjustment: RateAdjustment) -> None:
        self.adjustments.append(adjustment)


@pytest.mark.skipif(not REDIS_AVAILABLE, reason="Redis not available (set EVENT_BUS_BACKEND=redis)")
@pytest.mark.asyncio
async def test_redis_feedback_flow() -> None:
    """Test full feedback flow with Redis backend."""
    # Setup
    cfg = PulseConfig.__new__(
        PulseConfig,
        enabled=True,
        backend="redis",
        redis_url=REDIS_URL,
        ns="test_redis",
        track="v1",
        publisher_token="unset",
    )
    settings = PipelineFeedbackSettings(provider_name="test", scale_soft=0.7)
    rate_controller = MockRateController()
    
    consumer = FeedbackConsumer(rate_controller, settings, cfg)
    bus = create_event_bus(backend="redis", redis_url=REDIS_URL)
    
    stream = f"{cfg.ns}.telemetry.feedback"
    
    # Publish event (bus will wrap in envelope)
    event = FeedbackEvent(
        coordinator_id="redis_test",
        queue_size=80,
        capacity=100,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time(),
    )
    await bus.publish(stream, event, key="redis_test")
    
    # Start consumer
    task = asyncio.create_task(consumer.run("test_redis_consumer"))
    await asyncio.sleep(0.5)  # Let it process
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # Assert
    assert len(rate_controller.adjustments) >= 1
    assert rate_controller.adjustments[0].scale == 0.7

