from __future__ import annotations

from typing import Literal

from pydantic import BaseSettings, Field


class RuntimeSettings(BaseSettings):
    """Env-configurable settings for RuntimeOrchestrator."""
    mode: Literal["classic", "dag"] = Field(default="dag", description="Runtime mode")
    channel_capacity: int = Field(default=2048, ge=1)
    high_watermark_pct: float = Field(default=0.75, ge=0.05, le=0.95)
    low_watermark_pct: float = Field(default=0.25, ge=0.01, le=0.9)
    max_concurrency: int = Field(default=64, ge=1, le=512)

    class Config:
        env_prefix = "MDP_"
        env_file = ".env"

