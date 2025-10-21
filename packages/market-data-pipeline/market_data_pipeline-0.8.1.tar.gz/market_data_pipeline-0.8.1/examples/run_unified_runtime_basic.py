"""
Phase 5.0.5a — Unified Runtime Basic Example

Demonstrates the UnifiedRuntime facade for both Classic and DAG modes.
"""
import asyncio

from market_data_pipeline.runtime import UnifiedRuntime
from market_data_pipeline.settings.runtime_unified import (
    RuntimeModeEnum,
    UnifiedRuntimeSettings,
)


async def main():
    print("=" * 60)
    print("Phase 5.0.5a — Unified Runtime Examples")
    print("=" * 60)

    # Example 1: Classic mode (requires your classic builder/service in path)
    print("\n[Example 1: Classic Mode]")
    classic_settings = UnifiedRuntimeSettings(
        mode=RuntimeModeEnum.classic,
        classic={
            "spec": {
                "name": "demo-classic",
                "source": {"type": "synthetic", "symbols": ["AAPL"], "interval_ms": 10},
                "operator": {"type": "noop"},
                "sink": {"type": "console"},
            }
        },
    )
    try:
        async with UnifiedRuntime(classic_settings) as rt:
            print(f"  Mode: {rt.mode.value}")
            print(f"  State: started={rt.state.started}")
            await rt.run()
            print("  ✅ Classic mode executed successfully")
    except Exception as e:
        print(f"  ⚠️ Classic example skipped: {e}")

    # Example 2: DAG mode (requires DAG runtime installed)
    print("\n[Example 2: DAG Mode]")
    dag_settings = UnifiedRuntimeSettings(
        mode=RuntimeModeEnum.dag,
        dag={
            "name": "demo-dag",
            "graph": {
                "nodes": [
                    {"id": "src", "type": "source.synthetic", "config": {"rate": 100}},
                    {"id": "map", "type": "operator.map", "config": {"expr": "x"}},
                    {"id": "out", "type": "sink.console"},
                ],
                "edges": [{"from": "src", "to": "map"}, {"from": "map", "to": "out"}],
            },
        },
    )
    try:
        async with UnifiedRuntime(dag_settings) as rt:
            print(f"  Mode: {rt.mode.value}")
            print(f"  State: started={rt.state.started}")
            await rt.run()
            print("  ✅ DAG mode executed successfully")
    except Exception as e:
        print(f"  ⚠️ DAG example skipped: {e}")

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

