import asyncio
import pytest

from market_data_pipeline.orchestration.dag.channel import Channel


@pytest.mark.asyncio
async def test_channel_throughput_baseline():
    """
    Baseline throughput test for Channel without pytest-benchmark.
    Measures sustained message rate through a bounded channel.
    """
    ch = Channel[int](capacity=4096)
    n = 5000

    async def producer():
        for i in range(n):
            await ch.put(i)
        await ch.close()

    async def consumer():
        count = 0
        try:
            while True:
                await ch.get()
                count += 1
        except Exception:
            return count

    import time
    t0 = time.perf_counter()
    
    prod = asyncio.create_task(producer())
    cons = asyncio.create_task(consumer())
    await asyncio.gather(prod, cons)
    
    t1 = time.perf_counter()
    duration = t1 - t0
    
    throughput = n / duration
    print(f"\n  Channel throughput: {throughput:,.0f} msgs/sec")
    print(f"  Duration: {duration:.3f}s")
    
    # Basic assertion - should handle at least 10k msgs/sec
    assert throughput > 10000, f"Throughput too low: {throughput:,.0f} msgs/sec"

