"""Configuration management using Pydantic Settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class PipelineSettings(BaseSettings):
    """Pipeline configuration settings."""

    # Pipeline configuration
    batch_size: int = Field(default=500, description="Maximum batch size")
    flush_ms: int = Field(default=100, description="Flush interval in milliseconds")
    max_bytes: int = Field(default=512_000, description="Maximum batch size in bytes")

    # Queue configuration
    op_queue_max: int = Field(default=8, description="Maximum operator queue size")
    sink_queue_max: int = Field(default=16, description="Maximum sink queue size")

    # Drop policy
    drop_policy: str = Field(
        default="oldest", description="Drop policy: oldest or newest"
    )

    # Sink workers
    sink_workers: int = Field(default=2, description="Number of sink workers")

    # Pacing configuration
    pacing_max_per_sec: int = Field(
        default=1000, description="Maximum messages per second for pacing"
    )
    pacing_burst: int = Field(default=1000, description="Pacing burst capacity")
    
    # Source configuration
    ticks_per_sec: int = Field(default=100, description="Ticks per second for synthetic/IBKR sources")
    replay_path: Optional[str] = Field(default=None, description="Path to replay file")
    replay_speed: float = Field(default=1.0, description="Replay speed multiplier (1.0 = realtime)")
    
    # Operator configuration
    bar_window_sec: int = Field(default=1, description="Bar aggregation window in seconds")
    bar_allowed_lateness_sec: int = Field(default=0, description="Allowed lateness for bar aggregation")

    # Telemetry configuration
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    enable_tracing: bool = Field(
        default=False, description="Enable OpenTelemetry tracing"
    )
    telemetry_enabled: bool = Field(default=True, description="Enable telemetry (CORE compatibility)")
    metrics_port: int = Field(default=8080, description="Metrics server port")

    # Logging configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")

    # Database configuration
    database_url: Optional[str] = Field(
        default=None, description="Database connection URL"
    )
    database_pool_size: int = Field(
        default=10, description="Database connection pool size"
    )
    database_vendor: str = Field(
        default="market_data_pipeline", description="Database vendor identifier"
    )
    database_timeframe: str = Field(
        default="1s", description="Database timeframe setting"
    )
    database_retry_max_attempts: int = Field(
        default=5, description="Database retry max attempts"
    )
    database_retry_backoff_ms: int = Field(
        default=50, description="Database retry backoff in milliseconds"
    )

    # Kafka configuration (for KafkaSink)
    kafka_bootstrap_servers: Optional[str] = Field(
        default=None, description="Kafka bootstrap servers"
    )
    kafka_topic: Optional[str] = Field(default=None, description="Kafka topic name")

    # IBKR configuration
    ibkr_host: Optional[str] = Field(default=None, description="IBKR TWS/Gateway host")
    ibkr_port: int = Field(default=7497, description="IBKR TWS/Gateway port")
    ibkr_client_id: int = Field(default=1, description="IBKR client ID")

    class Config:
        env_prefix = "PIPELINE_"
        case_sensitive = False

    @validator("drop_policy")
    def validate_drop_policy(cls, v: str) -> str:
        """Validate drop policy."""
        if v not in ["oldest", "newest"]:
            raise ValueError("drop_policy must be 'oldest' or 'newest'")
        return v

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()

    @validator("log_format")
    def validate_log_format(cls, v: str) -> str:
        """Validate log format."""
        if v not in ["json", "text"]:
            raise ValueError("log_format must be 'json' or 'text'")
        return v


def load_config(config_file: Optional[str] = None) -> PipelineSettings:
    """Load configuration from file and environment variables."""
    settings = PipelineSettings()

    if config_file:
        config_path = Path(config_file)
        if config_path.exists():
            # Load from YAML file if it exists
            import yaml

            with open(config_path, "r") as f:
                config_data = yaml.safe_load(f)
                if config_data:
                    # Update settings with file values
                    for key, value in config_data.items():
                        if hasattr(settings, key):
                            setattr(settings, key, value)

    return settings


def get_config() -> PipelineSettings:
    """Get the current configuration."""
    return load_config()


def get_pipeline_config() -> PipelineSettings:
    """Get the pipeline configuration (alias for get_config for compatibility)."""
    return get_config()


# Global configuration instance
_config: Optional[PipelineSettings] = None


def get_global_config() -> PipelineSettings:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = get_config()
    return _config


def set_global_config(config: PipelineSettings) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config
