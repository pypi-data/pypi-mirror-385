"""
Orchestration layer (Phase 3.0)

Provides runtime coordination across multiple market-data sources
and providers — including dynamic registry, routing, rate coordination,
circuit-breaker protection, and a unified PipelineRuntime API.

This layer is opt-in and does not break existing pipeline functionality.
"""

from .circuit_breaker import CircuitBreaker
from .coordinator import RateCoordinator
from .registry import SourceRegistry
from .router import SourceRouter
from .runtime import PipelineRuntime, PipelineRuntimeSettings

__all__ = [
    "CircuitBreaker",
    "RateCoordinator",
    "SourceRegistry",
    "SourceRouter",
    "PipelineRuntime",
    "PipelineRuntimeSettings",
]

