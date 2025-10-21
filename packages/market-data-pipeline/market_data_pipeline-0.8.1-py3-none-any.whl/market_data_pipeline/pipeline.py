"""Streaming pipeline orchestrator."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from .batcher import Batcher
from .context import PipelineContext
from .errors import PipelineError
from .operator import Operator
from .sink import Sink
from .source import TickSource
from .types import Bar, Quote

logger = logging.getLogger(__name__)


class StreamingPipeline:
    """Main pipeline orchestrator for streaming market data processing."""

    def __init__(
        self,
        *,
        source: TickSource,
        operator: Operator,
        batcher: Batcher,
        sink: Sink,
        ctx: PipelineContext,
    ) -> None:
        """Initialize the streaming pipeline."""
        self.source = source
        self.operator = operator
        self.batcher = batcher
        self.sink = sink
        self.ctx = ctx
        self._running = False

    async def run(self, duration_sec: Optional[float] = None) -> None:
        """Run the pipeline for the specified duration or indefinitely."""
        if self._running:
            raise PipelineError("Pipeline is already running")

        self._running = True
        logger.info(
            "Starting pipeline",
            extra={
                "tenant_id": self.ctx.tenant_id,
                "pipeline_id": self.ctx.pipeline_id,
            },
        )

        try:
            if duration_sec:
                await asyncio.wait_for(self._run_loop(), timeout=duration_sec)
            else:
                await self._run_loop()
        except asyncio.TimeoutError:
            logger.info("Pipeline duration completed")
        except Exception as e:
            logger.error("Pipeline error", exc_info=e)
            raise
        finally:
            await self._graceful_shutdown()

    async def _run_loop(self) -> None:
        """Main processing loop."""
        async for tick in self.source.stream():
            try:
                # Process tick through operator
                bar = await self.operator.handle(tick)

                if bar:
                    # Add to batcher
                    batch = await self.batcher.add(bar)

                    if batch:
                        # Write batch to sink
                        await self.sink.write(batch)

            except Exception as e:
                logger.error("Error processing tick", exc_info=e)
                # Continue processing other ticks

    async def _graceful_shutdown(self) -> None:
        """Gracefully shutdown the pipeline."""
        logger.info("Shutting down pipeline")

        # Flush any remaining items in batcher
        try:
            tail = await self.batcher.flush()
            if tail:
                await self.sink.write(tail)
        except Exception as e:
            logger.error("Error during graceful shutdown", exc_info=e)

        # Close all components
        try:
            await self.sink.close()
        except Exception as e:
            logger.error("Error closing sink", exc_info=e)

        try:
            await self.source.close()
        except Exception as e:
            logger.error("Error closing source", exc_info=e)

        self._running = False
        logger.info("Pipeline shutdown complete")
