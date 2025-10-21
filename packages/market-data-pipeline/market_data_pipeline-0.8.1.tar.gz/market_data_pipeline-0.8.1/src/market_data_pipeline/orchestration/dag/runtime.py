from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from .channel import Channel, Watermark
from .graph import Dag


@dataclass(frozen=True)
class RunConfig:
    channel_capacity: int = 2048
    high_watermark_pct: float = 0.75
    low_watermark_pct: float = 0.25
    max_concurrency: int = 64  # cap on tasks for safety


@dataclass
class DagRunStats:
    tasks_started: int = 0
    tasks_completed: int = 0
    cancelled: bool = False


class DagRuntime:
    """
    Executes a DAG where each node function has signature:
        async fn(in_channels: dict[str, Channel], out_channels: dict[str, Channel]) -> None

    A node can be:
      - Source: no inbound edges → writes to its out_channels
      - Operator: reads from its in_channels, writes to out_channels
      - Sink: reads from in_channels, closes on upstream close
    """
    def __init__(self, dag: Dag, config: RunConfig | None = None) -> None:
        dag.validate()
        self._dag = dag
        self._cfg = config or RunConfig()
        self._tasks: list[asyncio.Task] = []
        self._stats = DagRunStats()
        self._channels: dict[tuple[str, str], Channel] = {}  # (src, dst) -> channel
        self._stop_evt = asyncio.Event()

    def _mk_watermark(self) -> Watermark:
        cap = self._cfg.channel_capacity
        return Watermark(
            high=max(1, int(cap * self._cfg.high_watermark_pct)),
            low=max(1, int(cap * self._cfg.low_watermark_pct)),
        )

    async def _on_high(self) -> None:
        # hook for global backpressure signal (extend in Phase 5.0.7)
        return

    async def _on_low(self) -> None:
        # hook for global recovery signal
        return

    def _wire_channels(self) -> dict[str, dict[str, Channel]]:
        """
        Returns node_name -> {"in": Channel, "out": Dict[dst, Channel]} map.
        For fan-out, each edge has its own channel.
        """
        wm = self._mk_watermark()
        # create channel per edge
        for e in self._dag.edges:
            self._channels[(e.src, e.dst)] = Channel(
                capacity=self._cfg.channel_capacity,
                watermark=wm,
                on_high=self._on_high,
                on_low=self._on_low,
            )
        # build node IO mapping
        io: dict[str, dict[str, Any]] = {}
        for name in self._dag.nodes:
            outs: dict[str, Channel] = {}
            ins: dict[str, Channel] = {}
            for (src, dst), ch in self._channels.items():
                if src == name:
                    outs[dst] = ch
                if dst == name:
                    ins[src] = ch
            io[name] = {"in": ins, "out": outs}
        return io  # type: ignore[return-value]

    async def _run_node(self, name: str, fn: Callable[..., Awaitable[None]], in_ch: dict[str, Channel], out_ch: dict[str, Channel]) -> None:
        try:
            await fn(in_ch, out_ch)
        finally:
            # close all downstream channels initiated by this node (signals completion)
            for ch in out_ch.values():
                await ch.close()

    async def start(self) -> DagRunStats:
        if self._tasks:
            return self._stats  # already started
        io_map = self._wire_channels()

        for name, node in self._dag.nodes.items():
            if len(self._tasks) >= self._cfg.max_concurrency:
                raise RuntimeError("Exceeded max_concurrency for DAG tasks")
            task = asyncio.create_task(
                self._run_node(name, node.fn, io_map[name]["in"], io_map[name]["out"]),
                name=f"dag-node:{name}",
            )
            self._tasks.append(task)
            self._stats.tasks_started += 1

        # wait for completion or cancellation
        try:
            results = await asyncio.gather(*self._tasks, return_exceptions=True)
            # count completions (ignore ChannelClosed propagation and cancellations handled below)
            for r in results:
                if not isinstance(r, Exception):
                    self._stats.tasks_completed += 1
        except asyncio.CancelledError:
            self._stats.cancelled = True
            raise
        finally:
            # ensure channels closed
            for ch in self._channels.values():
                await ch.close()
        return self._stats

    async def stop(self) -> None:
        if not self._tasks:
            return
        self._stats.cancelled = True
        for t in self._tasks:
            t.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        for ch in self._channels.values():
            await ch.close()

