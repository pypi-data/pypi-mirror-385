"""
SourceRouter — Meta-source that wraps multiple TickSources or Providers.

Implements the TickSource protocol while routing requests to multiple
underlying sources with fallback and retry logic.
"""

from __future__ import annotations

import logging
from typing import AsyncIterator, List, Optional, Sequence

from ..errors import SourceError
from ..source.base import SourceStatus, TickSource
from ..source.capabilities import SourceCapabilities
from ..types import Quote

logger = logging.getLogger(__name__)


class RetryableError(SourceError):
    """Indicates an error that should trigger fallback to next source."""

    pass


class SourceRouter:
    """Routes quote streams across multiple sources with fallback.
    
    Implements TickSource protocol, allowing it to be used as a drop-in
    replacement for any single source. Provides automatic fallback when
    a source fails.
    
    Strategies:
    - "first": Use first available source, fallback on error
    - "round_robin": Distribute load across sources (future)
    - "fastest": Use source with lowest latency (future)
    
    Example:
        router = SourceRouter(
            sources=[ibkr_source, polygon_source],
            strategy="first"
        )
        
        # Router implements TickSource, can be used in pipeline
        async for quote in router.stream():
            process(quote)
    """

    def __init__(
        self,
        sources: Sequence[TickSource],
        strategy: str = "first",
        max_retries: int = 3,
    ) -> None:
        """Initialize source router.
        
        Args:
            sources: List of TickSource implementations to route between
            strategy: Routing strategy ("first", "round_robin", "fastest")
            max_retries: Maximum retry attempts per source
        """
        if not sources:
            raise ValueError("SourceRouter requires at least one source")
        
        self.sources = list(sources)
        self.strategy = strategy
        self.max_retries = max_retries
        self._current_source_idx = 0
        self._active_source: Optional[TickSource] = None

    async def stream(self) -> AsyncIterator[Quote]:
        """Stream quotes with automatic fallback on errors.
        
        Yields quotes from the first available source. On error,
        automatically fails over to the next source in the list.
        
        Yields:
            Quote objects from underlying sources
            
        Raises:
            SourceError: If all sources fail
        """
        if self.strategy == "first":
            async for quote in self._stream_first_available():
                yield quote
        else:
            raise NotImplementedError(f"Strategy {self.strategy} not yet implemented")

    async def _stream_first_available(self) -> AsyncIterator[Quote]:
        """Stream from first available source with fallback."""
        last_error: Optional[Exception] = None
        
        for source in self.sources:
            try:
                logger.info("Attempting to stream from source: %s", source)
                self._active_source = source
                
                # Start source if it supports explicit start
                if hasattr(source, "start"):
                    await source.start()
                
                # Stream quotes
                async for quote in source.stream():
                    yield quote
                
                # If we get here, streaming completed successfully
                logger.info("Source %s completed successfully", source)
                break
                
            except RetryableError as err:
                logger.warning(
                    "Source %s failed with retryable error: %s. Trying next source...",
                    source,
                    err,
                )
                last_error = err
                continue
                
            except Exception as err:
                logger.error(
                    "Source %s failed with unexpected error: %s",
                    source,
                    err,
                    exc_info=True,
                )
                last_error = err
                continue
        else:
            # All sources failed
            raise SourceError(
                f"All sources failed. Last error: {last_error}"
            ) from last_error

    async def status(self) -> SourceStatus:
        """Get status of currently active source.
        
        Returns:
            SourceStatus of active source, or disconnected if none active
        """
        if self._active_source:
            return await self._active_source.status()
        return SourceStatus(connected=False, detail="No active source")

    async def close(self) -> None:
        """Close all underlying sources."""
        logger.info("Closing source router and all underlying sources")
        
        for source in self.sources:
            try:
                await source.close()
            except Exception as e:
                logger.warning("Error closing source %s: %s", source, e)

    @property
    def symbols(self) -> List[str]:
        """Get symbols from currently active source.
        
        Returns:
            List of symbols from active source, or empty list if none active
        """
        if self._active_source and hasattr(self._active_source, "symbols"):
            return self._active_source.symbols
        return []

    @property
    def capabilities(self) -> SourceCapabilities:
        """Get combined capabilities of all sources.
        
        Returns union of all source capabilities.
        
        Returns:
            Combined SourceCapabilities
        """
        combined = SourceCapabilities(0)
        for source in self.sources:
            if hasattr(source, "capabilities"):
                combined |= source.capabilities
        return combined

    async def start(self) -> None:
        """Start all sources that support explicit start."""
        logger.info("Starting source router")
        
        for source in self.sources:
            if hasattr(source, "start"):
                try:
                    await source.start()
                    logger.debug("Started source: %s", source)
                except Exception as e:
                    logger.warning("Failed to start source %s: %s", source, e)

    def add_source(self, source: TickSource) -> None:
        """Add a new source to the router.
        
        Args:
            source: TickSource to add
        """
        self.sources.append(source)
        logger.info("Added source to router: %s", source)

    def remove_source(self, source: TickSource) -> None:
        """Remove a source from the router.
        
        Args:
            source: TickSource to remove
        """
        if source in self.sources:
            self.sources.remove(source)
            logger.info("Removed source from router: %s", source)

