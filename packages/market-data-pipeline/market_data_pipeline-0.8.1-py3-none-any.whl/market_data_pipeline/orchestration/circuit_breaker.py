"""
Simple asynchronous circuit breaker utility.

Implements the circuit breaker pattern to protect against repeated provider failures.
The breaker opens after a threshold of failures and stays open for a timeout period.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

logger = logging.getLogger(__name__)


class CircuitBreakerOpen(Exception):
    """Raised when attempting to use a circuit breaker that is open."""

    pass


class CircuitBreaker:
    """Protects against repeated provider failures using circuit breaker pattern.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests are blocked
    - HALF_OPEN: Testing if service has recovered
    
    Example:
        breaker = CircuitBreaker(threshold=5, timeout=60.0)
        
        if breaker.is_open():
            raise CircuitBreakerOpen("IBKR")
        
        try:
            await ibkr.connect()
        except Exception:
            await breaker.record_failure()
            raise
    """

    def __init__(
        self,
        threshold: int = 5,
        timeout: float = 60.0,
        half_open_attempts: int = 1,
    ) -> None:
        """Initialize circuit breaker.
        
        Args:
            threshold: Number of failures before opening circuit
            timeout: Seconds to keep circuit open before attempting recovery
            half_open_attempts: Number of successful attempts needed to close circuit
        """
        self.threshold = threshold
        self.timeout = timeout
        self.half_open_attempts = half_open_attempts
        
        self.failures = 0
        self.successes = 0
        self.open_until: Optional[datetime] = None
        self._lock = asyncio.Lock()

    def is_open(self) -> bool:
        """Check if circuit is currently open.
        
        Returns:
            True if circuit is open and blocking requests
        """
        if self.open_until is None:
            return False
        
        now = datetime.now(timezone.utc)
        if now >= self.open_until:
            # Timeout expired, enter half-open state
            logger.info("Circuit breaker timeout expired, entering half-open state")
            self.open_until = None
            self.failures = 0
            return False
        
        return True

    async def record_failure(self) -> None:
        """Record a failure and potentially open the circuit.
        
        If failures exceed threshold, circuit opens for timeout period.
        """
        async with self._lock:
            self.failures += 1
            self.successes = 0  # Reset success counter
            
            if self.failures >= self.threshold:
                self.open_until = datetime.now(timezone.utc) + timedelta(
                    seconds=self.timeout
                )
                logger.warning(
                    "Circuit breaker opened after %d failures. "
                    "Will retry after %s seconds",
                    self.failures,
                    self.timeout,
                )
                self.failures = 0  # Reset for next cycle

    async def record_success(self) -> None:
        """Record a successful operation.
        
        In half-open state, multiple successes close the circuit.
        """
        async with self._lock:
            self.successes += 1
            self.failures = 0  # Reset failure counter
            
            # If we were half-open and got enough successes, fully close
            if (
                self.open_until is None
                and self.successes >= self.half_open_attempts
            ):
                logger.info(
                    "Circuit breaker closed after %d successful attempts",
                    self.successes,
                )
                self.successes = 0

    async def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        async with self._lock:
            self.failures = 0
            self.successes = 0
            self.open_until = None
            logger.info("Circuit breaker manually reset")

    def get_state(self) -> str:
        """Get current circuit state.
        
        Returns:
            "closed", "open", or "half_open"
        """
        if self.open_until is None:
            return "closed"
        elif self.is_open():
            return "open"
        else:
            return "half_open"

