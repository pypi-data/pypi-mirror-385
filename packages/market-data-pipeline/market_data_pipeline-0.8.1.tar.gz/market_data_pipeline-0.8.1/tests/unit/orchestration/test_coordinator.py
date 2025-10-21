"""Unit tests for RateCoordinator."""

import pytest

from market_data_pipeline.orchestration.coordinator import RateCoordinator
from market_data_pipeline.orchestration.circuit_breaker import CircuitBreakerOpen


class TestRateCoordinator:
    """Test RateCoordinator functionality."""

    def test_register_provider(self):
        """Test provider registration."""
        coordinator = RateCoordinator()
        
        # Register a provider
        coordinator.register_provider(
            name="test_provider",
            capacity=60,
            refill_rate=60,
        )
        
        # Should have registered components
        assert "test_provider" in coordinator._buckets
        assert "test_provider" in coordinator._cooldowns
        assert "test_provider" in coordinator._breakers

    @pytest.mark.asyncio
    async def test_acquire_unregistered_raises(self):
        """Test acquiring from unregistered provider raises error."""
        coordinator = RateCoordinator()
        
        with pytest.raises(ValueError, match="not registered"):
            await coordinator.acquire("nonexistent")

    @pytest.mark.asyncio
    async def test_acquire_success(self):
        """Test successful token acquisition."""
        coordinator = RateCoordinator()
        coordinator.register_provider(
            name="test",
            capacity=100,
            refill_rate=100,
        )
        
        # Should succeed
        await coordinator.acquire("test")
        await coordinator.acquire("test", n=5)

    @pytest.mark.asyncio
    async def test_acquire_blocked_by_circuit_breaker(self):
        """Test acquisition blocked when circuit is open."""
        coordinator = RateCoordinator()
        coordinator.register_provider(
            name="test",
            breaker_threshold=2,
            breaker_timeout=10.0,
        )
        
        # Open the circuit
        await coordinator.record_failure("test")
        await coordinator.record_failure("test")
        
        # Acquisition should fail
        with pytest.raises(CircuitBreakerOpen):
            await coordinator.acquire("test")

    @pytest.mark.asyncio
    async def test_record_failure(self):
        """Test recording failures."""
        coordinator = RateCoordinator()
        coordinator.register_provider(
            name="test",
            breaker_threshold=3,
        )
        
        # Record failures
        await coordinator.record_failure("test")
        await coordinator.record_failure("test")
        
        # Should still work
        await coordinator.acquire("test")
        
        # One more failure opens circuit
        await coordinator.record_failure("test")
        
        with pytest.raises(CircuitBreakerOpen):
            await coordinator.acquire("test")

    @pytest.mark.asyncio
    async def test_get_provider_state(self):
        """Test getting provider state."""
        coordinator = RateCoordinator()
        coordinator.register_provider("test")
        
        state = coordinator.get_provider_state("test")
        
        assert state["provider"] == "test"
        assert "circuit_state" in state
        assert "in_cooldown" in state

    @pytest.mark.asyncio
    async def test_get_state_unregistered(self):
        """Test getting state of unregistered provider."""
        coordinator = RateCoordinator()
        
        state = coordinator.get_provider_state("nonexistent")
        assert "error" in state

