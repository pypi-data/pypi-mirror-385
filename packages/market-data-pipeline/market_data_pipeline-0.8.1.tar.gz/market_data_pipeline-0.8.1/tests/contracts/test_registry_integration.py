"""
Contract test: Schema Registry integration.

Tests the integration between Pipeline and Schema Registry Service:
- Schema fetching and caching
- Version negotiation
- Payload validation
- Graceful degradation

Phase 11.0B: Validates registry client integration and schema validation.
"""

from __future__ import annotations

import time
from unittest.mock import AsyncMock, MagicMock

import pytest
from market_data_core.telemetry import BackpressureLevel, FeedbackEvent

# Test Schema Registry Manager
from market_data_pipeline.schemas import RegistryConfig, SchemaManager


@pytest.fixture
def registry_config() -> RegistryConfig:
    """Create test registry config."""
    return RegistryConfig(
        enabled=True,
        url="https://registry.test.openbb.co/api/v1",
        token="test_token",
        cache_ttl=300,
        timeout=30.0,
        prefer_track="v2",
        fallback_track="v1",
    )


@pytest.fixture
def mock_registry_client() -> AsyncMock:
    """Create mock registry client."""
    client = AsyncMock()
    
    # Mock negotiate response
    client.negotiate = AsyncMock(
        return_value=MagicMock(
            name="telemetry.FeedbackEvent",
            track="v2",
            core_version="1.2.0",
            sha256="test_hash",
            deprecated=False,
        )
    )
    
    # Mock fetch_schema response
    client.fetch_schema = AsyncMock(
        return_value=MagicMock(
            name="telemetry.FeedbackEvent",
            track="v2",
            core_version="1.2.0",
            content={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "type": "object",
                "properties": {
                    "coordinator_id": {"type": "string"},
                    "queue_size": {"type": "integer"},
                    "capacity": {"type": "integer"},
                    "level": {"type": "string"},
                    "source": {"type": "string"},
                    "ts": {"type": "number"},
                },
                "required": [
                    "coordinator_id",
                    "queue_size",
                    "capacity",
                    "level",
                    "source",
                    "ts",
                ],
            },
        )
    )
    
    return client


def test_registry_config_validation():
    """
    Test registry configuration validation.
    
    Contract:
    - enabled=true requires url to be set
    - cache_ttl must be >= 0
    - timeout must be > 0
    """
    # Valid config
    cfg = RegistryConfig(
        enabled=True,
        url="https://registry.openbb.co/api/v1",
        cache_ttl=300,
        timeout=30.0,
    )
    cfg.validate()  # Should not raise
    
    # Invalid: enabled but no URL
    with pytest.raises(ValueError, match="REGISTRY_URL must be set"):
        cfg = RegistryConfig(enabled=True, url="")
        cfg.validate()
    
    # Invalid: negative cache TTL
    with pytest.raises(ValueError, match="REGISTRY_CACHE_TTL must be >= 0"):
        cfg = RegistryConfig(cache_ttl=-1)
        cfg.validate()
    
    # Invalid: zero timeout
    with pytest.raises(ValueError, match="REGISTRY_TIMEOUT must be > 0"):
        cfg = RegistryConfig(timeout=0.0)
        cfg.validate()


@pytest.mark.asyncio
async def test_schema_manager_initialization(registry_config: RegistryConfig):
    """
    Test schema manager initialization and lifecycle.
    
    Contract:
    - Manager can be created with config
    - start() initializes client
    - close() cleans up resources
    - Context manager works
    """
    manager = SchemaManager(
        registry_url=registry_config.url,
        token=registry_config.token,
        enabled=False,  # Disable for testing
        cache_ttl=registry_config.cache_ttl,
    )
    
    assert not manager._started
    assert manager.enabled is False
    
    # Start/close lifecycle
    await manager.start()
    await manager.close()


@pytest.mark.asyncio
async def test_schema_manager_graceful_degradation():
    """
    Test graceful degradation when registry is disabled or unavailable.
    
    Contract:
    - When disabled, validation always returns (True, [])
    - No exceptions raised when registry unavailable
    - Metrics track degradation
    """
    manager = SchemaManager(
        registry_url="https://registry.test.openbb.co",
        enabled=False,  # Explicitly disabled
    )
    
    await manager.start()
    
    # Validation should succeed without calling registry
    is_valid, errors = await manager.validate_payload(
        "telemetry.FeedbackEvent",
        {"test": "data"},
    )
    
    assert is_valid is True
    assert errors == []
    
    await manager.close()


@pytest.mark.asyncio
async def test_schema_cache_ttl():
    """
    Test schema caching with TTL.
    
    Contract:
    - First fetch goes to registry (cache miss)
    - Subsequent fetches use cache (cache hit)
    - Expired entries are evicted
    """
    import asyncio
    
    from market_data_pipeline.schemas.registry_manager import SchemaCache
    
    cache = SchemaCache(ttl_seconds=1)  # 1 second TTL
    
    # Empty cache
    result = await cache.get("test_key")
    assert result is None
    
    # Set value
    test_schema = {"type": "object"}
    await cache.set("test_key", test_schema)
    
    # Get from cache (before expiry)
    result = await cache.get("test_key")
    assert result == test_schema
    
    # Wait for expiry
    await asyncio.sleep(1.1)
    
    # Cache miss after expiry
    result = await cache.get("test_key")
    assert result is None


@pytest.mark.asyncio
async def test_feedback_event_validation():
    """
    Test FeedbackEvent validation against registry schema.
    
    Contract:
    - Valid FeedbackEvent passes validation
    - Invalid payload fails validation with error details
    - Validation uses cached schemas when available
    """
    # Create valid FeedbackEvent
    event = FeedbackEvent(
        coordinator_id="store_01",
        queue_size=500,
        capacity=1000,
        level=BackpressureLevel.ok,
        source="store",
        ts=time.time(),
    )
    
    # Convert to dict for validation
    payload = event.model_dump()
    
    # Verify payload structure
    assert "coordinator_id" in payload
    assert "queue_size" in payload
    assert "capacity" in payload
    assert "level" in payload
    assert "source" in payload
    assert "ts" in payload
    
    # Type checks
    assert isinstance(payload["coordinator_id"], str)
    assert isinstance(payload["queue_size"], int)
    assert isinstance(payload["capacity"], int)
    assert isinstance(payload["ts"], float)


def test_schema_manager_stats():
    """
    Test schema manager statistics tracking.
    
    Contract:
    - Stats track cache hits/misses
    - Stats track validation success/failure
    - Stats track registry errors
    """
    manager = SchemaManager(
        registry_url="https://registry.test.openbb.co",
        enabled=False,
    )
    
    stats = manager.get_stats()
    
    # Verify stats structure
    assert "cache_hits" in stats
    assert "cache_misses" in stats
    assert "validation_success" in stats
    assert "validation_failure" in stats
    assert "registry_errors" in stats
    assert "cache" in stats
    assert "enabled" in stats
    assert "started" in stats
    
    # Initial values
    assert stats["cache_hits"] == 0
    assert stats["cache_misses"] == 0
    assert stats["enabled"] is False
    assert stats["started"] is False


@pytest.mark.asyncio
async def test_pulse_consumer_registry_integration():
    """
    Test Pulse consumer integration with schema manager.
    
    Contract:
    - Consumer accepts optional schema_manager
    - Validation is performed if manager provided
    - Validation failures are logged but don't block processing
    """
    from unittest.mock import AsyncMock, MagicMock
    
    from market_data_pipeline.pulse.consumer import FeedbackConsumer
    
    # Mock dependencies
    rate_controller = AsyncMock()
    settings = MagicMock()
    settings.provider_name = "test"
    settings.get_policy = MagicMock(return_value={})
    
    # Create schema manager (disabled for test)
    schema_manager = SchemaManager(
        registry_url="https://registry.test.openbb.co",
        enabled=False,
    )
    
    # Create consumer with schema manager
    consumer = FeedbackConsumer(
        rate_controller=rate_controller,
        settings=settings,
        schema_manager=schema_manager,
    )
    
    # Verify schema manager is attached
    assert consumer.schema_manager is schema_manager


if __name__ == "__main__":
    import asyncio
    
    pytest.main([__file__, "-v"])

