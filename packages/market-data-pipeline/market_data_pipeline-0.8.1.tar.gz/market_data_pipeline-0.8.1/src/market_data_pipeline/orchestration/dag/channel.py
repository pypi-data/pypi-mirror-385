from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")

class ChannelClosed(RuntimeError):
    pass

@dataclass(frozen=True)
class Watermark:
    high: int
    low: int

class Channel(Generic[T]):
    """
    A bounded async channel with high/low watermark callbacks for backpressure signaling.
    """
    def __init__(
        self,
        capacity: int = 2048,
        *,
        watermark: Watermark | None = None,
        on_high: Callable[[], Awaitable[None]] | None = None,
        on_low: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._q: asyncio.Queue[T] = asyncio.Queue(capacity)
        self._closed = asyncio.Event()
        self._watermark = watermark or Watermark(high=max(1, capacity * 3 // 4), low=max(1, capacity // 4))
        self._on_high = on_high
        self._on_low = on_low
        self._last_high = False  # avoid duplicate signals

    @property
    def capacity(self) -> int:
        return self._q.maxsize

    def size(self) -> int:
        return self._q.qsize()

    def closed(self) -> bool:
        return self._closed.is_set()

    async def close(self) -> None:
        self._closed.set()

    async def put(self, item: T) -> None:
        if self.closed():
            raise ChannelClosed("put() on closed channel")
        await self._q.put(item)
        await self._maybe_signal()

    async def get(self) -> T:
        while True:
            if self.closed() and self._q.empty():
                raise ChannelClosed("get() from closed+drained channel")
            try:
                item = await asyncio.wait_for(self._q.get(), timeout=0.1)
                await self._maybe_signal()
                return item
            except TimeoutError:
                # loop until either item appears or channel fully closed/drained
                if self.closed() and self._q.empty():
                    raise ChannelClosed("get() from closed+drained channel")

    async def _maybe_signal(self) -> None:
        # Watermark callbacks are best-effort (do not block channel ops).
        q = self.size()
        if not self._last_high and q >= self._watermark.high:
            self._last_high = True
            if self._on_high:
                asyncio.create_task(self._on_high())
        elif self._last_high and q <= self._watermark.low:
            self._last_high = False
            if self._on_low:
                asyncio.create_task(self._on_low())

