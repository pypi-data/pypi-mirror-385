"""Tests for provider base classes."""
import pytest

from market_data_pipeline.adapters.providers.provider_base import ProviderSource


def test_provider_source_is_abstract():
    """ProviderSource cannot be instantiated directly."""
    with pytest.raises(TypeError):
        ProviderSource()  # type: ignore[abstract]


def test_provider_source_requires_methods():
    """ProviderSource subclasses must implement all abstract methods."""
    
    class IncompleteProvider(ProviderSource):
        async def start(self) -> None:
            pass
    
    with pytest.raises(TypeError):
        IncompleteProvider()  # type: ignore[abstract]

