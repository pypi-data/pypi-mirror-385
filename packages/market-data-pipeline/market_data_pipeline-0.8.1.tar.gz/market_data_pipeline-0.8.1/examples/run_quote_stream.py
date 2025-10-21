"""
Demonstrates opt-in orchestration using PipelineRuntime.

This example shows how to use the Phase 3.0 orchestration layer
to stream quotes with automatic source routing and rate limiting.
"""

import asyncio
import logging

from market_data_pipeline.orchestration import PipelineRuntime, PipelineRuntimeSettings


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


async def main() -> None:
    """Run quote streaming with orchestration."""
    logger.info("Starting quote stream example...")
    
    # Create runtime settings
    # Note: Rate coordination is disabled for synthetic source in this example
    # Enable it when using real providers like IBKR
    settings = PipelineRuntimeSettings(
        orchestration_enabled=True,
        enable_rate_coordination=False,  # Disabled for synthetic
        circuit_breaker_threshold=5,
        circuit_breaker_timeout_sec=60.0,
    )
    
    # Use runtime as context manager
    async with PipelineRuntime(settings) as runtime:
        logger.info("Runtime initialized, streaming quotes...")
        
        # Stream quotes with automatic routing and rate limiting
        symbols = ["AAPL", "MSFT", "GOOGL"]
        count = 0
        max_quotes = 100  # Limit for demo
        
        try:
            async for quote in runtime.stream_quotes(symbols):
                logger.info(
                    "Quote: %s @ $%s (size: %s)",
                    quote.symbol,
                    quote.price,
                    quote.size,
                )
                
                count += 1
                if count >= max_quotes:
                    logger.info("Reached max quotes, stopping...")
                    break
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error("Error during streaming: %s", e, exc_info=True)
    
    logger.info("Quote stream complete. Total quotes: %d", count)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")

