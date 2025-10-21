"""Pipeline context for tenancy and configuration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class PipelineContext:
    """Pipeline execution context with tenant and pipeline identification."""

    tenant_id: str
    pipeline_id: str
    labels: Optional[Dict[str, str]] = None

    def get_idempotency_key(self, symbol: str, window_ts: str) -> str:
        """Generate deterministic idempotency key for batch writes."""
        return f"{self.tenant_id}:{self.pipeline_id}:{symbol}:{window_ts}"
