import asyncio
from datetime import datetime, timedelta, timezone
from market_data_pipeline.orchestration.dag import (
    TumblingWindowSpec,
    WatermarkPolicy,
    tumbling_window_event_time,
    hash_partition,
    PartitioningSpec,
)

UTC = timezone.utc

async def main():
    base = datetime.now(tz=UTC)

    async def _ticks():
        # interleaving two symbols with slight disorder
        ts = [
            {"sym": "AAPL", "t": base + timedelta(seconds=0), "px": 190.1},
            {"sym": "MSFT", "t": base + timedelta(seconds=1), "px": 401.0},
            {"sym": "AAPL", "t": base + timedelta(seconds=2), "px": 190.2},
            {"sym": "AAPL", "t": base + timedelta(seconds=1, milliseconds=200), "px": 190.15},  # late but within lag
            {"sym": "MSFT", "t": base + timedelta(seconds=6), "px": 402.0},
        ]
        for x in ts:
            await asyncio.sleep(0.01)
            yield x

    # Partition by symbol
    parts = await hash_partition(
        _ticks().__aiter__(),
        get_key=lambda x: x["sym"],
        spec=PartitioningSpec(partitions=2),
    )

    # Build windowed processors per partition
    async def _consume_partition(idx: int):
        spec = TumblingWindowSpec(size=timedelta(seconds=5))
        policy = WatermarkPolicy(lag=timedelta(seconds=1))
        async for frame in tumbling_window_event_time(
            parts.stream_partition(idx),
            spec,
            get_event_time=lambda x: x["t"],
            watermark_policy=policy,
        ):
            print(f"[p={idx}] window {frame.start.time()}..{frame.end.time()} count={len(frame.items)}")

    tasks = [asyncio.create_task(_consume_partition(i)) for i in range(parts.partitions())]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

