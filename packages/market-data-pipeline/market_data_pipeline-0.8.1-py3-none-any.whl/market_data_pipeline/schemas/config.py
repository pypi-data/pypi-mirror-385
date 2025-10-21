"""Schema registry configuration (Phase 11.0B + 11.1)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RegistryConfig:
    """
    Schema Registry configuration.
    
    Environment Variables:
        REGISTRY_ENABLED: Enable registry integration (default: false)
        REGISTRY_URL: Registry service base URL (required if enabled)
        REGISTRY_TOKEN: Optional admin token for write operations
        REGISTRY_CACHE_TTL: Cache TTL in seconds (default: 300)
        REGISTRY_TIMEOUT: Request timeout in seconds (default: 30.0)
        SCHEMA_PREFER_TRACK: Preferred schema track (default: v2)
        SCHEMA_FALLBACK_TRACK: Fallback schema track (default: v1)
        REGISTRY_ENFORCEMENT: Enforcement mode (warn|strict, default: warn)
    
    Enforcement Modes (Phase 11.1):
        - warn: Log validation failures, continue processing
        - strict: Raise SchemaValidationError on validation failures
    
    Example:
        cfg = RegistryConfig()
        if cfg.enabled:
            manager = SchemaManager(
                registry_url=cfg.url,
                token=cfg.token,
                cache_ttl=cfg.cache_ttl,
                enforcement_mode=cfg.enforcement_mode,
            )
            await manager.start()
    """
    
    enabled: bool = os.getenv("REGISTRY_ENABLED", "false").lower() == "true"
    url: str = os.getenv("REGISTRY_URL", "https://registry.openbb.co/api/v1")
    token: str | None = os.getenv("REGISTRY_TOKEN")
    cache_ttl: int = int(os.getenv("REGISTRY_CACHE_TTL", "300"))
    timeout: float = float(os.getenv("REGISTRY_TIMEOUT", "30.0"))
    prefer_track: str = os.getenv("SCHEMA_PREFER_TRACK", "v2")
    fallback_track: str | None = os.getenv("SCHEMA_FALLBACK_TRACK", "v1")
    enforcement_mode: str = os.getenv("REGISTRY_ENFORCEMENT", "warn")
    poll_seconds: int = int(os.getenv("REGISTRY_POLL_SECONDS", "60"))
    
    def validate(self) -> None:
        """
        Validate configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        if self.enabled and not self.url:
            raise ValueError("REGISTRY_URL must be set when REGISTRY_ENABLED=true")
        
        if self.cache_ttl < 0:
            raise ValueError("REGISTRY_CACHE_TTL must be >= 0")
        
        if self.timeout <= 0:
            raise ValueError("REGISTRY_TIMEOUT must be > 0")
        
        if self.enforcement_mode not in ("warn", "strict"):
            raise ValueError("REGISTRY_ENFORCEMENT must be 'warn' or 'strict'")

