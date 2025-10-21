from __future__ import annotations

import asyncio
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from loguru import logger

from .dag.channel import Channel, ChannelClosed
from .dag.graph import Dag
from .dag.runtime import DagRuntime
from .dag.runtime import RunConfig as DagRunConfig

# Classic service remains available; we import lazily to avoid hard coupling.
# from ..runners.service import PipelineService


@dataclass
class OrchestratorSettings:
    mode: Literal["classic", "dag"] = "dag"
    # dag-specific
    channel_capacity: int = 2048
    high_watermark_pct: float = 0.75
    low_watermark_pct: float = 0.25
    max_concurrency: int = 64


class RuntimeOrchestrator:
    """
    Unified entrypoint façade.
    mode="classic" → defers to PipelineService (unchanged).
    mode="dag" → runs DagRuntime.
    Phase 5.0.4: adds provider integration helpers.
    """
    def __init__(self, settings: OrchestratorSettings | None = None) -> None:
        self.settings = settings or OrchestratorSettings()
        self._dag_runtime: DagRuntime | None = None
        # self._classic: Optional[PipelineService] = None
        
        # Phase 5.0.4: Provider registry (lazy import)
        self._registry = None

    def _get_registry(self):
        """Lazy load provider registry to avoid import errors if not used."""
        if self._registry is None:
            try:
                from ..adapters.providers import ProviderRegistry
                self._registry = ProviderRegistry()
            except ImportError as e:
                msg = "Provider adapters not available. Install market-data-ibkr to use provider integration."
                raise ImportError(msg) from e
        return self._registry

    async def run_dag(self, dag: Dag) -> None:
        cfg = DagRunConfig(
            channel_capacity=self.settings.channel_capacity,
            high_watermark_pct=self.settings.high_watermark_pct,
            low_watermark_pct=self.settings.low_watermark_pct,
            max_concurrency=self.settings.max_concurrency,
        )
        self._dag_runtime = DagRuntime(dag, cfg)
        await self._dag_runtime.start()

    async def stop(self) -> None:
        if self._dag_runtime:
            await self._dag_runtime.stop()
        # if self._classic:
        #     await self._classic.stop()

    # ── Phase 5.0.4: Provider integration helpers ──

    async def quotes_to_channel(
        self, symbols: Iterable[str], max_buffer: int = 2048
    ) -> Channel:
        """
        Spin up an IBKR quotes provider and pump into a Channel.
        Returns the channel for downstream consumption.
        """
        registry = self._get_registry()
        src = registry.build("ibkr", symbols=list(symbols), mode="quotes")
        await src.start()
        ch = Channel(capacity=max_buffer)
        
        async def pump():
            try:
                async for item in src.stream():
                    await ch.put(item)
            except ChannelClosed:
                pass
            finally:
                await ch.close()
                await src.stop()
        
        # Fire and forget pump task
        asyncio.create_task(pump())
        logger.info(f"quotes_to_channel: pump started for symbols={list(symbols)}")
        return ch

    async def bars_to_channel(
        self, symbols: Iterable[str], resolution: str = "5s", max_buffer: int = 2048
    ) -> Channel:
        """
        Spin up an IBKR bars provider and pump into a Channel.
        Returns the channel for downstream consumption.
        """
        registry = self._get_registry()
        src = registry.build(
            "ibkr", symbols=list(symbols), mode="bars", bar_resolution=resolution
        )
        await src.start()
        ch = Channel(capacity=max_buffer)
        
        async def pump():
            try:
                async for item in src.stream():
                    await ch.put(item)
            except ChannelClosed:
                pass
            finally:
                await ch.close()
                await src.stop()
        
        # Fire and forget pump task
        asyncio.create_task(pump())
        logger.info(f"bars_to_channel: pump started for symbols={list(symbols)} resolution={resolution}")
        return ch

