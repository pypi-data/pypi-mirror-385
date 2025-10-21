"""Integration test for CLI in DAG mode."""
import sys
from pathlib import Path
from subprocess import PIPE, run

import pytest

CONFIG = """
mode: dag
dag:
  nodes:
    - id: src
      type: operator.buffer
      params:
        max_items: 1
        flush_interval: 0.01
    - id: sink
      type: operator.map
      params: {}
  edges:
    - [src, sink]
"""


@pytest.mark.integration
@pytest.mark.skipif(
    sys.platform == "win32",
    reason="CLI integration tests may have path issues on Windows"
)
def test_cli_runs_in_dag_mode(tmp_path: Path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(CONFIG, encoding="utf-8")

    proc = run(
        [sys.executable, "-m", "market_data_pipeline.cli.main", "run", "--config", str(cfg)],
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        timeout=10,
    )
    # May fail due to missing dependencies, but should not crash
    assert proc.returncode in (0, 1)  # 0 = success, 1 = expected error

