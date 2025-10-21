"""Simple test script to demonstrate pipeline builder functionality."""

import asyncio
from market_data_pipeline import (
    PipelineBuilder,
    PipelineSpec,
    PipelineOverrides,
    create_pipeline,
    get_pipeline_config,
)


def test_basic_imports():
    """Test that all components can be imported."""
    print("✓ All pipeline builder components imported successfully")
    return True


def test_config_loading():
    """Test configuration loading."""
    config = get_pipeline_config()
    print(f"✓ Configuration loaded: batch_size={config.batch_size}, flush_ms={config.flush_ms}")
    return True


def test_pipeline_spec_creation():
    """Test creating pipeline specifications."""
    spec = PipelineSpec(
        tenant_id="test_tenant",
        pipeline_id="test_pipeline",
        source="synthetic",
        symbols=["AAPL", "MSFT"],
        operator="bars",
        sink="store"
    )
    
    print(f"✓ Pipeline spec created: {spec.tenant_id}/{spec.pipeline_id}")
    print(f"  Source: {spec.source}, Symbols: {spec.symbols}")
    print(f"  Operator: {spec.operator}, Sink: {spec.sink}")
    return True


def test_pipeline_overrides():
    """Test pipeline overrides."""
    overrides = PipelineOverrides(
        ticks_per_sec=200,
        batch_size=1000,
        sink_workers=4,
        bar_window_sec=5
    )
    
    print(f"✓ Pipeline overrides created:")
    print(f"  ticks_per_sec: {overrides.ticks_per_sec}")
    print(f"  batch_size: {overrides.batch_size}")
    print(f"  sink_workers: {overrides.sink_workers}")
    print(f"  bar_window_sec: {overrides.bar_window_sec}")
    return True


def test_builder_creation():
    """Test pipeline builder creation."""
    config = get_pipeline_config()
    builder = PipelineBuilder(config=config)
    
    print(f"✓ Pipeline builder created with config")
    print(f"  Config batch_size: {config.batch_size}")
    print(f"  Config flush_ms: {config.flush_ms}")
    return True


def test_validation():
    """Test pipeline validation."""
    builder = PipelineBuilder()
    
    # Test valid spec
    valid_spec = PipelineSpec(
        tenant_id="test_tenant",
        pipeline_id="test_pipeline",
        source="synthetic",
        symbols=["AAPL"],
        operator="bars",
        sink="store"
    )
    
    try:
        builder._validate_spec(valid_spec)
        print("✓ Valid pipeline spec passed validation")
    except Exception as e:
        print(f"✗ Valid spec failed validation: {e}")
        return False
    
    # Test invalid spec
    invalid_spec = PipelineSpec(
        tenant_id="",  # Empty tenant_id
        pipeline_id="test_pipeline",
        source="synthetic",
        symbols=["AAPL"]
    )
    
    try:
        builder._validate_spec(invalid_spec)
        print("✗ Invalid spec should have failed validation")
        return False
    except Exception as e:
        print(f"✓ Invalid spec correctly failed validation: {e}")
    
    return True


def test_convenience_function():
    """Test the convenience function (without actually building)."""
    try:
        # This will fail at build time due to missing dependencies, but we can test the function exists
        from market_data_pipeline import create_pipeline
        print("✓ create_pipeline function imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import create_pipeline: {e}")
        return False


def main():
    """Run all tests."""
    print("Pipeline Builder Simple Test")
    print("=" * 40)
    
    tests = [
        test_basic_imports,
        test_config_loading,
        test_pipeline_spec_creation,
        test_pipeline_overrides,
        test_builder_creation,
        test_validation,
        test_convenience_function,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
