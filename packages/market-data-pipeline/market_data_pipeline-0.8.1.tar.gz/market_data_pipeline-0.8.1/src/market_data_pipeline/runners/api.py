"""FastAPI application for the market data pipeline."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from jsonschema import validate, ValidationError
from pydantic import BaseModel, Field, validator
from prometheus_client import generate_latest

from ..config import get_config
from ..metrics import PipelineMetrics
from ..pipeline_builder import PipelineBuilder, PipelineSpec as BuilderPipelineSpec, PipelineOverrides
from .service import PipelineService, PipelineSpec

app = FastAPI(
    title="Market Data Pipeline API",
    description="API for market data pipeline orchestration",
    version="0.1.0",
)

metrics: Optional[PipelineMetrics] = None
service: Optional[PipelineService] = None
pipeline_schema: Optional[Dict[str, Any]] = None


def load_pipeline_schema() -> Dict[str, Any]:
    """Load the JSON schema for PipelineSpec validation."""
    global pipeline_schema
    if pipeline_schema is None:
        schema_path = Path(__file__).parent.parent.parent / "pipeline_spec.schema.json"
        with open(schema_path, 'r') as f:
            pipeline_schema = json.load(f)
    return pipeline_schema


class CreatePipelineRequest(BaseModel):
    tenant_id: str = Field(..., description="Tenant ID")
    pipeline_id: str = Field(..., description="Pipeline ID")
    source_type: str = Field("synthetic", description="synthetic|replay|ibkr")
    symbols: List[str] = Field(..., description="Symbols list")
    rate: Optional[int] = Field(None, description="Ticks/sec (synthetic/ibkr)")
    replay_path: Optional[str] = Field(None, description="Path for replay source")
    duration: Optional[float] = Field(
        None, description="Duration sec (None = run until delete)"
    )
    operator_type: str = Field("bars", description="bars|options")
    sink_type: str = Field("store", description="store|kafka (future)")
    extra: Dict[str, Any] = Field(default_factory=dict)

    @validator("source_type")
    def validate_source_type(cls, v: str) -> str:
        v = v.lower()
        if v not in {"synthetic", "replay", "ibkr"}:
            raise ValueError("source_type must be one of: synthetic, replay, ibkr")
        return v

    @validator("operator_type")
    def validate_operator_type(cls, v: str) -> str:
        v = v.lower()
        if v not in {"bars", "options"}:
            raise ValueError("operator_type must be one of: bars, options")
        return v

    @validator("sink_type")
    def validate_sink_type(cls, v: str) -> str:
        v = v.lower()
        if v not in {"store", "kafka"}:
            raise ValueError("sink_type must be one of: store, kafka")
        return v


class PipelineSpecRequest(BaseModel):
    """JSON-spec aware pipeline request using PipelineBuilder."""
    tenant_id: str = Field(..., description="Tenant ID")
    pipeline_id: str = Field(..., description="Pipeline ID")
    source: str = Field(..., description="synthetic|replay|ibkr")
    symbols: List[str] = Field(default_factory=list, description="Symbols list")
    duration_sec: Optional[float] = Field(None, description="Duration in seconds")
    operator: str = Field("bars", description="bars|options")
    sink: str = Field("store", description="store|kafka")
    overrides: Dict[str, Any] = Field(default_factory=dict, description="Configuration overrides")

    @validator("source")
    def validate_source(cls, v: str) -> str:
        v = v.lower()
        if v not in {"synthetic", "replay", "ibkr"}:
            raise ValueError("source must be one of: synthetic, replay, ibkr")
        return v

    @validator("operator")
    def validate_operator(cls, v: str) -> str:
        v = v.lower()
        if v not in {"bars", "options"}:
            raise ValueError("operator must be one of: bars, options")
        return v

    @validator("sink")
    def validate_sink(cls, v: str) -> str:
        v = v.lower()
        if v not in {"store", "kafka"}:
            raise ValueError("sink must be one of: store, kafka")
        return v


class PipelineResponse(BaseModel):
    pipeline_key: str
    message: str = "ok"


@app.on_event("startup")
async def startup_event() -> None:
    global metrics, service
    metrics = PipelineMetrics()
    cfg = get_config()
    metrics.set_pipeline_info(
        tenant_id="system",
        pipeline_id="api",
        version="0.1.0",
        config_file=cfg.__class__.__name__,
    )
    service = PipelineService(cfg)
    await service.start()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    if service:
        await service.stop()


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Market Data Pipeline API", "version": "0.1.0"}


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "healthy", "service": "market-data-pipeline"}


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics_endpoint() -> str:
    """
    Prometheus metrics endpoint for KEDA autoscaling and Grafana.
    
    Returns all registered metrics including:
    - Pipeline metrics (PipelineMetrics class)
    - Phase 6.0B KEDA metrics (PIPELINE_RATE_SCALE_FACTOR, etc.)
    """
    if metrics is None:
        raise HTTPException(status_code=503, detail="Metrics not initialized")
    # Use global default registry (includes all metrics from all modules)
    return generate_latest()  # type: ignore[return-value]


@app.post("/pipelines", response_model=PipelineResponse)
async def create_pipeline(req: CreatePipelineRequest) -> PipelineResponse:
    """Create pipeline using legacy API format."""
    if not service:
        raise HTTPException(status_code=503, detail="Service not available")
    spec = PipelineSpec(
        tenant_id=req.tenant_id,
        pipeline_id=req.pipeline_id,
        source_type=req.source_type,
        symbols=req.symbols,
        rate=req.rate,
        replay_path=req.replay_path,
        duration_sec=req.duration,
        operator_type=req.operator_type,
        sink_type=req.sink_type,
        extra=req.extra,
    )
    try:
        key = await service.create_pipeline(spec)
        return PipelineResponse(pipeline_key=key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/pipelines/spec", response_model=PipelineResponse)
async def create_pipeline_from_spec(req: PipelineSpecRequest) -> PipelineResponse:
    """Create pipeline using JSON PipelineSpec format with PipelineBuilder."""
    try:
        # Validate against JSON schema
        schema = load_pipeline_schema()
        spec_dict = req.dict()
        validate(instance=spec_dict, schema=schema)
        
        # Convert to PipelineBuilder spec
        builder_spec = BuilderPipelineSpec(
            tenant_id=req.tenant_id,
            pipeline_id=req.pipeline_id,
            source=req.source,
            symbols=req.symbols,
            duration_sec=req.duration_sec,
            operator=req.operator,
            sink=req.sink,
            overrides=PipelineOverrides(**req.overrides),
        )
        
        # Use PipelineBuilder to create and run the pipeline
        builder = PipelineBuilder()
        await builder.build_and_run(builder_spec)
        
        key = f"{req.tenant_id}:{req.pipeline_id}"
        return PipelineResponse(pipeline_key=key, message="Pipeline completed")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Schema validation error: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/pipelines/{tenant_id}:{pipeline_id}", response_model=PipelineResponse)
async def delete_pipeline(tenant_id: str, pipeline_id: str) -> PipelineResponse:
    if not service:
        raise HTTPException(status_code=503, detail="Service not available")
    key = f"{tenant_id}:{pipeline_id}"
    try:
        await service.delete_pipeline(key)
        return PipelineResponse(pipeline_key=key, message="deleted")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/pipelines", response_model=List[str])
async def list_pipelines() -> List[str]:
    if not service:
        raise HTTPException(status_code=503, detail="Service not available")
    return await service.list_pipelines()


@app.get("/pipelines/{tenant_id}:{pipeline_id}")
async def get_pipeline(tenant_id: str, pipeline_id: str) -> Dict[str, Any]:
    if not service:
        raise HTTPException(status_code=503, detail="Service not available")
    key = f"{tenant_id}:{pipeline_id}"
    try:
        return await service.get_pipeline_status(key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
