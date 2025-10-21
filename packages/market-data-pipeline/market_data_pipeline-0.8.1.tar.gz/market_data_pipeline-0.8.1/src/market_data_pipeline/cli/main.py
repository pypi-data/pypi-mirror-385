from __future__ import annotations

import argparse
import asyncio
import sys

from loguru import logger

from market_data_pipeline.runtime.unified_runtime import UnifiedRuntime
from market_data_pipeline.settings.runtime_unified import (
    RuntimeModeEnum,
    UnifiedRuntimeSettings,
)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="mdp",
        description="Market Data Pipeline CLI (Unified Runtime)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run a pipeline/runtime job.")
    run.add_argument("--mode", choices=[m.value for m in RuntimeModeEnum], required=False)
    run.add_argument("--config", type=str, required=True, help="Path to YAML/JSON config")
    run.add_argument("--job", type=str, default="default", help="Job name (for DAG)")

    # Stubs to extend later
    sub.add_parser("list", help="List known jobs (stub)")
    status = sub.add_parser("status", help="Get job status (stub)")
    status.add_argument("--job", type=str, default="default")

    return p.parse_args(argv)


async def _run_cmd(args: argparse.Namespace) -> int:
    if args.command == "list":
        print("Jobs: [example] (stub)")
        return 0

    if args.command == "status":
        print(f"Status for job '{args.job}': RUNNING (stub)")
        return 0

    if args.command == "run":
        settings = UnifiedRuntimeSettings.from_file(args.config)
        if args.mode:
            # override config mode from CLI if provided
            settings = settings.model_copy(update={"mode": RuntimeModeEnum(args.mode)})

        logger.info(f"Starting UnifiedRuntime in mode={settings.mode.value}")
        async with UnifiedRuntime(settings) as rt:
            # Classic: will delegate to existing service/runner
            # DAG:     will delegate to DagRuntime (builder/registry used internally)
            await rt.run(name=getattr(args, "job", "default"))
        logger.info("UnifiedRuntime finished.")
        return 0

    return 1


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    try:
        exit_code = asyncio.run(_run_cmd(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except Exception as exc:
        logger.exception(f"mdp failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()

