"""
Integration tests for Phase 8.0 backpressure feedback system.

Phase 8.0: Updated to use Core v1.1.0 DTOs and protocols.
Tests end-to-end feedback flow: FeedbackBus → FeedbackHandler → RateCoordinator
"""

import asyncio
import time

import pytest
from market_data_core.telemetry import BackpressureLevel, FeedbackEvent

from market_data_pipeline.orchestration.coordinator import RateCoordinator
from market_data_pipeline.orchestration.feedback import (
    FeedbackHandler,
    RateCoordinatorAdapter,
    feedback_bus,
    reset_feedback_bus,
)


@pytest.fixture(autouse=True)
def reset_bus():
    """Reset feedback bus before each test to ensure clean state."""
    reset_feedback_bus()
    yield
    reset_feedback_bus()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_feedback_inprocess_flow():
    """
    Test end-to-end feedback: FeedbackBus → FeedbackHandler → RateCoordinator.
    
    Phase 8.0: Now uses Core FeedbackEvent DTOs and RateCoordinatorAdapter.
    
    This simulates the flow where:
    1. WriteCoordinator detects backpressure
    2. Publishes Core FeedbackEvent to bus
    3. FeedbackHandler receives event, creates RateAdjustment
    4. RateCoordinator rate is adjusted via adapter
    """
    # Setup: Create RateCoordinator and wrap in adapter
    coord = RateCoordinator()
    coord.register_provider("ibkr", capacity=100, refill_rate=100)
    adapter = RateCoordinatorAdapter(coord)
    
    # Verify initial state
    assert coord._scale_factors["ibkr"] == 1.0
    assert coord._pressure_states["ibkr"] == "ok"
    assert coord._buckets["ibkr"].budget.max_msgs_per_sec == 100
    
    # Setup: Create FeedbackHandler and subscribe to bus
    handler = FeedbackHandler(adapter, "ibkr")
    feedback_bus().subscribe(handler.handle)
    
    # Step 1: Simulate SOFT backpressure from store (Core DTO)
    await asyncio.wait_for(
        feedback_bus().publish(
            FeedbackEvent(
                coordinator_id="store_01",
                queue_size=800,
                capacity=1000,
                level=BackpressureLevel.soft,
                source="store",
                ts=time.time()
            )
        ),
        timeout=1.0
    )
    
    # Verify: Rate was scaled to 50%
    assert coord._scale_factors["ibkr"] == 0.5
    assert coord._pressure_states["ibkr"] == "soft"
    assert coord._buckets["ibkr"].budget.max_msgs_per_sec == 50
    
    # Step 2: Simulate HARD backpressure
    await asyncio.wait_for(
        feedback_bus().publish(
            FeedbackEvent(
                coordinator_id="store_01",
                queue_size=950,
                capacity=1000,
                level=BackpressureLevel.hard,
                source="store",
                ts=time.time()
            )
        ),
        timeout=1.0
    )
    
    # Verify: Rate was scaled to minimum (1 token/sec)
    assert coord._scale_factors["ibkr"] == 0.0
    assert coord._pressure_states["ibkr"] == "hard"
    assert coord._buckets["ibkr"].budget.max_msgs_per_sec == 1
    
    # Step 3: Simulate recovery to OK
    await asyncio.wait_for(
        feedback_bus().publish(
            FeedbackEvent(
                coordinator_id="store_01",
                queue_size=100,
                capacity=1000,
                level=BackpressureLevel.ok,
                source="store",
                ts=time.time()
            )
        ),
        timeout=1.0
    )
    
    # Verify: Rate was restored to full (100 tokens/sec)
    assert coord._scale_factors["ibkr"] == 1.0
    assert coord._pressure_states["ibkr"] == "ok"
    assert coord._buckets["ibkr"].budget.max_msgs_per_sec == 100


@pytest.mark.asyncio
@pytest.mark.integration
async def test_feedback_multiple_subscribers():
    """Test that multiple handlers can subscribe to the same bus."""
    coord = RateCoordinator()
    coord.register_provider("ibkr", capacity=100, refill_rate=100)
    coord.register_provider("polygon", capacity=200, refill_rate=200)
    adapter = RateCoordinatorAdapter(coord)
    
    # Create two handlers for different providers
    handler_ibkr = FeedbackHandler(adapter, "ibkr")
    handler_polygon = FeedbackHandler(adapter, "polygon")
    
    # Subscribe both
    feedback_bus().subscribe(handler_ibkr.handle)
    feedback_bus().subscribe(handler_polygon.handle)
    
    # Publish event targeting IBKR (both will receive it, but only IBKR will process)
    # In a real system, events would have provider filtering
    await asyncio.wait_for(
        feedback_bus().publish(FeedbackEvent(
            coordinator_id="store_01", queue_size=700, capacity=1000,
            level=BackpressureLevel.soft, source="store", ts=time.time()
        )),
        timeout=1.0
    )
    
    # Both should have received the event and adjusted their rates
    assert coord._scale_factors["ibkr"] == 0.5
    assert coord._scale_factors["polygon"] == 0.5


@pytest.mark.asyncio
@pytest.mark.integration  
async def test_feedback_with_unified_runtime():
    """
    Test that UnifiedRuntime integrates feedback correctly.
    
    This tests that:
    1. Feedback can be enabled via settings
    2. FeedbackHandler is created and subscribed
    3. Rate adjustments work end-to-end
    """
    from market_data_pipeline.runtime import UnifiedRuntime
    from market_data_pipeline.settings import UnifiedRuntimeSettings
    
    # Create settings with feedback enabled
    settings = UnifiedRuntimeSettings(
        mode="dag",
        dag={
            "graph": {
                "nodes": [
                    {"id": "test", "type": "operator.buffer", "params": {}}
                ],
                "edges": []
            }
        },
        feedback={
            "enable_feedback": True,
            "provider_name": "ibkr"
        }
    )
    
    # Create runtime with timeout
    async with asyncio.timeout(5.0):
        async with UnifiedRuntime(settings) as rt:
            # Access the DAG facade to get the rate coordinator
            dag_facade = rt._impl
            
            # Verify feedback was setup
            assert hasattr(dag_facade, "_feedback_handler")
            assert dag_facade._feedback_handler is not None
            assert hasattr(dag_facade, "_rate_coordinator")
            
            # Verify rate coordinator was initialized
            coord = dag_facade._rate_coordinator
            assert "ibkr" in coord._buckets
            assert coord._scale_factors["ibkr"] == 1.0
            
            # Simulate feedback event
            await asyncio.wait_for(
                feedback_bus().publish(FeedbackEvent(
            coordinator_id="store_01", queue_size=700, capacity=1000,
            level=BackpressureLevel.soft, source="store", ts=time.time()
        )),
                timeout=1.0
            )
            
            # Verify rate was adjusted
            assert coord._scale_factors["ibkr"] == 0.5


@pytest.mark.asyncio
@pytest.mark.integration
async def test_feedback_disabled_via_settings():
    """Test that feedback can be disabled via settings."""
    from market_data_pipeline.runtime import UnifiedRuntime
    from market_data_pipeline.settings import UnifiedRuntimeSettings
    
    # Create settings with feedback DISABLED
    settings = UnifiedRuntimeSettings(
        mode="dag",
        dag={
            "graph": {
                "nodes": [
                    {"id": "test", "type": "operator.buffer", "params": {}}
                ],
                "edges": []
            }
        },
        feedback={
            "enable_feedback": False
        }
    )
    
    # Create runtime with timeout
    async with asyncio.timeout(5.0):
        async with UnifiedRuntime(settings) as rt:
            dag_facade = rt._impl
            
            # Verify feedback was NOT setup
            assert dag_facade._feedback_handler is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_feedback_respects_custom_policy():
    """Test that custom scale policy is respected."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    adapter = RateCoordinatorAdapter(coord)
    
    # Custom policy: softer throttling
    custom_policy = {"ok": 1.0, "soft": 0.75, "hard": 0.25}
    handler = FeedbackHandler(adapter, "test", policy=custom_policy)
    feedback_bus().subscribe(handler.handle)
    
    # Send SOFT event
    await asyncio.wait_for(
        feedback_bus().publish(FeedbackEvent(
            coordinator_id="store_01", queue_size=700, capacity=1000,
            level=BackpressureLevel.soft, source="store", ts=time.time()
        )),
        timeout=1.0
    )
    
    # Should use custom scale of 0.75 instead of default 0.5
    assert coord._scale_factors["test"] == 0.75
    assert coord._buckets["test"].budget.max_msgs_per_sec == 75

