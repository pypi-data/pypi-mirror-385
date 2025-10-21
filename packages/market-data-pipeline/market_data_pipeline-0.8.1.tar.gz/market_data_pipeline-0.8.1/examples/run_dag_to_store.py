"""
Phase 5.0.5 — End-to-End DAG Pipeline Example

Demonstrates IBKR → DAG Operators → Store Sink flow using the unified runtime.

Requirements:
- market-data-core
- market-data-ibkr (optional, will skip if not available)
- market-data-store (optional, will skip if not available)

Run:
  python examples/run_dag_to_store.py
  
  OR with YAML:
  mdp run --config examples/run_dag_to_store.yaml
"""

import asyncio

from market_data_pipeline.runtime import UnifiedRuntime
from market_data_pipeline.settings.runtime_unified import UnifiedRuntimeSettings

# Example DAG configuration
EXAMPLE_DAG = {
    "mode": "dag",
    "dag": {
        "graph": {
            "nodes": [
                {
                    "id": "src",
                    "type": "provider.ibkr.stream",
                    "params": {
                        "stream": "bars",
                        "symbols": ["AAPL", "MSFT"],
                        "resolution": "5s",
                        "settings": {"client_id": 101},
                    },
                },
                {
                    "id": "resample",
                    "type": "operator.resample_ohlc",
                    "params": {"interval": "1m"},
                },
                {
                    "id": "sink",
                    "type": "operator.map",
                    "params": {
                        "fn_name": "store_bars",
                        "sink": "market_data_store.sinks.bars.BarsSink",
                    },
                },
            ],
            "edges": [["src", "resample"], ["resample", "sink"]],
        }
    },
}


async def main():
    print("=" * 60)
    print("Phase 5.0.5 — DAG to Store Pipeline Example")
    print("=" * 60)

    try:
        settings = UnifiedRuntimeSettings.from_dict(EXAMPLE_DAG)
        print(f"\nMode: {settings.mode.value}")
        print(f"Nodes: {len(settings.dag.graph.get('nodes', []))}")  # type: ignore[union-attr]
        print(f"Edges: {len(settings.dag.graph.get('edges', []))}")  # type: ignore[union-attr]

        async with UnifiedRuntime(settings) as rt:
            print(f"\nRuntime started in {rt.mode.value} mode")
            await rt.run("dag_to_store")
            print("\n✅ Pipeline completed successfully")

    except ImportError as e:
        print(f"\n⚠️ Skipping example: Missing dependency ({e})")
        print("Install: pip install market-data-ibkr market-data-store")

    except Exception as e:
        print(f"\n⚠️ Example encountered expected error: {e}")
        print("(This is normal if dependencies are not configured)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

