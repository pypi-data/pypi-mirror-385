"""Unit tests for CircuitBreaker."""

import asyncio

import pytest

from market_data_pipeline.orchestration.circuit_breaker import CircuitBreaker


class TestCircuitBreaker:
    """Test CircuitBreaker functionality."""

    @pytest.mark.asyncio
    async def test_initial_state_closed(self):
        """Test circuit breaker starts in closed state."""
        breaker = CircuitBreaker(threshold=3, timeout=1.0)
        
        assert not breaker.is_open()
        assert breaker.get_state() == "closed"

    @pytest.mark.asyncio
    async def test_opens_after_threshold(self):
        """Test circuit opens after threshold failures."""
        breaker = CircuitBreaker(threshold=3, timeout=1.0)
        
        # Record failures
        await breaker.record_failure()
        assert not breaker.is_open()
        
        await breaker.record_failure()
        assert not breaker.is_open()
        
        await breaker.record_failure()
        # Should now be open
        assert breaker.is_open()
        assert breaker.get_state() == "open"

    @pytest.mark.asyncio
    async def test_closes_after_timeout(self):
        """Test circuit closes after timeout."""
        breaker = CircuitBreaker(threshold=2, timeout=0.1)  # Short timeout for test
        
        # Open the circuit
        await breaker.record_failure()
        await breaker.record_failure()
        assert breaker.is_open()
        
        # Wait for timeout
        await asyncio.sleep(0.15)
        
        # Should be closed now
        assert not breaker.is_open()

    @pytest.mark.asyncio
    async def test_reset(self):
        """Test manual reset."""
        breaker = CircuitBreaker(threshold=2, timeout=10.0)
        
        # Open the circuit
        await breaker.record_failure()
        await breaker.record_failure()
        assert breaker.is_open()
        
        # Reset
        await breaker.reset()
        
        # Should be closed
        assert not breaker.is_open()
        assert breaker.get_state() == "closed"

    @pytest.mark.asyncio
    async def test_success_resets_failures(self):
        """Test that success resets failure counter."""
        breaker = CircuitBreaker(threshold=3, timeout=1.0)
        
        # Record some failures
        await breaker.record_failure()
        await breaker.record_failure()
        assert not breaker.is_open()
        
        # Record success
        await breaker.record_success()
        
        # Circuit should still be closed and failures reset
        # Need 3 more failures to open
        await breaker.record_failure()
        await breaker.record_failure()
        assert not breaker.is_open()
        
        await breaker.record_failure()
        assert breaker.is_open()

