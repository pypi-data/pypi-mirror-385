"""
RateCoordinator — global pacing and circuit-breaker integration.

Phase 8.0: Updated to use Core v1.1.0 BackpressureLevel enum.

Coordinates rate limits across multiple providers and pipelines,
ensuring global budget constraints are respected.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Optional, Union

from market_data_core.telemetry import BackpressureLevel

from ..pacing import Budget, Pacer
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpen

logger = logging.getLogger(__name__)


class CooldownManager:
    """Manages cooldown periods for providers.
    
    When a provider triggers a cooldown (e.g., IBKR pacing error 162/420),
    this manager tracks the cooldown state across all pipelines.
    """

    def __init__(self, cooldown_sec: int = 600) -> None:
        """Initialize cooldown manager.
        
        Args:
            cooldown_sec: Default cooldown period in seconds
        """
        self.cooldown_sec = cooldown_sec
        self._cooldowns: Dict[str, asyncio.Event] = {}
        self._lock = asyncio.Lock()

    async def trigger_cooldown(self, scope: str, duration_sec: Optional[int] = None) -> None:
        """Trigger a cooldown period for a scope.
        
        Args:
            scope: Cooldown scope (e.g., "ibkr:market_data", "ibkr:historical")
            duration_sec: Override default cooldown duration
        """
        async with self._lock:
            event = asyncio.Event()
            self._cooldowns[scope] = event
            
        duration = duration_sec or self.cooldown_sec
        logger.warning("Cooldown triggered for %s: %d seconds", scope, duration)
        
        # Schedule cooldown expiration
        await asyncio.sleep(duration)
        
        async with self._lock:
            if scope in self._cooldowns:
                del self._cooldowns[scope]
                logger.info("Cooldown expired for %s", scope)

    def is_cooling_down(self, scope: str) -> bool:
        """Check if a scope is currently in cooldown.
        
        Args:
            scope: Cooldown scope
            
        Returns:
            True if scope is in cooldown
        """
        return scope in self._cooldowns


class RateCoordinator:
    """Coordinates global rate limits across all providers.
    
    This coordinator ensures that multiple concurrent pipelines respect
    shared rate limits and circuit breakers for each provider.
    
    Example:
        coordinator = RateCoordinator()
        coordinator.register_provider("ibkr", capacity=60, refill_rate=1.0)
        
        # In each pipeline:
        await coordinator.acquire("ibkr")  # Blocks until token available
        
        # On error:
        await coordinator.record_failure("ibkr")
        await coordinator.trigger_cooldown("ibkr", "market_data")
    """

    def __init__(self) -> None:
        """Initialize rate coordinator with empty registries."""
        self._buckets: Dict[str, Pacer] = {}
        self._cooldowns: Dict[str, CooldownManager] = {}
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        
        # Phase 6.0A: Dynamic rate adjustment support
        self._base_rates: Dict[str, int] = {}  # Original refill rates
        self._scale_factors: Dict[str, float] = {}  # Current scale (0.0-1.0)
        self._pressure_states: Dict[str, str] = {}  # ok/soft/hard
        
        # Phase 6.0B: Use global KEDA metrics (graceful degradation built into metrics.py)
        try:
            from ..metrics import (
                PIPELINE_RATE_SCALE_FACTOR,
                PIPELINE_BACKPRESSURE_STATE,
            )
            self._metric_scale = PIPELINE_RATE_SCALE_FACTOR
            self._metric_pressure = PIPELINE_BACKPRESSURE_STATE
            self._metrics_available = True
        except Exception:  # pragma: no cover
            self._metric_scale = None
            self._metric_pressure = None
            self._metrics_available = False

    def register_provider(
        self,
        name: str,
        capacity: int = 60,
        refill_rate: int = 60,
        cooldown_sec: int = 600,
        breaker_threshold: int = 5,
        breaker_timeout: float = 60.0,
    ) -> None:
        """Register a provider with rate limiting and circuit breaker.
        
        Args:
            name: Provider identifier (e.g., "ibkr", "polygon")
            capacity: Token bucket capacity (burst size)
            refill_rate: Tokens per second refill rate
            cooldown_sec: Default cooldown duration for pacing errors
            breaker_threshold: Failures before circuit opens
            breaker_timeout: Seconds to keep circuit open
        """
        logger.info("Registering rate controls for provider: %s", name)
        
        # Create shared token bucket using existing Pacer
        budget = Budget(max_msgs_per_sec=refill_rate, burst=capacity)
        self._buckets[name] = Pacer(budget)
        
        # Phase 6.0A: Store base rate for dynamic adjustment
        self._base_rates[name] = refill_rate
        self._scale_factors[name] = 1.0  # Start at full rate
        self._pressure_states[name] = "ok"  # Start with no backpressure
        
        # Create cooldown manager
        self._cooldowns[name] = CooldownManager(cooldown_sec)
        
        # Create circuit breaker
        self._breakers[name] = CircuitBreaker(
            threshold=breaker_threshold,
            timeout=breaker_timeout,
        )
        
        # Create lock for this provider
        self._locks[name] = asyncio.Lock()
        
        # Initialize metrics
        if self._metrics_available:
            self._metric_scale.labels(provider=name).set(1.0)
            self._metric_pressure.labels(provider=name).set(0)  # 0 = ok

    async def acquire(self, provider: str, n: int = 1) -> None:
        """Acquire pacing tokens for a provider.
        
        This blocks until tokens are available and circuit breaker allows.
        
        Args:
            provider: Provider identifier
            n: Number of tokens to acquire
            
        Raises:
            CircuitBreakerOpen: If circuit breaker is open
            ValueError: If provider not registered
        """
        if provider not in self._buckets:
            raise ValueError(f"Provider {provider} not registered")
        
        # Check circuit breaker
        breaker = self._breakers.get(provider)
        if breaker and breaker.is_open():
            raise CircuitBreakerOpen(f"Circuit open for provider {provider}")
        
        # Check cooldown
        cooldown = self._cooldowns.get(provider)
        if cooldown and cooldown.is_cooling_down(f"{provider}:global"):
            logger.debug("Provider %s is in cooldown, blocking...", provider)
            # Could wait for cooldown to expire or raise immediately
            raise RuntimeError(f"Provider {provider} is in cooldown")
        
        # Acquire from token bucket
        bucket = self._buckets[provider]
        await bucket.allow(n)

    async def trigger_cooldown(
        self,
        provider: str,
        scope: str,
        duration_sec: Optional[int] = None,
    ) -> None:
        """Trigger a cooldown period for a provider scope.
        
        Args:
            provider: Provider identifier
            scope: Cooldown scope (e.g., "market_data", "historical")
            duration_sec: Override default cooldown duration
        """
        if provider not in self._cooldowns:
            logger.warning("Provider %s not registered, ignoring cooldown", provider)
            return
        
        cooldown_key = f"{provider}:{scope}"
        await self._cooldowns[provider].trigger_cooldown(cooldown_key, duration_sec)

    async def record_failure(self, provider: str) -> None:
        """Record a failure for circuit breaker tracking.
        
        Args:
            provider: Provider identifier
        """
        if provider not in self._breakers:
            logger.warning("Provider %s not registered, ignoring failure", provider)
            return
        
        await self._breakers[provider].record_failure()

    async def record_success(self, provider: str) -> None:
        """Record a successful operation.
        
        Args:
            provider: Provider identifier
        """
        if provider not in self._breakers:
            return
        
        await self._breakers[provider].record_success()

    def get_provider_state(self, provider: str) -> Dict[str, any]:
        """Get current state of a provider's rate controls.
        
        Args:
            provider: Provider identifier
            
        Returns:
            Dictionary with state information
        """
        if provider not in self._buckets:
            return {"error": "Provider not registered"}
        
        breaker = self._breakers.get(provider)
        return {
            "provider": provider,
            "circuit_state": breaker.get_state() if breaker else "unknown",
            "in_cooldown": (
                self._cooldowns[provider].is_cooling_down(f"{provider}:global")
                if provider in self._cooldowns
                else False
            ),
            "scale_factor": self._scale_factors.get(provider, 1.0),
            "pressure_state": self._pressure_states.get(provider, "ok"),
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Phase 6.0A: Dynamic Rate Adjustment API
    # ──────────────────────────────────────────────────────────────────────────

    async def set_budget_scale(self, provider: str, scale: float) -> None:
        """Adjust provider's refill rate by scale factor.
        
        This method allows dynamic rate adjustment in response to backpressure
        feedback from downstream components (e.g., WriteCoordinator).
        
        Args:
            provider: Provider identifier
            scale: Scale factor (0.0-1.0) where:
                   1.0 = full rate (no backpressure)
                   0.5 = half rate (soft backpressure)
                   0.0 = paused (hard backpressure)
        
        Example:
            # Reduce rate to 50% in response to SOFT backpressure
            await coordinator.set_budget_scale("ibkr", 0.5)
        """
        if provider not in self._buckets:
            logger.warning("Provider %s not registered, ignoring scale adjustment", provider)
            return
        
        # Clamp scale to [0.0, 1.0]
        scale = max(0.0, min(1.0, scale))
        
        base_rate = self._base_rates[provider]
        new_rate = max(1, int(base_rate * scale))  # Ensure at least 1 token/sec
        
        # Update Pacer's budget dynamically
        async with self._locks[provider]:
            bucket = self._buckets[provider]
            old_rate = bucket.budget.max_msgs_per_sec
            bucket.budget = Budget(
                max_msgs_per_sec=new_rate,
                burst=bucket.budget.burst
            )
            self._scale_factors[provider] = scale
        
        logger.info(
            "Scaled %s rate: %d → %d tokens/sec (scale=%.2f, base=%d)",
            provider, old_rate, new_rate, scale, base_rate
        )
        
        # Update metrics
        if self._metrics_available and self._metric_scale:
            self._metric_scale.labels(provider=provider).set(scale)

    async def set_global_pressure(self, provider: str, level: Union[BackpressureLevel, str]) -> None:
        """Set backpressure state for a provider.
        
        Phase 8.0: Now accepts Core BackpressureLevel enum (backward compatible with strings).
        
        This is primarily for logging and metrics. The actual rate adjustment
        is done via set_budget_scale().
        
        Args:
            provider: Provider identifier
            level: Core BackpressureLevel enum or legacy string ("ok", "soft", "hard")
        
        Example:
            from market_data_core.telemetry import BackpressureLevel
            await coordinator.set_global_pressure("ibkr", BackpressureLevel.soft)
            
            # Legacy string also supported:
            await coordinator.set_global_pressure("ibkr", "soft")
        """
        if provider not in self._buckets:
            logger.warning("Provider %s not registered, ignoring pressure state", provider)
            return
        
        # Normalize to BackpressureLevel enum
        if isinstance(level, str):
            level_enum = BackpressureLevel[level]
        else:
            level_enum = level
        
        # Store as string for backward compatibility with existing code
        level_str = level_enum.value
        old_level = self._pressure_states.get(provider, "ok")
        self._pressure_states[provider] = level_str
        
        if old_level != level_str:
            logger.info("Provider %s backpressure: %s → %s", provider, old_level, level_str)
        
        # Update metrics using enum mapping (0=ok, 1=soft, 2=hard)
        if self._metrics_available and self._metric_pressure:
            level_map = {
                BackpressureLevel.ok: 0,
                BackpressureLevel.soft: 1,
                BackpressureLevel.hard: 2,
            }
            self._metric_pressure.labels(provider=provider).set(level_map[level_enum])

