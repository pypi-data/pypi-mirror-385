# tests/unit/test_source_synthetic.py
import asyncio
import pytest
from market_data_pipeline.source.synthetic import SyntheticSource


@pytest.mark.asyncio
async def test_synthetic_source_emits_ticks_and_respects_symbols():
    src = SyntheticSource(
        symbols=["NVDA", "SPY"], ticks_per_sec=20, pacing_budget=(20, 20)
    )
    emitted = []

    async def collect():
        async for q in src.stream():
            emitted.append(q)
            if len(emitted) >= 30:
                break
        await src.close()

    await asyncio.wait_for(collect(), timeout=3.0)
    assert len(emitted) >= 30
    syms = {q.symbol for q in emitted}
    assert syms == {"NVDA", "SPY"}
