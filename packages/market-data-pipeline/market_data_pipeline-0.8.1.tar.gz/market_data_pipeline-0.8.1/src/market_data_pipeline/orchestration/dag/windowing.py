from __future__ import annotations

import asyncio
import contextlib
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Deque,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
)

T = TypeVar("T")
K = TypeVar("K")
U = TypeVar("U")

UTC = timezone.utc


@dataclass(frozen=True)
class WatermarkPolicy:
    """
    Event-time watermark configuration.

    - lag: watermark = max_event_time - lag
    - allowed_lateness: items with event_time <= watermark - allowed_lateness are dropped
    """
    lag: timedelta = timedelta(seconds=5)
    allowed_lateness: timedelta = timedelta(seconds=0)


class EventTimeClock(Generic[T]):
    """
    Maintains event-time watermark per key and globally.
    """

    def __init__(
        self,
        get_event_time: Callable[[T], datetime],
        policy: WatermarkPolicy,
        get_key: Optional[Callable[[T], K]] = None,
    ) -> None:
        self._get_event_time = get_event_time
        self._policy = policy
        self._get_key = get_key
        self._max_event_time_global: Optional[datetime] = None
        self._max_event_time_per_key: Dict[K, datetime] = {}

    def observe(self, item: T) -> None:
        et = self._norm(self._get_event_time(item))
        if self._max_event_time_global is None or et > self._max_event_time_global:
            self._max_event_time_global = et

        if self._get_key is not None:
            key = self._get_key(item)  # type: ignore[call-arg]
            prev = self._max_event_time_per_key.get(key)
            if prev is None or et > prev:
                self._max_event_time_per_key[key] = et

    def watermark(self, key: Optional[K] = None) -> Optional[datetime]:
        """
        Returns watermark for given key if tracked, otherwise global watermark.
        watermark = max_event_time - lag
        """
        max_et: Optional[datetime]
        if key is not None and key in self._max_event_time_per_key:
            max_et = self._max_event_time_per_key[key]
        else:
            max_et = self._max_event_time_global

        if max_et is None:
            return None
        return self._norm(max_et - self._policy.lag)

    def is_late(self, item: T, key: Optional[K] = None) -> bool:
        """
        Returns True if item is beyond allowed_lateness versus watermark.
        """
        wm = self.watermark(key)
        if wm is None:
            return False
        threshold = wm - self._policy.allowed_lateness
        return self._norm(self._get_event_time(item)) <= threshold

    @staticmethod
    def _norm(dt: datetime) -> datetime:
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


@dataclass(frozen=True)
class TumblingWindowSpec:
    size: timedelta
    # emit_partial: if True, will emit current incomplete window on flush/end
    emit_partial: bool = False


@dataclass(frozen=True)
class WindowFrame(Generic[K, T]):
    key: Optional[K]
    start: datetime
    end: datetime
    items: Tuple[T, ...]


def _floor_to(dt: datetime, size: timedelta) -> datetime:
    dt = dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    epoch = datetime(1970, 1, 1, tzinfo=UTC)
    delta = dt - epoch
    bucket = (delta // size) * size
    return epoch + bucket


async def tumbling_window_event_time(
    source: AsyncIterator[T],
    spec: TumblingWindowSpec,
    *,
    get_event_time: Callable[[T], datetime],
    get_key: Optional[Callable[[T], K]] = None,
    watermark_policy: Optional[WatermarkPolicy] = None,
    flush_interval: float = 0.250,
) -> AsyncIterator[WindowFrame[K, T]]:
    """
    Event-time tumbling windows with watermarks and allowed lateness.

    - Windows are aligned to multiples of `spec.size` from epoch.
    - Watermark = max_event_time - policy.lag
    - Late data beyond allowed_lateness is dropped.
    - Within-lateness items are added to still-open windows (by watermark).
    """
    wm_policy = watermark_policy or WatermarkPolicy()
    clock = EventTimeClock(get_event_time=get_event_time, policy=wm_policy, get_key=get_key)

    # per-key window buffers: key -> {(window_start): deque}
    buffers: Dict[Optional[K], Dict[datetime, Deque[T]]] = defaultdict(lambda: defaultdict(deque))
    # track the latest window start observed per key (to accelerate close)
    open_windows: Dict[Optional[K], set[datetime]] = defaultdict(set)

    async def _emit_ready(now_wm: Optional[datetime]) -> List[WindowFrame[K, T]]:
        if now_wm is None:
            return []
        emitted: List[WindowFrame[K, T]] = []
        keys = list(buffers.keys())
        for k in keys:
            starts = list(open_windows[k])
            for start in starts:
                end = start + spec.size
                # A window is "ready" to emit when watermark has passed its end.
                if end <= now_wm:
                    dq = buffers[k].pop(start, deque())
                    if start in open_windows[k]:
                        open_windows[k].remove(start)
                    if dq or spec.emit_partial:
                        emitted.append(
                            WindowFrame(
                                key=k,
                                start=start,
                                end=end,
                                items=tuple(dq),
                            )
                        )
        return emitted

    async def _flush_remaining() -> List[WindowFrame[K, T]]:
        emitted: List[WindowFrame[K, T]] = []
        for k, wins in buffers.items():
            for start, dq in list(wins.items()):
                if dq or spec.emit_partial:
                    emitted.append(
                        WindowFrame(
                            key=k,
                            start=start,
                            end=start + spec.size,
                            items=tuple(dq),
                        )
                    )
        buffers.clear()
        open_windows.clear()
        return emitted

    async def _ticker(stop_evt: asyncio.Event, q: asyncio.Queue) -> None:
        try:
            while not stop_evt.is_set():
                await asyncio.sleep(flush_interval)
                await q.put(None)  # signal tick
        except asyncio.CancelledError:
            pass

    tick_q: asyncio.Queue = asyncio.Queue(maxsize=16)
    stop_evt = asyncio.Event()
    tick_task = asyncio.create_task(_ticker(stop_evt, tick_q))

    try:
        src_iter = source.__aiter__()
        pending_src = asyncio.create_task(src_iter.__anext__())
        pending_tick = asyncio.create_task(tick_q.get())

        while True:
            done, _ = await asyncio.wait(
                {pending_src, pending_tick},
                return_when=asyncio.FIRST_COMPLETED,
            )

            if pending_src in done:
                try:
                    item = pending_src.result()
                except StopAsyncIteration:
                    # Source ended: flush remaining windows
                    for frame in await _flush_remaining():
                        yield frame
                    break

                # Observe clock & route item
                clock.observe(item)
                k: Optional[K] = get_key(item) if get_key else None
                if clock.is_late(item, k):
                    # Drop too-late item
                    pending_src = asyncio.create_task(src_iter.__anext__())
                    continue

                et = EventTimeClock._norm(get_event_time(item))
                start = _floor_to(et, spec.size)
                buffers[k][start].append(item)
                open_windows[k].add(start)

                # Try emit by watermark
                for frame in await _emit_ready(clock.watermark(k)):
                    yield frame

                # re-arm src
                pending_src = asyncio.create_task(src_iter.__anext__())

            if pending_tick in done:
                try:
                    pending_tick.result()
                except Exception:
                    pass
                # global watermark flush
                for frame in await _emit_ready(clock.watermark(None)):
                    yield frame
                # re-arm tick
                pending_tick = asyncio.create_task(tick_q.get())

    finally:
        stop_evt.set()
        tick_task.cancel()
        with contextlib.suppress(Exception):
            await tick_task

