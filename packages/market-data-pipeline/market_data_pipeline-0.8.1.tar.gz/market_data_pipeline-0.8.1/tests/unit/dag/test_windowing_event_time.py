import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from market_data_pipeline.orchestration.dag import (
    TumblingWindowSpec,
    WatermarkPolicy,
    tumbling_window_event_time,
)

UTC = timezone.utc

@pytest.mark.asyncio
async def test_tumbling_window_with_watermark_and_lateness():
    # Build a tiny out-of-order stream
    base = datetime(2024, 1, 1, 9, 30, tzinfo=UTC)
    items = [
        {"t": base + timedelta(seconds=0), "v": 1},
        {"t": base + timedelta(seconds=2), "v": 2},
        {"t": base + timedelta(seconds=1), "v": 3},  # out-of-order (late but within lag)
        {"t": base + timedelta(seconds=6), "v": 4},  # next window
    ]

    async def _src():
        for it in items:
            await asyncio.sleep(0)  # yield to loop
            yield it

    spec = TumblingWindowSpec(size=timedelta(seconds=5), emit_partial=False)
    policy = WatermarkPolicy(lag=timedelta(seconds=2), allowed_lateness=timedelta(seconds=0))

    frames = []
    async for frame in tumbling_window_event_time(
        _src().__aiter__(),
        spec,
        get_event_time=lambda x: x["t"],
        watermark_policy=policy,
        flush_interval=0.05,
    ):
        frames.append(frame)

    # We expect two frames: [0..5), [5..10)
    assert len(frames) == 2
    first, second = frames[0], frames[1]
    assert first.start.minute == 30
    assert len(first.items) == 3  # 0s, 1s, 2s all landed before watermark passed 5s
    assert second.start.minute == 30
    assert second.start.second == 5
    assert len(second.items) == 1

