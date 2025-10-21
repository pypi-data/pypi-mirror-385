"""
SourceRegistry — dynamic loader for TickSource or Provider implementations.

Provides runtime registration and discovery of market data sources.
Supports both static registration and dynamic loading via importlib.
"""

from __future__ import annotations

import importlib
import logging
from typing import Any, Dict, Type

logger = logging.getLogger(__name__)


class SourceRegistry:
    """Runtime registry for source/provider classes.
    
    This registry allows dynamic loading of TickSource implementations
    from the current package or external provider packages (e.g., market_data_ibkr).
    
    Example:
        registry = SourceRegistry()
        registry.register("synthetic", SyntheticSource)
        source_cls = registry.load("synthetic")
        source = source_cls(symbols=["AAPL"], ...)
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._sources: Dict[str, Type[Any]] = {}

    def register(self, name: str, source_cls: Type[Any]) -> None:
        """Manually register a source class.
        
        Args:
            name: Identifier for the source (e.g., "synthetic", "ibkr", "replay")
            source_cls: Source class that implements TickSource protocol
        """
        logger.debug("Registering source: %s → %s", name, source_cls)
        self._sources[name] = source_cls

    def load(self, name: str) -> Type[Any]:
        """Load a source class by name.
        
        First checks registered sources, then attempts dynamic import.
        
        Args:
            name: Source identifier
            
        Returns:
            Source class
            
        Raises:
            ImportError: If source cannot be loaded
        """
        # Check if already registered
        if name in self._sources:
            return self._sources[name]

        # Attempt to load from pipeline sources first
        try:
            module = importlib.import_module(f"market_data_pipeline.source.{name}")
            # Look for conventional class names
            for class_name in [
                f"{name.upper()}Source",
                f"{name.capitalize()}Source",
            ]:
                cls = getattr(module, class_name, None)
                if cls is not None:
                    self.register(name, cls)
                    return cls
        except ImportError:
            logger.debug("Source %s not found in pipeline package", name)

        # Attempt to load from external provider package
        try:
            module = importlib.import_module(f"market_data_{name}")
            # Look for Provider class
            for class_name in [
                f"{name.upper()}Provider",
                f"{name.capitalize()}Provider",
            ]:
                cls = getattr(module, class_name, None)
                if cls is not None:
                    self.register(name, cls)
                    return cls
            
            raise ImportError(f"No provider class found in market_data_{name}")
        except ImportError as exc:
            logger.error("Failed to load provider '%s': %s", name, exc)
            raise

    def list_sources(self) -> list[str]:
        """List all registered sources.
        
        Returns:
            List of source identifiers
        """
        return list(self._sources.keys())

    def discover_entrypoints(self, group: str = "market_data.providers") -> None:
        """Discover and register sources via package entrypoints.
        
        This allows external packages to register providers via pyproject.toml:
        
        [project.entry-points."market_data.providers"]
        ibkr = "market_data_ibkr:IBKRProvider"
        
        Args:
            group: Entrypoint group name
        """
        try:
            # Python 3.10+
            from importlib.metadata import entry_points
            
            eps = entry_points()
            if hasattr(eps, "select"):
                # Python 3.10+
                discovered = eps.select(group=group)
            else:
                # Python 3.9
                discovered = eps.get(group, [])
            
            for ep in discovered:
                try:
                    provider_cls = ep.load()
                    self.register(ep.name, provider_cls)
                    logger.info("Discovered provider via entrypoint: %s", ep.name)
                except Exception as e:
                    logger.warning("Failed to load entrypoint %s: %s", ep.name, e)
        except ImportError:
            logger.warning("importlib.metadata not available, skipping entrypoint discovery")

