import asyncio
import pytest

from market_data_pipeline.orchestration.dag import (
    PartitioningSpec,
    hash_partition,
)

@pytest.mark.asyncio
async def test_hash_partition_fanout_and_streaming():
    src_items = [{"sym": "AAPL", "x": i} for i in range(20)] + [{"sym": "MSFT", "x": i} for i in range(20)]

    async def _src():
        for it in src_items:
            await asyncio.sleep(0)
            yield it

    parts = await hash_partition(
        _src().__aiter__(),
        get_key=lambda x: x["sym"],
        spec=PartitioningSpec(partitions=4, capacity=64),
    )

    # pull from all partitions and count
    counts = [0, 0, 0, 0]

    async def _drain(idx: int):
        async for _ in parts.stream_partition(idx):
            counts[idx] += 1

    tasks = [asyncio.create_task(_drain(i)) for i in range(parts.partitions())]
    await asyncio.gather(*tasks)

    assert sum(counts) == len(src_items)
    # at least two partitions should be non-empty given 2 keys and 4 parts
    assert len([c for c in counts if c > 0]) >= 2

