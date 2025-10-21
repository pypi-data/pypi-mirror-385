# Phase 5.0.1 — Core DAG Runtime

This drop introduces a production-ready, opt-in **DAG runtime** that coexists with the classic `PipelineService`.

## What's in here

- `Dag`, `Node`, `Edge` with validation (cycle detection)
- Bounded `Channel` with **high/low watermarks** and async callbacks
- Core async operators: `map_async`, `filter_async`, `buffer_async`, `tumbling_window`
- `DagRuntime` to execute node coroutines over wired channels
- `RuntimeOrchestrator` façade to unify "classic" and "dag" modes
- Tests and an example script

## Quick start

```bash
pytest tests/unit/dag -q
python examples/run_dag_runtime_basic.py
```

## Backpressure

Channels emit best-effort on_high/on_low signals. In Phase 5.0.7, these will feed autoscaling and upstream flow control.

## Compatibility

- 100% backward compatible (DAG runtime is opt-in)
- No changes to existing classic pipeline APIs

## Next steps

- 5.0.2 Windowing polish (event-time watermarks)
- 5.0.3 Operators (resample, router, dedupe)
- 5.0.5 API unification docs & examples
- 5.0.7 Store backpressure adapter

---

## How to apply

1. Add these files under your repo paths as shown.
2. Ensure `src/` is in your editable install or `pip install -e .`.
3. Run tests:
   ```bash
   pytest tests/unit/dag -q
   ```
4. Try the example:
   ```bash
   python examples/run_dag_runtime_basic.py
   ```

