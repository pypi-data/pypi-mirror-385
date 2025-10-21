"""
Schema Registry Manager with caching and validation.

Phase 11.0B: Integrates with Schema Registry Service for dynamic schema
negotiation, validation, and version management.

Phase 11.1: Adds enforcement modes (warn/strict) for validation failures.

Features:
    - Schema caching with TTL
    - Version negotiation (v2 preferred, v1 fallback)
    - Validation with detailed error reporting
    - Enforcement modes (warn/strict)
    - Preload critical schemas at startup
    - Graceful degradation on registry unavailable

Example:
    # Warn mode (default): log failures but continue
    manager = SchemaManager(
        registry_url="https://registry.openbb.co",
        enforcement_mode="warn"
    )
    await manager.start()
    
    # Validate payload
    is_valid, errors = await manager.validate_payload(
        "telemetry.FeedbackEvent",
        payload_dict,
        prefer="v2",
        fallback="v1"
    )
    
    # Strict mode: raise SchemaValidationError on failure
    manager = SchemaManager(
        registry_url="https://registry.openbb.co",
        enforcement_mode="strict"
    )
    await manager.start()
    
    try:
        await manager.validate_payload("telemetry.FeedbackEvent", payload_dict)
    except SchemaValidationError as e:
        logger.error(f"Validation failed: {e.errors}")
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from jsonschema import Draft7Validator, ValidationError
from loguru import logger

# Import metrics (graceful degradation if not available)
try:
    from ..metrics import (
        SCHEMA_CACHE_HITS,
        SCHEMA_CACHE_MISSES,
        SCHEMA_CACHE_SIZE,
        SCHEMA_ENFORCEMENT_ACTIONS,
        SCHEMA_REGISTRY_ERRORS,
        SCHEMA_VALIDATION_FAILURES,
        SCHEMA_VALIDATION_TOTAL,
    )
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

# Import SchemaValidationError
from ..errors import SchemaValidationError

try:
    from core_registry_client import RegistryClient, Track
    from core_registry_client.models import SchemaResponse
    from core_registry_client.client import SchemaNotFoundError
except ImportError:
    logger.warning(
        "core-registry-client not installed. Schema validation will be disabled."
    )
    # Fallback types for when client is not available
    class Track:  # type: ignore[no-redef]
        V1 = "v1"
        V2 = "v2"
    
    class SchemaNotFoundError(Exception):  # type: ignore[no-redef]
        pass
    
    RegistryClient = None  # type: ignore[misc,assignment]
    SchemaResponse = None  # type: ignore[misc,assignment]


class SchemaCache:
    """Simple TTL-based cache for schemas."""
    
    def __init__(self, ttl_seconds: int = 300) -> None:
        """
        Initialize schema cache.
        
        Args:
            ttl_seconds: Time-to-live for cached schemas (default: 5 minutes)
        """
        self.ttl_seconds = ttl_seconds
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Any | None:
        """Get cached schema if not expired."""
        async with self._lock:
            if key in self._cache:
                schema, timestamp = self._cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    # Update metrics
                    if METRICS_AVAILABLE:
                        SCHEMA_CACHE_SIZE.set(len(self._cache))
                    return schema
                # Expired, remove
                del self._cache[key]
            return None
    
    async def set(self, key: str, schema: Any) -> None:
        """Cache schema with current timestamp."""
        async with self._lock:
            self._cache[key] = (schema, time.time())
            # Update metrics
            if METRICS_AVAILABLE:
                SCHEMA_CACHE_SIZE.set(len(self._cache))
    
    async def clear(self) -> None:
        """Clear all cached schemas."""
        async with self._lock:
            self._cache.clear()
    
    def stats(self) -> dict[str, int]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "ttl_seconds": self.ttl_seconds,
        }


class SchemaManager:
    """
    Schema Registry Manager with caching and validation.
    
    Manages schema lifecycle: fetch, cache, validate, and refresh from Registry.
    Supports version negotiation and graceful degradation.
    
    Attributes:
        registry_url: Base URL of Schema Registry Service
        token: Optional admin token for write operations
        enabled: Whether registry integration is enabled
        cache_ttl: Cache TTL in seconds (default: 300)
    """
    
    def __init__(
        self,
        registry_url: str,
        token: str | None = None,
        enabled: bool = True,
        cache_ttl: int = 300,
        timeout: float = 30.0,
        enforcement_mode: str = "warn",
    ) -> None:
        """
        Initialize schema manager.
        
        Args:
            registry_url: Base URL of registry service
            token: Optional admin token
            enabled: Enable/disable registry (for testing)
            cache_ttl: Cache TTL in seconds
            timeout: Request timeout in seconds
            enforcement_mode: Enforcement mode (warn|strict, default: warn)
        """
        self.registry_url = registry_url
        self.token = token
        self.enabled = enabled
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.enforcement_mode = enforcement_mode
        
        if enforcement_mode not in ("warn", "strict"):
            raise ValueError("enforcement_mode must be 'warn' or 'strict'")
        
        self._client: Any = None
        self._cache = SchemaCache(ttl_seconds=cache_ttl)
        self._started = False
        
        # Metrics tracking
        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "validation_success": 0,
            "validation_failure": 0,
            "registry_errors": 0,
            "enforcement_warnings": 0,
            "enforcement_rejections": 0,
        }
    
    async def start(self) -> None:
        """
        Initialize registry client and preload critical schemas.
        
        Raises:
            RuntimeError: If client initialization fails (when enabled=True)
        """
        if not self.enabled:
            logger.info("[registry] Schema registry disabled (enabled=false)")
            return
        
        if RegistryClient is None:
            logger.warning(
                "[registry] core-registry-client not available. "
                "Schema validation will be disabled."
            )
            self.enabled = False
            return
        
        try:
            self._client = RegistryClient(
                base_url=self.registry_url,
                token=self.token,
                timeout=self.timeout,
            )
            
            logger.info(
                f"[registry] Initialized client: url={self.registry_url} "
                f"cache_ttl={self.cache_ttl}s"
            )
            
            # Preload critical schemas
            await self._preload_schemas()
            
            self._started = True
            logger.info("[registry] Schema manager started successfully")
        
        except Exception as e:
            logger.error(f"[registry] Failed to initialize client: {e}")
            # Graceful degradation: disable registry on startup failure
            self.enabled = False
            raise RuntimeError(f"Registry client initialization failed: {e}")
    
    async def _preload_schemas(self) -> None:
        """Preload critical schemas into cache at startup."""
        critical_schemas = [
            ("telemetry.FeedbackEvent", "v2", "v1"),
            ("telemetry.RateAdjustment", "v2", "v1"),
        ]
        
        for name, prefer, fallback in critical_schemas:
            try:
                await self.get_schema(name, prefer=prefer, fallback=fallback)
                logger.info(f"[registry] Preloaded schema: {name}")
            except Exception as e:
                logger.warning(f"[registry] Failed to preload {name}: {e}")
    
    async def close(self) -> None:
        """Close registry client connections."""
        if self._client:
            await self._client.close()
            self._started = False
            logger.info("[registry] Schema manager closed")
    
    async def __aenter__(self) -> SchemaManager:
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def get_schema(
        self,
        name: str,
        prefer: str = "v2",
        fallback: str | None = "v1",
    ) -> dict[str, Any]:
        """
        Get schema by name with version negotiation.
        
        Tries preferred version first, falls back to fallback version if needed.
        Results are cached with TTL.
        
        Args:
            name: Schema name (e.g., "telemetry.FeedbackEvent")
            prefer: Preferred track version (default: v2)
            fallback: Fallback track version (default: v1)
        
        Returns:
            JSON Schema content
        
        Raises:
            SchemaNotFoundError: If schema not found in any track
            RuntimeError: If registry is disabled or client unavailable
        """
        if not self.enabled or not self._client:
            raise RuntimeError(
                "Schema registry is disabled or not initialized. "
                "Call start() first or enable registry."
            )
        
        # Check cache first
        cache_key = f"{name}:{prefer}:{fallback}"
        cached = await self._cache.get(cache_key)
        if cached:
            self._stats["cache_hits"] += 1
            if METRICS_AVAILABLE:
                SCHEMA_CACHE_HITS.labels(schema=name).inc()
            logger.debug(f"[registry] Cache hit: {name} (prefer={prefer})")
            return cached
        
        self._stats["cache_misses"] += 1
        if METRICS_AVAILABLE:
            SCHEMA_CACHE_MISSES.labels(schema=name).inc()
        
        try:
            # Negotiate with registry
            result = await self._client.negotiate(
                name=name,
                prefer=prefer,
                fallback=fallback,
            )
            
            # Fetch full schema content
            schema_response = await self._client.fetch_schema(
                track=result.track,
                name=name,
                version=result.core_version,
            )
            
            # Cache the content
            content = schema_response.content
            await self._cache.set(cache_key, content)
            
            logger.info(
                f"[registry] Fetched schema: {name} "
                f"(track={result.track}, version={result.core_version})"
            )
            
            return content
        
        except SchemaNotFoundError as e:
            self._stats["registry_errors"] += 1
            if METRICS_AVAILABLE:
                SCHEMA_REGISTRY_ERRORS.labels(schema=name, error_type="not_found").inc()
            logger.error(f"[registry] Schema not found: {name}")
            raise
        
        except Exception as e:
            self._stats["registry_errors"] += 1
            error_type = "timeout" if "timeout" in str(e).lower() else "network"
            if METRICS_AVAILABLE:
                SCHEMA_REGISTRY_ERRORS.labels(schema=name, error_type=error_type).inc()
            logger.error(f"[registry] Error fetching schema {name}: {e}")
            raise
    
    async def validate_payload(
        self,
        schema_name: str,
        payload: dict[str, Any],
        prefer: str = "v2",
        fallback: str | None = "v1",
    ) -> tuple[bool, list[str]]:
        """
        Validate payload against schema.
        
        Args:
            schema_name: Schema name to validate against
            payload: Payload dict to validate
            prefer: Preferred schema track
            fallback: Fallback schema track
        
        Returns:
            Tuple of (is_valid, error_messages)
        
        Example:
            is_valid, errors = await manager.validate_payload(
                "telemetry.FeedbackEvent",
                {"symbol": "AAPL", ...},
            )
            if not is_valid:
                logger.warning(f"Validation failed: {errors}")
        """
        if not self.enabled:
            # Graceful degradation: always return valid when disabled
            return True, []
        
        try:
            # Get schema from registry (cached)
            schema = await self.get_schema(schema_name, prefer=prefer, fallback=fallback)
            
            # Validate using jsonschema
            validator = Draft7Validator(schema)
            errors: list[ValidationError] = list(validator.iter_errors(payload))
            
            if errors:
                self._stats["validation_failure"] += 1
                if METRICS_AVAILABLE:
                    SCHEMA_VALIDATION_TOTAL.labels(schema=schema_name, outcome="failure").inc()
                    SCHEMA_VALIDATION_FAILURES.labels(schema=schema_name, mode=self.enforcement_mode).inc()
                
                error_messages = [
                    f"{e.json_path}: {e.message}" for e in errors
                ]
                
                # Phase 11.1: Enforcement mode handling
                if self.enforcement_mode == "strict":
                    # Strict mode: raise exception
                    self._stats["enforcement_rejections"] += 1
                    if METRICS_AVAILABLE:
                        SCHEMA_ENFORCEMENT_ACTIONS.labels(
                            schema=schema_name,
                            severity="error",
                            action="rejected"
                        ).inc()
                    
                    logger.error(
                        f"[registry] STRICT MODE: Validation failed for {schema_name}: {error_messages}"
                    )
                    raise SchemaValidationError(
                        f"Schema validation failed for {schema_name}",
                        schema_name=schema_name,
                        errors=error_messages,
                        track=prefer,
                        enforcement_mode="strict",
                    )
                else:
                    # Warn mode: log and continue
                    self._stats["enforcement_warnings"] += 1
                    if METRICS_AVAILABLE:
                        SCHEMA_ENFORCEMENT_ACTIONS.labels(
                            schema=schema_name,
                            severity="warn",
                            action="logged"
                        ).inc()
                    
                    logger.warning(
                        f"[registry] WARN MODE: Validation failed for {schema_name}: {error_messages}"
                    )
                    return False, error_messages
            
            self._stats["validation_success"] += 1
            if METRICS_AVAILABLE:
                SCHEMA_VALIDATION_TOTAL.labels(schema=schema_name, outcome="success").inc()
            return True, []
        
        except SchemaValidationError:
            # Re-raise validation errors from strict mode (don't catch our own exception)
            raise
        
        except Exception as e:
            # Don't fail validation on registry errors (graceful degradation)
            if METRICS_AVAILABLE:
                SCHEMA_VALIDATION_TOTAL.labels(schema=schema_name, outcome="error").inc()
            logger.warning(
                f"[registry] Validation error for {schema_name}: {e}. "
                "Treating as valid (graceful degradation)."
            )
            return True, []
    
    def get_stats(self) -> dict[str, Any]:
        """
        Get manager statistics.
        
        Returns:
            Dict with cache stats and validation metrics
        """
        return {
            **self._stats,
            "cache": self._cache.stats(),
            "enabled": self.enabled,
            "started": self._started,
        }
    
    async def clear_cache(self) -> None:
        """Clear schema cache (force refresh on next fetch)."""
        await self._cache.clear()
        logger.info("[registry] Schema cache cleared")

