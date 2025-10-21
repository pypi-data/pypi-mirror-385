"""Examples demonstrating the pipeline_builder functionality."""

import asyncio
from market_data_pipeline import (
    PipelineBuilder,
    PipelineSpec,
    PipelineOverrides,
    create_pipeline,
    get_pipeline_config,
)


async def example_synthetic_bars_store():
    """Example: Synthetic data -> bars -> store pipeline."""
    print("=== Synthetic -> Bars -> Store Pipeline ===")
    
    # Simple approach using convenience function
    pipeline = create_pipeline(
        tenant_id="demo_tenant",
        pipeline_id="synthetic_demo",
        source="synthetic",
        symbols=["AAPL", "MSFT", "GOOGL"],
        duration_sec=10.0,  # Run for 10 seconds
        operator="bars",
        sink="store"
    )
    
    print(f"Created pipeline: {pipeline}")
    print("Pipeline components:")
    print(f"  Source: {pipeline.source}")
    print(f"  Operator: {pipeline.operator}")
    print(f"  Batcher: {pipeline.batcher}")
    print(f"  Sink: {pipeline.sink}")
    
    # Run the pipeline
    try:
        await pipeline.run(duration_sec=10.0)
        print("Pipeline completed successfully!")
    except Exception as e:
        print(f"Pipeline failed: {e}")
    finally:
        await pipeline.close()


async def example_ibkr_bars_store_with_overrides():
    """Example: IBKR data -> bars -> store with custom overrides."""
    print("\n=== IBKR -> Bars -> Store Pipeline (with overrides) ===")
    
    # Custom overrides for high-frequency trading
    overrides = {
        "ticks_per_sec": 500,           # Higher tick rate
        "pacing_max_per_sec": 2000,     # Higher pacing limit
        "pacing_burst": 3000,           # Larger burst capacity
        "batch_size": 1000,             # Larger batches
        "flush_ms": 50,                 # Faster flush
        "sink_workers": 4,               # More sink workers
        "sink_queue_max": 500,          # Larger queue
        "bar_allowed_lateness_sec": 1,  # Allow 1 second lateness
    }
    
    pipeline = create_pipeline(
        tenant_id="trading_tenant",
        pipeline_id="ibkr_hft",
        source="ibkr",
        symbols=["SPY", "QQQ", "IWM", "GLD"],
        operator="bars",
        sink="store",
        overrides=overrides
    )
    
    print(f"Created high-frequency IBKR pipeline: {pipeline}")
    print("Custom configuration applied:")
    for key, value in overrides.items():
        print(f"  {key}: {value}")
    
    # Note: In production, you'd run this without duration_sec for continuous operation
    # await pipeline.run()  # Run indefinitely


async def example_replay_options_kafka():
    """Example: Replay data -> options -> Kafka pipeline."""
    print("\n=== Replay -> Options -> Kafka Pipeline ===")
    
    # Using the builder pattern for more control
    builder = PipelineBuilder()
    
    spec = PipelineSpec(
        tenant_id="research_tenant",
        pipeline_id="options_analysis",
        source="replay",
        operator="options",
        sink="kafka",
        overrides=PipelineOverrides(
            replay_path="/data/market_replay_2024.parquet",
            replay_speed=2.0,  # 2x speed
            kafka_bootstrap="kafka-cluster:9092",
            kafka_topic="options_chains",
            batch_size=2000,    # Larger batches for options data
            flush_ms=200,       # Slower flush for options
            sink_workers=6,     # More workers for complex options processing
        )
    )
    
    try:
        pipeline = builder.build(spec)
        print(f"Created options analysis pipeline: {pipeline}")
        print("Configuration:")
        print(f"  Replay file: {spec.overrides.replay_path}")
        print(f"  Replay speed: {spec.overrides.replay_speed}x")
        print(f"  Kafka topic: {spec.overrides.kafka_topic}")
        print(f"  Batch size: {spec.overrides.batch_size}")
        
        # Run for analysis
        await pipeline.run(duration_sec=60.0)  # 1 minute analysis
        print("Options analysis completed!")
        
    except Exception as e:
        print(f"Pipeline creation failed: {e}")
    finally:
        if 'pipeline' in locals():
            await pipeline.close()


def example_custom_configuration():
    """Example: Using custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    # Create custom config
    from market_data_pipeline.config import PipelineSettings
    
    custom_config = PipelineSettings(
        batch_size=2000,
        flush_ms=50,
        sink_workers=8,
        pacing_max_per_sec=5000,
        ticks_per_sec=1000,
        bar_window_sec=5,  # 5-second bars
        bar_allowed_lateness_sec=2,
    )
    
    # Use custom config with builder
    builder = PipelineBuilder(config=custom_config)
    
    spec = PipelineSpec(
        tenant_id="custom_tenant",
        pipeline_id="custom_pipeline",
        source="synthetic",
        symbols=["BTC-USD", "ETH-USD"],  # Crypto symbols
        operator="bars",
        sink="store"
    )
    
    pipeline = builder.build(spec)
    print(f"Created pipeline with custom config: {pipeline}")
    print("Custom settings applied:")
    print(f"  Batch size: {custom_config.batch_size}")
    print(f"  Flush interval: {custom_config.flush_ms}ms")
    print(f"  Sink workers: {custom_config.sink_workers}")
    print(f"  Bar window: {custom_config.bar_window_sec}s")


async def example_error_handling():
    """Example: Error handling and validation."""
    print("\n=== Error Handling Example ===")
    
    # Example 1: Missing required dependencies
    try:
        pipeline = create_pipeline(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="ibkr",  # IBKR not installed
            symbols=["AAPL"]
        )
        print("IBKR pipeline created (unexpected)")
    except Exception as e:
        print(f"Expected error for missing IBKR: {e}")
    
    # Example 2: Invalid configuration
    try:
        pipeline = create_pipeline(
            tenant_id="",  # Empty tenant_id
            pipeline_id="test_pipeline",
            source="synthetic",
            symbols=["AAPL"]
        )
        print("Pipeline created with empty tenant_id (unexpected)")
    except Exception as e:
        print(f"Expected error for empty tenant_id: {e}")
    
    # Example 3: Missing symbols for synthetic source
    try:
        pipeline = create_pipeline(
            tenant_id="test_tenant",
            pipeline_id="test_pipeline",
            source="synthetic",
            symbols=[]  # Empty symbols
        )
        print("Synthetic pipeline created without symbols (unexpected)")
    except Exception as e:
        print(f"Expected error for missing symbols: {e}")


async def example_production_workflow():
    """Example: Production workflow with proper error handling."""
    print("\n=== Production Workflow Example ===")
    
    # Production configuration
    config = get_pipeline_config()
    
    # Create multiple pipelines for different purposes
    pipelines = []
    
    try:
        # Market data pipeline
        market_pipeline = create_pipeline(
            tenant_id="prod_tenant",
            pipeline_id="market_data",
            source="synthetic",
            symbols=["SPY", "QQQ", "IWM"],
            operator="bars",
            sink="store",
            overrides={
                "batch_size": 1000,
                "sink_workers": 4,
                "bar_window_sec": 1,
            }
        )
        pipelines.append(market_pipeline)
        
        # Options pipeline (if available)
        try:
            options_pipeline = create_pipeline(
                tenant_id="prod_tenant",
                pipeline_id="options_data",
                source="synthetic",
                symbols=["SPY"],
                operator="options",
                sink="store",
                overrides={
                    "batch_size": 500,
                    "sink_workers": 2,
                    "bar_window_sec": 5,
                }
            )
            pipelines.append(options_pipeline)
            print("Options pipeline created")
        except Exception as e:
            print(f"Options pipeline not available: {e}")
        
        print(f"Created {len(pipelines)} production pipelines")
        
        # Run all pipelines concurrently
        tasks = []
        for i, pipeline in enumerate(pipelines):
            task = asyncio.create_task(
                pipeline.run(duration_sec=30.0),
                name=f"pipeline_{i}"
            )
            tasks.append(task)
        
        # Wait for all pipelines to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Pipeline {i} failed: {result}")
            else:
                print(f"Pipeline {i} completed successfully")
                
    finally:
        # Clean up all pipelines
        for pipeline in pipelines:
            try:
                await pipeline.close()
            except Exception as e:
                print(f"Error closing pipeline: {e}")


async def example_database_sink():
    """Example: Using the new production-grade DatabaseSink."""
    print("\n=== Database Sink Example ===")
    
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
    """Run all examples."""
    print("Pipeline Builder Examples")
    print("=" * 50)
    
    # Basic examples
    await example_synthetic_bars_store()
    await example_ibkr_bars_store_with_overrides()
    await example_replay_options_kafka()
    
    # Database sink example
    await example_database_sink()
    
    # Configuration examples
    example_custom_configuration()
    
    # Error handling
    await example_error_handling()
    
    # Production workflow
    await example_production_workflow()
    
    print("\nAll examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
