"""Unit tests for SourceRegistry."""

import pytest

from market_data_pipeline.orchestration.registry import SourceRegistry
from market_data_pipeline.source.synthetic import SyntheticSource


class TestSourceRegistry:
    """Test SourceRegistry functionality."""

    def test_register_and_load(self):
        """Test manual registration and loading."""
        registry = SourceRegistry()
        
        # Register a source
        registry.register("synthetic", SyntheticSource)
        
        # Load it back
        loaded_cls = registry.load("synthetic")
        
        assert loaded_cls is SyntheticSource

    def test_list_sources(self):
        """Test listing registered sources."""
        registry = SourceRegistry()
        
        # Initially empty
        assert registry.list_sources() == []
        
        # Register some sources
        registry.register("synthetic", SyntheticSource)
        registry.register("test", SyntheticSource)
        
        # Check list
        sources = registry.list_sources()
        assert "synthetic" in sources
        assert "test" in sources
        assert len(sources) == 2

    def test_load_nonexistent_raises(self):
        """Test loading nonexistent source raises error."""
        registry = SourceRegistry()
        
        with pytest.raises(ImportError):
            registry.load("nonexistent_source_xyz")

    def test_load_builtin_source(self):
        """Test loading built-in source via import."""
        registry = SourceRegistry()
        
        # Should auto-load synthetic source
        source_cls = registry.load("synthetic")
        assert source_cls.__name__ == "SyntheticSource"

    def test_discover_entrypoints(self):
        """Test entrypoint discovery (may have no entrypoints in test env)."""
        registry = SourceRegistry()
        
        # Should not raise even if no entrypoints found
        registry.discover_entrypoints()
        
        # Verify it still works
        registry.register("test", SyntheticSource)
        assert "test" in registry.list_sources()

