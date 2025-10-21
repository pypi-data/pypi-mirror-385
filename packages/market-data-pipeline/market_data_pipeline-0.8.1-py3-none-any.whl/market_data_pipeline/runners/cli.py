"""Command-line interface for the market data pipeline."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
from jsonschema import validate, ValidationError

from ..batcher import HybridBatcher
from ..config import get_config
from ..context import PipelineContext
from ..operator import SecondBarAggregator, Operator
from ..pipeline import StreamingPipeline
from ..pipeline_builder import PipelineBuilder, PipelineSpec, PipelineOverrides
from ..sink import StoreSink
from ..source import SyntheticSource

# Optional extras
try:
    from ..source import ReplaySource, IBKRSource  # type: ignore
except Exception:
    ReplaySource = None  # type: ignore
    IBKRSource = None  # type: ignore

try:
    from market_data_store.async_client import AsyncBatchProcessor  # type: ignore
except Exception:
    AsyncBatchProcessor = None  # type: ignore


@click.group()
def main() -> None:
    """Market Data Pipeline CLI."""
    pass


@main.command()
@click.option("--tenant", required=True, help="Tenant ID")
@click.option("--pipeline", required=False, default="cli", help="Pipeline ID")
@click.option(
    "--source", type=click.Choice(["synthetic", "replay", "ibkr"]), default="synthetic"
)
@click.option("--symbols", required=True, help="Comma-separated list of symbols")
@click.option("--rate", type=int, default=100, help="Ticks per second (synthetic/ibkr)")
@click.option("--replay-path", type=str, help="Path for replay source (CSV/Parquet)")
@click.option("--operator", type=click.Choice(["bars", "options"]), default="bars")
@click.option("--sink", type=click.Choice(["store"]), default="store")
@click.option("--duration", type=float, default=10.0, help="Duration in seconds")
@click.option("--config", help="Configuration file path (optional)")
def run(
    tenant: str,
    pipeline: str,
    source: str,
    symbols: str,
    rate: int,
    replay_path: Optional[str],
    operator: str,
    sink: str,
    duration: float,
    config: Optional[str],
) -> None:
    """Run a market data pipeline."""

    cfg = get_config()  # you can extend to load from file if desired
    symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]

    # Build context
    ctx = PipelineContext(tenant_id=tenant, pipeline_id=pipeline)

    # Source
    if source == "synthetic":
        src = SyntheticSource(
            symbols=symbol_list, ticks_per_sec=rate, pacing_budget=(rate, rate), ctx=ctx
        )
    elif source == "replay":
        if ReplaySource is None:
            click.echo("ReplaySource not installed", err=True)
            sys.exit(2)
        if not replay_path:
            click.echo("--replay-path is required for replay source", err=True)
            sys.exit(2)
        src = ReplaySource(path=replay_path, ctx=ctx)  # type: ignore
    else:
        if IBKRSource is None:
            click.echo("IBKRSource not installed", err=True)
            sys.exit(2)
        src = IBKRSource(symbols=symbol_list, ctx=ctx)  # type: ignore

    # Operator
    if operator == "bars":
        op: Operator = SecondBarAggregator(window_sec=1)
    else:
        op = SecondBarAggregator(window_sec=1)  # swap to Options operator when ready

    # Batcher
    batcher = HybridBatcher(
        max_rows=getattr(cfg, "batch_size", 500),
        max_bytes=getattr(cfg, "max_bytes", 512_000),
        flush_ms=getattr(cfg, "flush_ms", 100),
        op_queue_max=getattr(cfg, "op_queue_max", 8),
        drop_policy=getattr(cfg, "drop_policy", "oldest"),
    )

    # Sink
    if sink == "store":
        if AsyncBatchProcessor is None:
            click.echo("market_data_store AsyncBatchProcessor not installed", err=True)
            sys.exit(2)
        bp = (
            asyncio.run(AsyncBatchProcessor.from_env_async())
            if hasattr(AsyncBatchProcessor, "from_env_async")
            else AsyncBatchProcessor.from_env()
        )  # type: ignore
        snk = StoreSink(
            bp,
            workers=getattr(cfg, "sink_workers", 2),
            queue_max=getattr(cfg, "sink_queue_max", 100),
            backpressure_policy=getattr(cfg, "drop_policy", "oldest"),
            ctx=ctx,
        )
    else:
        click.echo(f"Unsupported sink: {sink}", err=True)
        sys.exit(2)

    pipe = StreamingPipeline(
        source=src, operator=op, batcher=batcher, sink=snk, ctx=ctx
    )

    try:
        asyncio.run(pipe.run(duration_sec=duration))
        click.echo(f"Pipeline completed successfully for tenant {tenant}")
    except KeyboardInterrupt:
        click.echo("Pipeline interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Pipeline error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--spec", type=click.Path(exists=True), required=True, help="Path to JSON PipelineSpec file")
def runspec(spec: str) -> None:
    """Run a pipeline from a JSON PipelineSpec file."""
    try:
        # Load JSON spec
        with open(spec, 'r') as f:
            data = json.load(f)
        
        # Validate against JSON schema
        schema_path = Path(__file__).parent.parent.parent / "pipeline_spec.schema.json"
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        validate(instance=data, schema=schema)
        
        # Create PipelineSpec from JSON
        spec_obj = PipelineSpec(
            tenant_id=data["tenant_id"],
            pipeline_id=data["pipeline_id"],
            source=data["source"],
            symbols=data.get("symbols", []),
            duration_sec=data.get("duration_sec"),
            operator=data.get("operator", "bars"),
            sink=data.get("sink", "store"),
            overrides=PipelineOverrides(**data.get("overrides", {})),
        )
        
        # Use PipelineBuilder to create and run the pipeline
        builder = PipelineBuilder()
        asyncio.run(builder.build_and_run(spec_obj))
        
        click.echo(f"Pipeline completed successfully: {spec_obj.tenant_id}/{spec_obj.pipeline_id}")
        
    except FileNotFoundError:
        click.echo(f"Spec file not found: {spec}", err=True)
        sys.exit(1)
    except json.JSONDecodeError as e:
        click.echo(f"Invalid JSON in spec file: {e}", err=True)
        sys.exit(1)
    except ValidationError as e:
        click.echo(f"Schema validation error: {e.message}", err=True)
        sys.exit(1)
    except KeyError as e:
        click.echo(f"Missing required field in spec: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("Pipeline interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Pipeline error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--port", default=8083, help="API server port")
@click.option("--host", default="0.0.0.0", help="API server host")
def api(port: int, host: str) -> None:
    """Start the API server."""
    import uvicorn
    from .api import app

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
