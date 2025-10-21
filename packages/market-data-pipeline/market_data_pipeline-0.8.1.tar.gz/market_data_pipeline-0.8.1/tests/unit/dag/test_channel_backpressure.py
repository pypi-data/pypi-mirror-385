import asyncio
import pytest
from market_data_pipeline.orchestration.dag.channel import Channel, Watermark


@pytest.mark.asyncio
async def test_channel_watermarks_fire_once_then_recover():
    highs = 0
    lows = 0

    async def on_high():
        nonlocal highs
        highs += 1

    async def on_low():
        nonlocal lows
        lows += 1

    ch = Channel[int](capacity=10, watermark=Watermark(high=7, low=3), on_high=on_high, on_low=on_low)

    # Fill to > high
    for i in range(8):
        await ch.put(i)

    await asyncio.sleep(0.05)  # let callbacks schedule
    assert highs == 1

    # Drain below low
    for _ in range(6):
        _ = await ch.get()

    await asyncio.sleep(0.05)
    assert lows == 1

    # Hit high again → should trigger another high
    for i in range(7):
        await ch.put(i)

    await asyncio.sleep(0.05)
    assert highs == 2


@pytest.mark.asyncio
async def test_channel_close_semantics():
    ch = Channel[int](capacity=2)
    await ch.put(1)
    await ch.put(2)
    await ch.close()

    assert await ch.get() == 1
    assert await ch.get() == 2
    with pytest.raises(Exception):
        await ch.get()

