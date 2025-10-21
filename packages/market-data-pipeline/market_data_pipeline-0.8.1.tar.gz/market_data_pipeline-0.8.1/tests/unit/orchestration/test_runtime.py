"""Unit tests for PipelineRuntime."""

import pytest

from market_data_pipeline.orchestration.runtime import (
    PipelineRuntime,
    PipelineRuntimeSettings,
)


class TestPipelineRuntime:
    """Test PipelineRuntime functionality."""
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Test runtime initialization."""
        settings = PipelineRuntimeSettings(
            orchestration_enabled=True,
            max_concurrent_pipelines=5,
        )
        
        runtime = PipelineRuntime(settings)
        
        assert not runtime._initialized
        assert runtime.settings.max_concurrent_pipelines == 5
        
        await runtime.initialize()
        
        assert runtime._initialized
        assert runtime.registry is not None
        assert runtime.service is not None
        
        await runtime.shutdown()
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using runtime as context manager."""
        settings = PipelineRuntimeSettings()
        
        async with PipelineRuntime(settings) as runtime:
            assert runtime._initialized
            assert runtime.service.running
        
        # Should be shutdown after context
        assert not runtime._initialized
    
    @pytest.mark.asyncio
    async def test_stream_quotes(self):
        """Test streaming quotes."""
        settings = PipelineRuntimeSettings(
            orchestration_enabled=True,
            enable_rate_coordination=False,  # Disable for simplicity
        )
        
        async with PipelineRuntime(settings) as runtime:
            # Stream a few quotes
            count = 0
            async for quote in runtime.stream_quotes(["AAPL"]):
                assert quote.symbol == "AAPL"
                count += 1
                if count >= 5:  # Limit for test
                    break
            
            assert count == 5
    
    @pytest.mark.asyncio
    async def test_list_pipelines(self):
        """Test listing pipelines."""
        settings = PipelineRuntimeSettings()
        
        async with PipelineRuntime(settings) as runtime:
            pipelines = await runtime.list_pipelines()
            
            # Should start with no pipelines
            assert isinstance(pipelines, list)
            assert len(pipelines) == 0
    
    def test_settings_defaults(self):
        """Test default settings."""
        settings = PipelineRuntimeSettings()
        
        assert settings.orchestration_enabled is True
        assert settings.max_concurrent_pipelines == 10
        assert settings.enable_rate_coordination is True
        assert settings.circuit_breaker_threshold == 5
        assert settings.circuit_breaker_timeout_sec == 60.0
    
    def test_settings_custom(self):
        """Test custom settings."""
        settings = PipelineRuntimeSettings(
            orchestration_enabled=False,
            max_concurrent_pipelines=20,
            circuit_breaker_threshold=10,
        )
        
        assert settings.orchestration_enabled is False
        assert settings.max_concurrent_pipelines == 20
        assert settings.circuit_breaker_threshold == 10

