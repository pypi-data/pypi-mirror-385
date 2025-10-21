#!/usr/bin/env python3
"""
Fetch schemas from Schema Registry for CI/CD contract testing.

Usage:
    python scripts/fetch_schemas.py [--output DIR] [--url URL] [--track TRACK]

Environment Variables:
    REGISTRY_URL: Registry service base URL
    REGISTRY_TOKEN: Optional admin token
    SCHEMA_TRACK: Preferred schema track (default: v2)

Examples:
    # Fetch schemas to default location
    python scripts/fetch_schemas.py

    # Fetch to custom directory
    python scripts/fetch_schemas.py --output tests/schemas

    # Fetch specific track
    python scripts/fetch_schemas.py --track v1

Phase 11.0B: Replaces bundled schemas from Core repo with live registry fetch.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from market_data_pipeline.schemas.config import RegistryConfig


async def fetch_schema(
    client: Any,
    name: str,
    track: str,
    output_dir: Path,
) -> None:
    """
    Fetch and save a single schema.
    
    Args:
        client: Registry client instance
        name: Schema name
        track: Schema track (v1/v2)
        output_dir: Output directory
    """
    try:
        from core_registry_client import Track
        
        # Map string to Track enum
        track_enum = Track.V2 if track == "v2" else Track.V1
        
        # Fetch schema
        schema = await client.fetch_schema(
            track=track_enum,
            name=name,
        )
        
        # Save to file
        filename = f"{name}.{track}.json"
        filepath = output_dir / filename
        
        with open(filepath, "w") as f:
            json.dump(schema.content, f, indent=2)
        
        print(f"✓ Fetched {name} (track={track}, version={schema.core_version})")
        print(f"  → {filepath}")
    
    except Exception as e:
        print(f"✗ Failed to fetch {name} (track={track}): {e}", file=sys.stderr)
        raise


async def fetch_all_schemas(
    registry_url: str,
    token: str | None,
    track: str,
    output_dir: Path,
) -> None:
    """
    Fetch all critical schemas from registry.
    
    Args:
        registry_url: Registry base URL
        token: Optional admin token
        track: Preferred track
        output_dir: Output directory
    """
    try:
        from core_registry_client import RegistryClient
    except ImportError:
        print(
            "✗ core-registry-client not installed. "
            "Run: pip install core-registry-client",
            file=sys.stderr,
        )
        sys.exit(1)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Connect to registry
    async with RegistryClient(
        base_url=registry_url,
        token=token,
        timeout=30.0,
    ) as client:
        print(f"Connected to registry: {registry_url}")
        print(f"Output directory: {output_dir}")
        print(f"Preferred track: {track}")
        print()
        
        # Critical schemas for pipeline
        schemas = [
            "telemetry.FeedbackEvent",
            "telemetry.RateAdjustment",
        ]
        
        # Fetch each schema
        for schema_name in schemas:
            await fetch_schema(client, schema_name, track, output_dir)
        
        print()
        print(f"✓ Successfully fetched {len(schemas)} schemas")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch schemas from Schema Registry for contract testing"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("tests/contracts/schemas"),
        help="Output directory (default: tests/contracts/schemas)",
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Registry URL (default: from REGISTRY_URL env var)",
    )
    parser.add_argument(
        "--token",
        type=str,
        help="Registry token (default: from REGISTRY_TOKEN env var)",
    )
    parser.add_argument(
        "--track",
        type=str,
        default="v2",
        choices=["v1", "v2"],
        help="Schema track (default: v2)",
    )
    
    args = parser.parse_args()
    
    # Load config from env
    config = RegistryConfig()
    
    # Override from CLI args
    registry_url = args.url or config.url
    token = args.token or config.token
    
    if not registry_url:
        print(
            "✗ Registry URL not configured. "
            "Set REGISTRY_URL env var or use --url flag.",
            file=sys.stderr,
        )
        sys.exit(1)
    
    # Run fetch
    try:
        asyncio.run(
            fetch_all_schemas(
                registry_url=registry_url,
                token=token,
                track=args.track,
                output_dir=args.output,
            )
        )
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

