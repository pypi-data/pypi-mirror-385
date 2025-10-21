from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from loguru import logger

# Core DAG operators (already in your repo from 5.0.1 / 5.0.3)
# These imports should be resilient; if not present, we skip registration.
try:
    from market_data_pipeline.orchestration.dag.operators import (
        buffer_async,
        filter_async,
        map_async,
        tumbling_window,
    )
except Exception:  # pragma: no cover
    map_async = filter_async = buffer_async = tumbling_window = None

try:
    from market_data_pipeline.orchestration.dag.contrib.operators_contrib import (
        deduplicate,
        resample_ohlc,
        router,
        throttle,
    )
except Exception:  # pragma: no cover
    resample_ohlc = deduplicate = throttle = router = None

# Provider adapters
try:
    from market_data_pipeline.adapters.providers.ibkr_stream_source import (
        IBKRStreamSource,
    )
except Exception:  # pragma: no cover
    IBKRStreamSource = None


@dataclass
class ComponentRegistry:
    """
    String → factory registry for providers and operators.

    YAML configs reference `type:` IDs that map to these registered factories.
    """

    providers: dict[str, Callable[..., Any]] = field(default_factory=dict)
    operators: dict[str, Callable[..., Any]] = field(default_factory=dict)

    # ----- Registration -----
    def register_provider(self, type_id: str, factory: Callable[..., Any]) -> None:
        self.providers[type_id] = factory

    def register_operator(self, type_id: str, factory: Callable[..., Any]) -> None:
        self.operators[type_id] = factory

    # ----- Lookup -----
    def build_provider(self, type_id: str, **kwargs: Any) -> Any:
        if type_id not in self.providers:
            msg = f"Provider type '{type_id}' not registered"
            raise KeyError(msg)
        logger.debug(f"Building provider: {type_id}({kwargs})")
        return self.providers[type_id](**kwargs)

    def get_operator(self, type_id: str) -> Callable[..., Any]:
        if type_id not in self.operators:
            msg = f"Operator type '{type_id}' not registered"
            raise KeyError(msg)
        return self.operators[type_id]


def default_registry() -> ComponentRegistry:
    """Create a registry with all available components registered."""
    reg = ComponentRegistry()

    # Providers
    if IBKRStreamSource:
        reg.register_provider("provider.ibkr.stream", IBKRStreamSource)

    # Core operators
    if map_async:
        reg.register_operator("operator.map", map_async)
    if filter_async:
        reg.register_operator("operator.filter", filter_async)
    if buffer_async:
        reg.register_operator("operator.buffer", buffer_async)
    if tumbling_window:
        reg.register_operator("operator.tumbling_window", tumbling_window)

    # Contrib
    if resample_ohlc:
        reg.register_operator("operator.resample_ohlc", resample_ohlc)
    if deduplicate:
        reg.register_operator("operator.deduplicate", deduplicate)
    if throttle:
        reg.register_operator("operator.throttle", throttle)
    if router:
        reg.register_operator("operator.router", router)

    return reg

