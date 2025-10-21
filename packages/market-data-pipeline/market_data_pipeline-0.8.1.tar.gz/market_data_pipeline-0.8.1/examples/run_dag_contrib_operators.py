"""
Phase 5.0.3 — Contrib Operators Example

Demonstrates OHLC resampling, deduplication, and throttling.
"""
import asyncio
from datetime import datetime, timedelta, timezone

from market_data_pipeline.orchestration.dag import (
    Bar,
    deduplicate,
    resample_ohlc,
    throttle,
)

UTC = timezone.utc


async def generate_ticks(symbol: str, count: int = 20):
    """Generate synthetic tick data."""
    base = datetime.now(UTC)
    for i in range(count):
        yield {
            "sym": symbol,
            "t": base + timedelta(seconds=i),
            "px": 100.0 + (i % 5),  # Price oscillates
        }
        await asyncio.sleep(0.05)


async def demo_ohlc_resample():
    """Demo: Resample ticks into 5-second OHLC bars."""
    print("\n=== OHLC Resample Demo ===")
    
    bars = []
    async for bar in resample_ohlc(
        generate_ticks("AAPL", count=15).__aiter__(),
        get_symbol=lambda x: x["sym"],
        get_price=lambda x: x["px"],
        get_time=lambda x: x["t"],
        window=timedelta(seconds=5),
        watermark_lag=timedelta(seconds=1),
    ):
        bars.append(bar)
        print(f"  {bar.symbol} [{bar.start.strftime('%H:%M:%S')} - {bar.end.strftime('%H:%M:%S')}]: "
              f"O={bar.open:.2f} H={bar.high:.2f} L={bar.low:.2f} C={bar.close:.2f} Count={bar.count}")
    
    print(f"  → Generated {len(bars)} bar(s)")


async def demo_deduplicate():
    """Demo: Remove duplicate ticks."""
    print("\n=== Deduplicate Demo ===")
    
    async def ticks_with_dupes():
        items = [
            {"sym": "AAPL", "px": 100.0},
            {"sym": "AAPL", "px": 100.0},  # duplicate
            {"sym": "AAPL", "px": 101.0},  # new
            {"sym": "AAPL", "px": 101.0},  # duplicate
            {"sym": "AAPL", "px": 102.0},  # new
        ]
        for it in items:
            await asyncio.sleep(0.01)
            yield it
    
    unique = []
    async for tick in deduplicate(
        ticks_with_dupes().__aiter__(),
        key_fn=lambda x: (x["sym"], x["px"]),
        ttl=5.0,
    ):
        unique.append(tick)
        print(f"  {tick['sym']}: ${tick['px']:.2f}")
    
    print(f"  → Kept {len(unique)}/5 ticks (removed {5 - len(unique)} duplicates)")


async def demo_throttle():
    """Demo: Throttle message rate."""
    print("\n=== Throttle Demo ===")
    
    async def fast_stream():
        for i in range(10):
            yield {"n": i}
    
    t0 = asyncio.get_event_loop().time()
    count = 0
    
    async for item in throttle(fast_stream().__aiter__(), rate_limit=5):
        count += 1
        elapsed = asyncio.get_event_loop().time() - t0
        print(f"  Item {item['n']} @ {elapsed:.2f}s")
    
    t1 = asyncio.get_event_loop().time()
    duration = t1 - t0
    actual_rate = count / duration
    
    print(f"  → Processed {count} items in {duration:.2f}s (rate: {actual_rate:.1f} msgs/sec)")


async def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("Phase 5.0.3 — Contrib Operators Demo")
    print("="*60)
    
    await demo_ohlc_resample()
    await demo_deduplicate()
    await demo_throttle()
    
    print("\n" + "="*60)
    print("✅ All demos complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

