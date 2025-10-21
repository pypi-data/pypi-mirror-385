from __future__ import annotations

import asyncio
from collections import deque
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta
from typing import Any

from .channel import Channel, ChannelClosed


# Operator: map
async def map_async(
    src: Channel,
    dst: Channel,
    fn: Callable[[Any], Awaitable[Any]] | Callable[[Any], Any],
) -> None:
    try:
        while True:
            item = await src.get()
            res = fn(item)
            if asyncio.iscoroutine(res):
                res = await res  # type: ignore[assignment]
            await dst.put(res)
    except ChannelClosed:
        await dst.close()


# Operator: filter
async def filter_async(
    src: Channel,
    dst: Channel,
    predicate: Callable[[Any], bool] | Callable[[Any], Awaitable[bool]],
) -> None:
    try:
        while True:
            item = await src.get()
            ok = predicate(item)
            if asyncio.iscoroutine(ok):
                ok = await ok  # type: ignore[assignment]
            if ok:
                await dst.put(item)
    except ChannelClosed:
        await dst.close()


# Operator: buffer (simple micro-batching by count or time)
async def buffer_async(
    src: Channel,
    dst: Channel,
    *,
    max_items: int = 500,
    flush_interval: float = 0.25,  # seconds
) -> None:
    buf: deque[Any] = deque()
    last_flush = asyncio.get_event_loop().time()
    try:
        while True:
            timeout = max(0.0, flush_interval - (asyncio.get_event_loop().time() - last_flush))
            try:
                item = await asyncio.wait_for(src.get(), timeout=timeout)
                buf.append(item)
                if len(buf) >= max_items:
                    await dst.put(list(buf))
                    buf.clear()
                    last_flush = asyncio.get_event_loop().time()
            except TimeoutError:
                if buf:
                    await dst.put(list(buf))
                    buf.clear()
                last_flush = asyncio.get_event_loop().time()
    except ChannelClosed:
        if buf:
            await dst.put(list(buf))
        await dst.close()


# Operator: tumbling window (event-time or process-time)
async def tumbling_window(
    src: Channel,
    dst: Channel,
    *,
    window: timedelta,
    timestamp_fn: Callable[[Any], datetime] | None = None,
) -> None:
    """
    Groups items into fixed-size, non-overlapping windows.
    If timestamp_fn is None, uses process-time (arrival time).
    Emits list[item] per window close.
    """
    bucket: list[Any] = []
    window_start = datetime.utcnow()
    try:
        while True:
            item = await src.get()
            now_ts = timestamp_fn(item) if timestamp_fn else datetime.utcnow()
            if now_ts - window_start >= window:
                if bucket:
                    await dst.put(bucket)
                bucket = [item]
                window_start = now_ts
            else:
                bucket.append(item)
    except ChannelClosed:
        if bucket:
            await dst.put(bucket)
        await dst.close()

