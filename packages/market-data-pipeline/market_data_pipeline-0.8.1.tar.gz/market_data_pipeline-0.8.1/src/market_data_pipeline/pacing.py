"""Pacing and throttling for market data sources."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Optional

from .errors import PacingError


@dataclass(frozen=True)
class Budget:
    """Pacing budget configuration."""

    max_msgs_per_sec: int
    burst: int


class Pacer:
    """Token bucket rate limiter for pacing market data."""

    def __init__(self, budget: Budget) -> None:
        """Initialize the pacer with a budget."""
        self.budget = budget
        self.tokens = float(budget.burst)
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def allow(self, n: int = 1) -> None:
        """Check if n tokens are available and consume them."""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_update

            # Add tokens based on elapsed time
            self.tokens = min(
                self.budget.burst, self.tokens + elapsed * self.budget.max_msgs_per_sec
            )
            self.last_update = now

            # Check if we have enough tokens
            if self.tokens < n:
                # Calculate how long to wait
                deficit = n - self.tokens
                wait_time = deficit / self.budget.max_msgs_per_sec

                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # Recalculate tokens after waiting
                    now = time.time()
                    elapsed = now - self.last_update
                    self.tokens = min(
                        self.budget.burst,
                        self.tokens + elapsed * self.budget.max_msgs_per_sec,
                    )
                    self.last_update = now

                    # Check again after waiting
                    if self.tokens < n:
                        raise PacingError(f"Insufficient tokens: {self.tokens} < {n}")

            # Consume tokens
            self.tokens -= n

    async def reset(self) -> None:
        """Reset the token bucket."""
        async with self._lock:
            self.tokens = float(self.budget.burst)
            self.last_update = time.time()
