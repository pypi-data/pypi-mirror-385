"""Pulse configuration (Phase 10.1)."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PulseConfig:
    """
    Pulse event bus configuration.
    
    Environment Variables:
        PULSE_ENABLED: Enable Pulse integration (default: true)
        EVENT_BUS_BACKEND: Backend type (inmem|redis, default: inmem)
        REDIS_URL: Redis connection string (default: redis://localhost:6379/0)
        MD_NAMESPACE: Namespace prefix for streams (default: mdp)
        SCHEMA_TRACK: Schema track (v1|v2, default: v1)
        PUBLISHER_TOKEN: Optional auth token for publishers
    
    Example:
        cfg = PulseConfig()
        if cfg.enabled:
            bus = create_event_bus(backend=cfg.backend, redis_url=cfg.redis_url)
    """
    
    enabled: bool = os.getenv("PULSE_ENABLED", "true").lower() == "true"
    backend: str = os.getenv("EVENT_BUS_BACKEND", "inmem")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ns: str = os.getenv("MD_NAMESPACE", "mdp")
    track: str = os.getenv("SCHEMA_TRACK", "v1")
    publisher_token: str = os.getenv("PUBLISHER_TOKEN", "unset")

