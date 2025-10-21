from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from loguru import logger

from .ibkr_stream_source import IBKRStreamSource
from .provider_base import ProviderSource

Mode = Literal["quotes", "bars"]


class ProviderRegistry:
    """Simple name→factory registry. Can evolve to entrypoints later."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable[..., ProviderSource[Any]]] = {}
        # default registrations
        self.register("ibkr", self._make_ibkr)

    def register(self, name: str, factory: Callable[..., ProviderSource[Any]]) -> None:
        self._factories[name] = factory

    def build(
        self,
        name: str,
        *,
        symbols: list[str] | tuple[str, ...],
        mode: Mode = "quotes",
        **kwargs: Any,
    ) -> ProviderSource[Any]:
        if name not in self._factories:
            msg = f"provider '{name}' not found"
            raise KeyError(msg)
        logger.info(f"ProviderRegistry.build: name={name} mode={mode} symbols={list(symbols)}")
        return self._factories[name](symbols=symbols, mode=mode, **kwargs)

    # built-in
    def _make_ibkr(
        self, *, symbols: list[str] | tuple[str, ...], mode: Mode = "quotes", **kwargs: Any
    ) -> ProviderSource[Any]:
        return IBKRStreamSource(symbols=symbols, mode=mode, **kwargs)

