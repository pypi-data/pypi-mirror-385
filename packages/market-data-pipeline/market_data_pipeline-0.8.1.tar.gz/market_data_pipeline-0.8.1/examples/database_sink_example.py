"""Example demonstrating the production-grade DatabaseSink usage."""

import asyncio
import os
from market_data_pipeline.sink.database import DatabaseSink, DatabaseSinkSettings
from market_data_pipeline.context import PipelineContext


async def example_database_sink_direct():
    """Example: Using DatabaseSink directly with custom settings."""
    print("=== Direct DatabaseSink Usage ===")
    
    # Create custom settings
    settings = DatabaseSinkSettings(
        vendor="production_pipeline",
        timeframe="1s",
        workers=4,
        queue_max=500,
        backpressure_policy="drop_oldest",
        retry_max_attempts=6,
        retry_backoff_ms=75,
    )
    
    # Create context
    ctx = PipelineContext(tenant_id="T1", pipeline_id="database_demo")
    
    # Create the sink
    sink = DatabaseSink(
        tenant_id="T1",
        settings=settings,
        ctx=ctx,
        # Either pass a prebuilt processor...
        # processor=await AsyncBatchProcessor.from_env_async(),
        # ...or let the sink construct one (preferred package wins):
        database_url=os.getenv("DATABASE_URL"),
    )
    
    print(f"Created DatabaseSink: {sink}")
    print(f"Settings: {settings}")
    print(f"Capabilities: {sink.capabilities}")
    
    # Start the sink
    await sink.start()
    print("DatabaseSink started")
    
    # Simulate some data (in real usage, this would come from the pipeline)
    from market_data_pipeline.types import Bar
    from datetime import datetime
    from decimal import Decimal
    
    sample_bars = [
        Bar(
            symbol="AAPL",
            timestamp=datetime.now(),
            open=Decimal("150.00"),
            high=Decimal("151.00"),
            low=Decimal("149.50"),
            close=Decimal("150.75"),
            volume=Decimal("1000"),
            vwap=Decimal("150.25"),
            trade_count=50,
            source="synthetic",
            metadata={"test": True}
        ),
        Bar(
            symbol="MSFT",
            timestamp=datetime.now(),
            open=Decimal("300.00"),
            high=Decimal("301.50"),
            low=Decimal("299.00"),
            close=Decimal("300.50"),
            volume=Decimal("2000"),
            vwap=Decimal("300.25"),
            trade_count=75,
            source="synthetic",
            metadata={"test": True}
        )
    ]
    
    try:
        # Write the batch
        await sink.write(sample_bars)
        print(f"Wrote {len(sample_bars)} bars to database sink")
        
        # Flush to ensure data is persisted
        await sink.flush()
        print("Flushed data to database")
        
        # Get metrics
        metrics = sink.get_metrics()
        print(f"Database sink metrics: {metrics}")
        
    except Exception as e:
        print(f"Error writing to database sink: {e}")
    finally:
        # Close the sink
        await sink.close(drain=True)
        print("DatabaseSink closed")


async def example_database_sink_via_pipeline():
    """Example: Using DatabaseSink via PipelineBuilder."""
    print("\n=== DatabaseSink via PipelineBuilder ===")
    
    from market_data_pipeline import create_pipeline
    
    # Create a pipeline with database sink
    pipeline = create_pipeline(
        tenant_id="demo_tenant",
        pipeline_id="database_demo",
        source="synthetic",
        symbols=["AAPL", "MSFT"],
        duration_sec=5.0,
        operator="bars",
        sink="database"  # Use the new database sink
    )
    
    print(f"Created pipeline with DatabaseSink: {pipeline}")
    print("Pipeline components:")
    print(f"  Source: {pipeline.source}")
    print(f"  Operator: {pipeline.operator}")
    print(f"  Batcher: {pipeline.batcher}")
    print(f"  Sink: {pipeline.sink}")
    print(f"  Sink capabilities: {pipeline.sink.capabilities}")
    
    # Run the pipeline
    try:
        await pipeline.run(duration_sec=5.0)
        print("Database sink pipeline completed successfully!")
        
        # Show metrics
        metrics = pipeline.sink.get_metrics()
        print(f"Database sink metrics: {metrics}")
        
    except Exception as e:
        print(f"Database sink pipeline failed: {e}")
    finally:
        await pipeline.close()


async def main():
    """Run database sink examples."""
    print("Database Sink Examples")
    print("=" * 50)
    
    # Note: These examples require either:
    # 1. market_data_store with AsyncBatchProcessor, or
    # 2. mds_client with AMDS
    # 3. A DATABASE_URL environment variable for AMDS
    
    try:
        # Direct usage example
        await example_database_sink_direct()
        
        # Pipeline usage example
        await example_database_sink_via_pipeline()
        
    except Exception as e:
        print(f"Example failed (likely missing database dependencies): {e}")
        print("To run these examples, install either:")
        print("  - market_data_store (preferred)")
        print("  - mds_client")
        print("And set DATABASE_URL environment variable if using mds_client")
    
    print("\nDatabase sink examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
