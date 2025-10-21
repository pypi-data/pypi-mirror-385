"""
Unit tests for RateCoordinator feedback capabilities (Phase 6.0A).

Tests dynamic rate adjustment and backpressure state management.
"""

import pytest

from market_data_pipeline.orchestration.coordinator import RateCoordinator
from market_data_pipeline.pacing import Budget


@pytest.mark.asyncio
async def test_set_budget_scale_adjusts_rate():
    """Test that set_budget_scale adjusts the Pacer's refill rate."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    
    # Scale to 50%
    await coord.set_budget_scale("test", 0.5)
    
    # Verify rate is now 50 tokens/sec
    assert coord._buckets["test"].budget.max_msgs_per_sec == 50
    assert coord._scale_factors["test"] == 0.5


@pytest.mark.asyncio
async def test_set_budget_scale_clamps_to_zero_one():
    """Test that scale factor is clamped to [0.0, 1.0]."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    
    # Try to set scale > 1.0
    await coord.set_budget_scale("test", 1.5)
    assert coord._scale_factors["test"] == 1.0
    assert coord._buckets["test"].budget.max_msgs_per_sec == 100
    
    # Try to set scale < 0.0
    await coord.set_budget_scale("test", -0.5)
    assert coord._scale_factors["test"] == 0.0
    # Minimum 1 token/sec
    assert coord._buckets["test"].budget.max_msgs_per_sec == 1


@pytest.mark.asyncio
async def test_set_budget_scale_preserves_capacity():
    """Test that scaling doesn't affect burst capacity."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=200, refill_rate=100)
    
    await coord.set_budget_scale("test", 0.5)
    
    # Capacity should remain unchanged
    assert coord._buckets["test"].budget.burst == 200
    # Only refill rate changes
    assert coord._buckets["test"].budget.max_msgs_per_sec == 50


@pytest.mark.asyncio
async def test_set_budget_scale_invalid_provider():
    """Test graceful handling of unregistered provider."""
    coord = RateCoordinator()
    
    # Should not raise, just log warning
    await coord.set_budget_scale("nonexistent", 0.5)
    
    # Should have no effect
    assert "nonexistent" not in coord._scale_factors


@pytest.mark.asyncio
async def test_set_budget_scale_zero():
    """Test that scale=0.0 sets minimum rate (1 token/sec)."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    
    await coord.set_budget_scale("test", 0.0)
    
    # Minimum 1 token/sec to avoid division by zero
    assert coord._buckets["test"].budget.max_msgs_per_sec == 1
    assert coord._scale_factors["test"] == 0.0


@pytest.mark.asyncio
async def test_set_budget_scale_one():
    """Test that scale=1.0 restores base rate."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    
    # Scale down then back up
    await coord.set_budget_scale("test", 0.5)
    await coord.set_budget_scale("test", 1.0)
    
    # Should be back to base rate
    assert coord._buckets["test"].budget.max_msgs_per_sec == 100
    assert coord._scale_factors["test"] == 1.0


@pytest.mark.asyncio
async def test_set_global_pressure_updates_state():
    """Test that set_global_pressure updates pressure state."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    
    await coord.set_global_pressure("test", "soft")
    
    assert coord._pressure_states["test"] == "soft"


@pytest.mark.asyncio
async def test_set_global_pressure_invalid_provider():
    """Test graceful handling of unregistered provider."""
    coord = RateCoordinator()
    
    # Should not raise, just log warning
    await coord.set_global_pressure("nonexistent", "hard")
    
    # Should have no effect
    assert "nonexistent" not in coord._pressure_states


@pytest.mark.asyncio
async def test_scale_persists_across_acquire():
    """Test that scaled rate persists during token acquisition."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    
    # Scale down to 50%
    await coord.set_budget_scale("test", 0.5)
    
    # Acquire should work with scaled rate
    await coord.acquire("test", 1)
    
    # Scale should still be 0.5
    assert coord._scale_factors["test"] == 0.5
    assert coord._buckets["test"].budget.max_msgs_per_sec == 50


@pytest.mark.asyncio
async def test_base_rate_preserved():
    """Test that base rate is preserved for re-scaling."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    
    # Multiple scale operations
    await coord.set_budget_scale("test", 0.5)
    await coord.set_budget_scale("test", 0.25)
    await coord.set_budget_scale("test", 1.0)
    
    # Should return to original base rate
    assert coord._base_rates["test"] == 100
    assert coord._buckets["test"].budget.max_msgs_per_sec == 100


@pytest.mark.asyncio
async def test_get_provider_state_includes_feedback():
    """Test that get_provider_state includes scale and pressure."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    
    await coord.set_budget_scale("test", 0.5)
    await coord.set_global_pressure("test", "soft")
    
    state = coord.get_provider_state("test")
    
    assert state["scale_factor"] == 0.5
    assert state["pressure_state"] == "soft"


@pytest.mark.asyncio
async def test_multiple_providers_independent():
    """Test that multiple providers have independent scale factors."""
    coord = RateCoordinator()
    coord.register_provider("ibkr", capacity=60, refill_rate=60)
    coord.register_provider("polygon", capacity=100, refill_rate=100)
    
    # Scale only IBKR
    await coord.set_budget_scale("ibkr", 0.5)
    
    # IBKR should be scaled
    assert coord._scale_factors["ibkr"] == 0.5
    assert coord._buckets["ibkr"].budget.max_msgs_per_sec == 30
    
    # Polygon should be unaffected
    assert coord._scale_factors["polygon"] == 1.0
    assert coord._buckets["polygon"].budget.max_msgs_per_sec == 100


@pytest.mark.asyncio
async def test_pressure_state_transitions():
    """Test that pressure state transitions are logged."""
    coord = RateCoordinator()
    coord.register_provider("test", capacity=100, refill_rate=100)
    
    # Transition through states
    await coord.set_global_pressure("test", "soft")
    assert coord._pressure_states["test"] == "soft"
    
    await coord.set_global_pressure("test", "hard")
    assert coord._pressure_states["test"] == "hard"
    
    await coord.set_global_pressure("test", "ok")
    assert coord._pressure_states["test"] == "ok"

