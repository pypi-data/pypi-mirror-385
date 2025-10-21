from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from market_data_pipeline.runtime.unified_runtime import UnifiedRuntime
from market_data_pipeline.settings.runtime_unified import (
    RuntimeModeEnum,
    UnifiedRuntimeSettings,
)


@pytest.mark.asyncio
async def test_classic_facade_start_run_stop(monkeypatch):
    # Mock PipelineService & PipelineBuilder
    service_mock_cls = MagicMock()
    service_mock = AsyncMock()
    service_mock_cls.return_value = service_mock
    service_mock.start = AsyncMock()
    service_mock.stop = AsyncMock()
    service_mock.create_and_run_pipeline = AsyncMock(return_value="pipeline-id-123")

    builder_mock_cls = MagicMock()
    builder_mock = MagicMock()
    builder_mock.create_pipeline.return_value = object()
    builder_mock_cls.return_value = builder_mock

    sys_modules = {}
    sys_modules["market_data_pipeline.runners.service"] = MagicMock(
        PipelineService=service_mock_cls
    )
    sys_modules["market_data_pipeline.pipeline_builder"] = MagicMock(
        PipelineBuilder=builder_mock_cls
    )

    with patch.dict("sys.modules", sys_modules):
        settings = UnifiedRuntimeSettings(
            mode=RuntimeModeEnum.classic,
            classic={"spec": {"name": "X"}},
        )
        async with UnifiedRuntime(settings) as rt:
            assert rt.mode.value == "classic"
            handle = await rt.run("classic-job")
            assert handle == "pipeline-id-123"


@pytest.mark.asyncio
async def test_dag_facade_start_run_stop(monkeypatch):
    # Mock DagRuntime, Dag, RuntimeOrchestrator
    dag_cls = MagicMock()
    dag_obj = MagicMock()
    dag_cls.from_dict.return_value = dag_obj

    dag_runtime_cls = MagicMock()
    dag_runtime = AsyncMock()
    dag_runtime.execute = AsyncMock()
    dag_runtime_cls.return_value = dag_runtime

    orchestrator_cls = MagicMock()

    sys_modules = {}
    sys_modules["market_data_pipeline.orchestration.dag.graph"] = MagicMock(Dag=dag_cls)
    sys_modules["market_data_pipeline.orchestration.dag.runtime"] = MagicMock(
        DagRuntime=dag_runtime_cls
    )
    sys_modules["market_data_pipeline.orchestration.runtime_orchestrator"] = MagicMock(
        RuntimeOrchestrator=orchestrator_cls
    )

    with patch.dict("sys.modules", sys_modules):
        settings = UnifiedRuntimeSettings(
            mode=RuntimeModeEnum.dag,
            dag={"graph": {"nodes": [], "edges": []}, "name": "DAG1"},
        )
        async with UnifiedRuntime(settings) as rt:
            assert rt.mode.value == "dag"
            job_name = await rt.run()
            assert job_name == "DAG1"

