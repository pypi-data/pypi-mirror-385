from __future__ import annotations

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .feedback import PipelineFeedbackSettings


class MetricsSettings(BaseModel):
    """
    Metrics configuration for Phase 6.0B KEDA autoscaling.
    
    If the FastAPI API is disabled but you still want metrics exposed,
    set standalone_port to start a simple Prometheus HTTP server.
    """

    enable: bool = Field(
        default=True, description="Enable Prometheus metrics collection"
    )
    standalone_port: int | None = Field(
        default=None,
        description="Port for standalone Prometheus server (if API is disabled)",
    )

    model_config = {"env_prefix": "MDP_METRICS_"}


class RuntimeModeEnum(str, Enum):
    classic = "classic"
    dag = "dag"


class ClassicRuntimeSettings(BaseModel):
    """
    Minimal shims that align with your existing Classic runtime.
    - 'spec' feeds PipelineBuilder.create_pipeline(spec)
    - 'service' maps to PipelineService(...) kwargs (optional)
    - 'builder' maps to PipelineBuilder(...) kwargs (optional)
    """

    spec: dict[str, Any] | None = Field(default=None)
    service: dict[str, Any] | None = Field(default=None)
    builder: dict[str, Any] | None = Field(default=None)


class DagRuntimeSettings(BaseModel):
    """
    DAG runtime config. Keep it simple in v1:
    - 'graph' is the dict passed to Dag.from_dict(...)
    - 'name' optional job name
    """

    graph: dict[str, Any] | None = Field(default=None)
    name: str | None = Field(default=None)


class UnifiedRuntimeSettings(BaseModel):
    """
    Mode-selecting settings object used by the UnifiedRuntime facade.
    Enhanced in Phase 5.0.5b with file/env loading.
    """

    mode: RuntimeModeEnum = Field(default=RuntimeModeEnum.classic)
    classic: ClassicRuntimeSettings | dict[str, Any] = Field(
        default_factory=ClassicRuntimeSettings
    )
    dag: DagRuntimeSettings | dict[str, Any] = Field(default_factory=DagRuntimeSettings)
    feedback: PipelineFeedbackSettings = Field(
        default_factory=PipelineFeedbackSettings,
        description="Backpressure feedback settings (Phase 6.0A)"
    )
    metrics: MetricsSettings = Field(
        default_factory=MetricsSettings,
        description="Metrics configuration for KEDA autoscaling (Phase 6.0B)"
    )

    @model_validator(mode="after")
    def _validate_mode_payload(self):
        # Normalize dict to models if needed
        if isinstance(self.classic, dict):
            self.classic = ClassicRuntimeSettings(**self.classic)
        if isinstance(self.dag, dict):
            self.dag = DagRuntimeSettings(**self.dag)

        if self.mode == RuntimeModeEnum.classic:
            if not self.classic or (not self.classic.spec and not self.classic.service):
                msg = "classic mode requires 'classic.spec' or 'classic.service'"
                raise ValueError(msg)
        elif not self.dag or not self.dag.graph:
            msg = "dag mode requires 'dag.graph'"
            raise ValueError(msg)

        return self

    # ---------- Convenience loaders ----------

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UnifiedRuntimeSettings:
        """Load settings from a dictionary."""
        return cls(**data)

    @classmethod
    def from_file(cls, path: str | Path) -> UnifiedRuntimeSettings:
        """
        Load settings from YAML or JSON file.
        Requires PyYAML for .yaml/.yml files.
        """
        p = Path(path)
        if not p.exists():
            msg = f"Config file not found: {p}"
            raise FileNotFoundError(msg)

        text = p.read_text(encoding="utf-8")
        if p.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml
            except Exception as e:
                msg = "PyYAML is required to load YAML configs. Install 'pyyaml'."
                raise RuntimeError(msg) from e
            data = yaml.safe_load(text) or {}
        else:
            data = json.loads(text)

        if not isinstance(data, dict):
            msg = "Config file must load to a top-level object/dict."
            raise ValueError(msg)
        return cls.from_dict(data)

    @classmethod
    def from_env(
        cls,
        env_prefix: str = "MDP_UNIFIED_",
        fallback: UnifiedRuntimeSettings | None = None,
    ) -> UnifiedRuntimeSettings:
        """
        Load settings from environment variables.
        Minimal env overlay:
          MDP_UNIFIED_MODE=classic|dag
          MDP_UNIFIED_CLASSIC_JSON='{"key":"value"}'
          MDP_UNIFIED_DAG_JSON='{"key":"value"}'
        """
        mode = os.getenv(f"{env_prefix}MODE")
        classic_json = os.getenv(f"{env_prefix}CLASSIC_JSON")
        dag_json = os.getenv(f"{env_prefix}DAG_JSON")

        payload: dict[str, Any] = {}
        if fallback is not None:
            payload = json.loads(fallback.model_dump_json())

        if mode:
            payload["mode"] = mode

        if classic_json:
            payload["classic"] = json.loads(classic_json)

        if dag_json:
            payload["dag"] = json.loads(dag_json)

        return cls(**payload)
