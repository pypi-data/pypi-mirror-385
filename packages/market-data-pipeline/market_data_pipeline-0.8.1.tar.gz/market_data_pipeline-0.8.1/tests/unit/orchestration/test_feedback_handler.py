"""
Unit tests for FeedbackHandler (Phase 8.0).

Phase 8.0: Updated to use Core v1.1.0 DTOs and protocols.
Tests feedback event handling and rate adjustment integration.
"""

import time

import pytest
from market_data_core.protocols import RateController
from market_data_core.telemetry import (
    BackpressureLevel,
    FeedbackEvent,
    RateAdjustment,
)

from market_data_pipeline.orchestration.feedback.consumer import (
    FeedbackHandler,
    RateCoordinatorAdapter,
)
from market_data_pipeline.settings.feedback import PipelineFeedbackSettings


# Mock RateController for testing (implements Core protocol)
class MockRateController(RateController):
    """Mock implementation of Core RateController protocol."""
    
    def __init__(self):
        self.adjustments = []
        self.last_adjustment = None
    
    async def apply(self, adjustment: RateAdjustment) -> None:
        """Record rate adjustments."""
        self.last_adjustment = adjustment
        self.adjustments.append(adjustment)


@pytest.mark.asyncio
async def test_handle_ok_sets_scale_one():
    """Test that OK backpressure sets scale to 1.0."""
    controller = MockRateController()
    handler = FeedbackHandler(controller, "ibkr")
    
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=100,
        capacity=1000,
        level=BackpressureLevel.ok,
        source="store",
        ts=time.time()
    )
    await handler.handle(event)
    
    assert controller.last_adjustment is not None
    assert controller.last_adjustment.provider == "ibkr"
    assert controller.last_adjustment.scale == 1.0
    assert controller.last_adjustment.reason == BackpressureLevel.ok


@pytest.mark.asyncio
async def test_handle_soft_sets_scale_half():
    """Test that SOFT backpressure sets scale to 0.5."""
    controller = MockRateController()
    handler = FeedbackHandler(controller, "ibkr")
    
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=800,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    await handler.handle(event)
    
    assert controller.last_adjustment is not None
    assert controller.last_adjustment.provider == "ibkr"
    assert controller.last_adjustment.scale == 0.5
    assert controller.last_adjustment.reason == BackpressureLevel.soft


@pytest.mark.asyncio
async def test_handle_hard_sets_scale_zero():
    """Test that HARD backpressure sets scale to 0.0."""
    controller = MockRateController()
    handler = FeedbackHandler(controller, "ibkr")
    
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=950,
        capacity=1000,
        level=BackpressureLevel.hard,
        source="store",
        ts=time.time()
    )
    await handler.handle(event)
    
    assert controller.last_adjustment is not None
    assert controller.last_adjustment.provider == "ibkr"
    assert controller.last_adjustment.scale == 0.0
    assert controller.last_adjustment.reason == BackpressureLevel.hard


@pytest.mark.asyncio
async def test_handle_creates_rate_adjustment():
    """Test that handler creates proper RateAdjustment DTO."""
    controller = MockRateController()
    handler = FeedbackHandler(controller, "ibkr")
    
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=600,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    await handler.handle(event)
    
    # Verify RateAdjustment was created and applied
    assert len(controller.adjustments) == 1
    adj = controller.adjustments[0]
    assert isinstance(adj, RateAdjustment)
    assert adj.provider == "ibkr"
    assert adj.scale == 0.5
    assert adj.reason == BackpressureLevel.soft


@pytest.mark.asyncio
async def test_custom_policy_enum_keys():
    """Test that custom policy with enum keys can be provided."""
    controller = MockRateController()
    custom_policy = {
        BackpressureLevel.ok: 1.0,
        BackpressureLevel.soft: 0.75,
        BackpressureLevel.hard: 0.25,
    }
    handler = FeedbackHandler(controller, "ibkr", policy=custom_policy)
    
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=700,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    await handler.handle(event)
    
    # Should use custom scale of 0.75
    assert controller.last_adjustment.scale == 0.75


@pytest.mark.asyncio
async def test_custom_policy_string_keys_legacy():
    """Test backward compatibility: custom policy with string keys still works."""
    controller = MockRateController()
    # Legacy format with string keys
    custom_policy = {"ok": 1.0, "soft": 0.75, "hard": 0.25}
    handler = FeedbackHandler(controller, "ibkr", policy=custom_policy)
    
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=700,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    await handler.handle(event)
    
    # Should convert string keys to enums and use custom scale of 0.75
    assert controller.last_adjustment.scale == 0.75


@pytest.mark.asyncio
async def test_multiple_providers_independent():
    """Test that different handlers can manage different providers."""
    controller = MockRateController()
    handler_ibkr = FeedbackHandler(controller, "ibkr")
    handler_polygon = FeedbackHandler(controller, "polygon")
    
    # Send events to different providers
    await handler_ibkr.handle(FeedbackEvent(
        coordinator_id="store_01", queue_size=600, capacity=1000,
        level=BackpressureLevel.soft, source="store", ts=time.time()
    ))
    await handler_polygon.handle(FeedbackEvent(
        coordinator_id="store_02", queue_size=950, capacity=1000,
        level=BackpressureLevel.hard, source="store", ts=time.time()
    ))
    
    # Should have called for both providers
    assert len(controller.adjustments) == 2
    assert controller.adjustments[0].provider == "ibkr"
    assert controller.adjustments[0].scale == 0.5
    assert controller.adjustments[1].provider == "polygon"
    assert controller.adjustments[1].scale == 0.0


@pytest.mark.asyncio
async def test_feedback_settings_default_policy():
    """Test that settings provide correct default policy with enum keys."""
    settings = PipelineFeedbackSettings()
    
    policy = settings.get_policy()
    
    # Phase 8.0: Policy now uses BackpressureLevel enum keys
    assert policy[BackpressureLevel.ok] == 1.0
    assert policy[BackpressureLevel.soft] == 0.5
    assert policy[BackpressureLevel.hard] == 0.0


@pytest.mark.asyncio
async def test_feedback_settings_custom_scales():
    """Test that settings can customize scale factors."""
    settings = PipelineFeedbackSettings(
        scale_ok=1.0,
        scale_soft=0.75,
        scale_hard=0.25
    )
    
    policy = settings.get_policy()
    
    # Phase 8.0: Policy now uses BackpressureLevel enum keys
    assert policy[BackpressureLevel.ok] == 1.0
    assert policy[BackpressureLevel.soft] == 0.75
    assert policy[BackpressureLevel.hard] == 0.25


@pytest.mark.asyncio
async def test_handler_with_settings():
    """Test that handler can be configured from settings."""
    settings = PipelineFeedbackSettings(
        enable_feedback=True,
        provider_name="polygon",
        scale_soft=0.75
    )
    
    controller = MockRateController()
    handler = FeedbackHandler(
        rate=controller,
        provider=settings.provider_name,
        policy=settings.get_policy()
    )
    
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=700,
        capacity=1000,
        level=BackpressureLevel.soft,
        source="store",
        ts=time.time()
    )
    await handler.handle(event)
    
    # Should use settings' custom scale
    assert controller.last_adjustment.provider == "polygon"
    assert controller.last_adjustment.scale == 0.75


@pytest.mark.asyncio
async def test_rate_adjustment_timestamp():
    """Test that RateAdjustment preserves FeedbackEvent timestamp."""
    controller = MockRateController()
    handler = FeedbackHandler(controller, "ibkr")
    
    event_ts = time.time()
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=500,
        capacity=1000,
        level=BackpressureLevel.ok,
        source="store",
        ts=event_ts
    )
    await handler.handle(event)
    
    # RateAdjustment should preserve timestamp
    assert controller.last_adjustment.ts == event_ts


@pytest.mark.asyncio
async def test_rate_adjustment_reason_matches_level():
    """Test that RateAdjustment.reason equals FeedbackEvent.level."""
    controller = MockRateController()
    handler = FeedbackHandler(controller, "ibkr")
    
    for level in [BackpressureLevel.ok, BackpressureLevel.soft, BackpressureLevel.hard]:
        event = FeedbackEvent(
            coordinator_id="store_01",
            queue_size=500,
            capacity=1000,
            level=level,
            source="store",
            ts=time.time()
        )
        await handler.handle(event)
        
        # Reason should match level
        assert controller.last_adjustment.reason == level

