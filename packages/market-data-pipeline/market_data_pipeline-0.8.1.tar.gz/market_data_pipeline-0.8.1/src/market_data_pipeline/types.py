"""Shared DTOs and type definitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel


@dataclass(frozen=True)
class Quote:
    """Market data quote/tick."""

    symbol: str
    timestamp: datetime
    price: Decimal
    size: Decimal
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    bid_size: Optional[Decimal] = None
    ask_size: Optional[Decimal] = None
    source: str = "unknown"
    metadata: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class Bar:
    """Aggregated bar data (OHLCV)."""

    symbol: str
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    vwap: Optional[Decimal] = None
    trade_count: Optional[int] = None
    source: str = "unknown"
    metadata: Optional[Dict[str, Any]] = None


class PipelineConfig(BaseModel):
    """Pipeline configuration."""

    # Batching configuration
    batch_size: int = 500
    flush_ms: int = 100
    max_bytes: int = 512_000

    # Queue configuration
    op_queue_max: int = 8
    sink_queue_max: int = 16

    # Drop policy
    drop_policy: str = "oldest"  # "oldest" or "newest"

    # Sink workers
    sink_workers: int = 2

    # Pacing configuration
    pacing_budget_max_msgs_per_sec: int = 1000
    pacing_budget_burst: int = 1000

    # Telemetry
    enable_metrics: bool = True
    enable_tracing: bool = False
    metrics_port: int = 8080

    class Config:
        env_prefix = "PIPELINE_"
