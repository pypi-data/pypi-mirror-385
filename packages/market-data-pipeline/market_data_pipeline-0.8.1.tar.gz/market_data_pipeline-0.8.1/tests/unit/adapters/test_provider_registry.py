"""Tests for provider registry."""
import pytest

pytest.importorskip("market_data_core")
pytest.importorskip("market_data_ibkr")

from market_data_pipeline.adapters.providers import ProviderRegistry


def test_registry_has_ibkr_by_default():
    """Registry includes IBKR provider by default."""
    reg = ProviderRegistry()
    src = reg.build("ibkr", symbols=["AAPL"], mode="quotes")
    assert hasattr(src, "stream")
    assert hasattr(src, "start")
    assert hasattr(src, "stop")


def test_registry_build_unknown_provider_raises():
    """Building unknown provider raises KeyError."""
    reg = ProviderRegistry()
    with pytest.raises(KeyError, match="not found"):
        reg.build("unknown_provider", symbols=["AAPL"], mode="quotes")


def test_registry_can_register_custom_provider():
    """Registry can be extended with custom providers."""
    from market_data_pipeline.adapters.providers.provider_base import ProviderSource
    
    class CustomProvider(ProviderSource):
        def __init__(self, **kwargs):
            self.kwargs = kwargs
        
        async def start(self) -> None:
            pass
        
        async def stop(self) -> None:
            pass
        
        def stream(self):
            async def _gen():
                yield 1
            return _gen()
    
    reg = ProviderRegistry()
    reg.register("custom", lambda **kwargs: CustomProvider(**kwargs))
    
    src = reg.build("custom", symbols=["TEST"], mode="quotes")
    assert isinstance(src, CustomProvider)

