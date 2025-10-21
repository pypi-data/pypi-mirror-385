"""Base batcher protocol."""

from __future__ import annotations

from typing import Optional, Protocol

from ..types import Bar


class Batcher(Protocol):
    """Protocol for batching aggregated data."""

    async def add(self, item: Bar) -> Optional[list[Bar]]:
        """Add an item to the batch. Returns a batch if ready to flush."""
        ...

    async def flush(self) -> Optional[list[Bar]]:
        """Force flush any remaining items in the batch."""
        ...
