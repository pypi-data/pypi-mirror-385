import pytest

from market_data_pipeline.settings.runtime_unified import (
    RuntimeModeEnum,
    UnifiedRuntimeSettings,
)


def test_classic_ok():
    s = UnifiedRuntimeSettings(
        mode=RuntimeModeEnum.classic,
        classic={"spec": {"name": "p", "source": {"type": "synthetic"}}},
    )
    assert s.mode == RuntimeModeEnum.classic
    assert s.classic.spec is not None


def test_classic_missing_spec_fails():
    with pytest.raises(ValueError):
        UnifiedRuntimeSettings(mode=RuntimeModeEnum.classic, classic={})


def test_dag_ok():
    s = UnifiedRuntimeSettings(
        mode=RuntimeModeEnum.dag,
        dag={"graph": {"nodes": [], "edges": []}, "name": "job"},
    )
    assert s.mode == RuntimeModeEnum.dag
    assert s.dag.graph is not None


def test_dag_missing_graph_fails():
    with pytest.raises(ValueError):
        UnifiedRuntimeSettings(mode=RuntimeModeEnum.dag, dag={})

