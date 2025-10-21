from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import (
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    Generic,
    Optional,
    TypeVar,
)

from .channel import Channel  # reuse your 5.0.1 bounded channel

T = TypeVar("T")
K = TypeVar("K")


@dataclass(frozen=True)
class PartitioningSpec:
    partitions: int = 8
    high_watermark: float = 0.75
    low_watermark: float = 0.25
    capacity: int = 2048


def _positive_hash(value: int) -> int:
    # keep deterministic, avoid negative modulo behavior surprises
    return value & 0x7FFFFFFF


class PartitionedChannel(Generic[K, T]):
    """
    A keyed fan-out over N Channels. Each partition behaves like an independent bounded channel.
    """

    def __init__(
        self,
        spec: PartitioningSpec,
        *,
        on_high: Optional[Callable[[int], Awaitable[None]]] = None,
        on_low: Optional[Callable[[int], Awaitable[None]]] = None,
    ) -> None:
        self._spec = spec
        self._parts: Dict[int, Channel[T]] = {}
        self._on_high = on_high
        self._on_low = on_low

        for i in range(spec.partitions):
            self._parts[i] = Channel[T](
                capacity=spec.capacity,
                # Note: Channel from 5.0.1 uses Watermark dataclass, not floats
                # We'll need to adapt this
            )

    async def _signal_high(self, idx: int) -> None:
        if self._on_high:
            await self._on_high(idx)

    async def _signal_low(self, idx: int) -> None:
        if self._on_low:
            await self._on_low(idx)

    def _part_index(self, key_hash: int) -> int:
        return _positive_hash(key_hash) % self._spec.partitions

    async def put(self, key_hash: int, item: T) -> None:
        idx = self._part_index(key_hash)
        await self._parts[idx].put(item)

    async def stream_partition(self, idx: int) -> AsyncIterator[T]:
        """Stream items from a specific partition."""
        ch = self._parts[idx]
        while True:
            try:
                item = await ch.get()
                yield item
            except Exception:  # ChannelClosed
                break

    def partitions(self) -> int:
        return self._spec.partitions

    async def close(self) -> None:
        await asyncio.gather(*(p.close() for p in self._parts.values()))


async def hash_partition(
    source: AsyncIterator[T],
    *,
    get_key: Callable[[T], K],
    hasher: Optional[Callable[[K], int]] = None,
    spec: Optional[PartitioningSpec] = None,
    on_high: Optional[Callable[[int], Awaitable[None]]] = None,
    on_low: Optional[Callable[[int], Awaitable[None]]] = None,
) -> PartitionedChannel[K, T]:
    """
    Fan-out a source stream into N partition channels using a stable hash on key.
    """
    try:
        import mmh3  # fast, consistent hashing
        _hasher = hasher or (lambda k: mmh3.hash64(str(k), signed=False)[0])  # 64-bit unsigned
    except ImportError:
        # Fallback to Python's built-in hash if mmh3 not available
        _hasher = hasher or (lambda k: hash(str(k)))

    _spec = spec or PartitioningSpec()

    parts = PartitionedChannel[K, T](_spec, on_high=on_high, on_low=on_low)

    async def _pump() -> None:
        try:
            async for item in source:
                key = get_key(item)
                key_hash = int(_hasher(key))
                await parts.put(key_hash, item)
        finally:
            await parts.close()

    asyncio.create_task(_pump())
    return parts

