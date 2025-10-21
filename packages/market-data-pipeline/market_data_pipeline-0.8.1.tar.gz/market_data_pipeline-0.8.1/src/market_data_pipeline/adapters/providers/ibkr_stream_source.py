from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable
from typing import Literal

from loguru import logger

from .provider_base import ProviderSource

# Optional imports - fail gracefully if not installed
try:
    from market_data_core import Bar, Instrument, Quote
    from market_data_ibkr import IBKRProvider, IBKRSettings

    HAS_IBKR = True
except ImportError:
    HAS_IBKR = False
    # Fallback types for type checking
    Bar = None  # type: ignore[misc,assignment]
    Instrument = None  # type: ignore[misc,assignment]
    Quote = None  # type: ignore[misc,assignment]
    IBKRProvider = None  # type: ignore[misc,assignment]
    IBKRSettings = None  # type: ignore[misc,assignment]

Mode = Literal["quotes", "bars"]


class IBKRStreamSource(ProviderSource):  # type: ignore[type-arg]
    """Wraps IBKRProvider and exposes an async iterator of Quote or Bar events."""

    def __init__(
        self,
        *,
        symbols: Iterable[str],
        mode: Mode = "quotes",
        bar_resolution: str = "5s",
        ibkr_settings: IBKRSettings | None = None,  # type: ignore[valid-type]
        provider: IBKRProvider | None = None,  # type: ignore[valid-type]
        graceful_cancel_timeout: float = 2.0,
    ) -> None:
        if not HAS_IBKR:
            msg = "market-data-ibkr and market-data-core are required for IBKRStreamSource"
            raise ImportError(msg)

        self._symbols = list(symbols)
        self._mode = mode
        self._resolution = bar_resolution
        self._prov = provider or IBKRProvider(ibkr_settings or IBKRSettings())
        self._started = False
        self._cancel_evt = asyncio.Event()
        self._graceful_cancel_timeout = graceful_cancel_timeout

    async def start(self) -> None:
        if self._started:
            return
        self._started = True
        logger.info(f"IBKRStreamSource starting: mode={self._mode} symbols={self._symbols}")

    async def stop(self) -> None:
        if not self._started:
            return
        logger.info("IBKRStreamSource stopping…")
        self._cancel_evt.set()
        # give upstream coroutines a chance to unwind
        try:
            await asyncio.wait_for(self._prov.close(), timeout=self._graceful_cancel_timeout)
        except Exception as e:
            logger.warning(f"IBKRProvider close timeout/err: {e}")
        self._started = False

    def stream(self) -> AsyncIterator:  # type: ignore[type-arg]
        if self._mode == "quotes":
            return self._stream_quotes()
        else:
            return self._stream_bars()

    async def _stream_quotes(self) -> AsyncIterator:  # type: ignore[type-arg]
        instruments = [Instrument(symbol=s) for s in self._symbols]
        async for q in self._prov.stream_quotes(instruments):
            if self._cancel_evt.is_set():
                break
            yield q  # already a Core DTO

    async def _stream_bars(self) -> AsyncIterator:  # type: ignore[type-arg]
        instruments = [Instrument(symbol=s) for s in self._symbols]
        async for b in self._prov.stream_bars(self._resolution, instruments):
            if self._cancel_evt.is_set():
                break
            yield b

