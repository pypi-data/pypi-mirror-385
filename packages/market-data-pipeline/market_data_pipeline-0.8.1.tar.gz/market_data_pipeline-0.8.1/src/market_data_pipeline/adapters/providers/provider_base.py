from __future__ import annotations

import abc
from collections.abc import AsyncIterator
from typing import Generic, TypeVar

T = TypeVar("T")


class ProviderSource(abc.ABC, Generic[T]):
    """Minimal common interface for provider-backed async sources."""

    @abc.abstractmethod
    async def start(self) -> None:
        """Initialize and start the provider connection."""
        ...

    @abc.abstractmethod
    async def stop(self) -> None:
        """Stop the provider and clean up resources."""
        ...

    @abc.abstractmethod
    def stream(self) -> AsyncIterator[T]:
        """Return an async iterator of data items."""
        ...

