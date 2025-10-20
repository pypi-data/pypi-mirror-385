"""Domain-specific conformance checks for imaging-starter.

This script is invoked by `vigil conformance` to validate that critical
pipeline outputs match committed golden baselines. It demonstrates the
domain-specific extension pattern for fast quality checks.

Design goals:
- Fast: Run critical steps directly, bypassing Snakemake overhead
- Focused: Check only segmentation and metrics steps (not full pipeline)
- Domain-specific: Validate imaging metrics (accuracy, precision, recall, F1)
- Versioned: Golden baselines committed to git for reproducibility
- CI-friendly: Simple pass/fail exit code

This is NOT a core Vigil feature - each project implements conformance
differently based on their scientific domain needs. See docs/cli-reference.md
and docs/creating-starters.md for guidance on implementing conformance in
your own projects.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

GOLDEN = "app/code/tests/conformance/metrics_golden.json"


def run_cmd(cmd: str) -> None:
    print("$", cmd)
    res = subprocess.run(cmd, shell=True, check=False)
    if res.returncode != 0:
        raise SystemExit(res.returncode)


def _diff_keys(keys: Sequence[str], golden: dict[str, float], current: dict[str, float]) -> list[tuple[str, float, float]]:
    return [
        (k, golden[k], current[k])
        for k in keys
        if abs(float(golden[k]) - float(current[k])) > 1e-6
    ]


def main() -> None:
    # Clean outputs
    shutil.rmtree("app/code/artifacts", ignore_errors=True)
    os.makedirs("app/code/artifacts", exist_ok=True)

    # Run steps directly (fast) instead of full Snakemake for conformance
    run_cmd(
        "uv run python -m app.code.lib.steps.segment --table app/data/handles/data.parquet.dhandle.json --out app/code/artifacts/processed.parquet --params app/code/configs/params.yaml"
    )
    run_cmd(
        "uv run python -m app.code.lib.steps.metrics --processed app/code/artifacts/processed.parquet --out app/code/artifacts/metrics.json --table_handle app/data/handles/data.parquet.dhandle.json"
    )

    with open(GOLDEN) as f:
        golden = json.load(f)
    with open("app/code/artifacts/metrics.json") as f:
        cur = json.load(f)

    keys = ["n", "tp", "tn", "fp", "fn", "accuracy", "precision", "recall", "f1"]
    diffs = _diff_keys(keys, golden, cur)
    if diffs:
        print("Conformance FAILED; diffs:")
        for k, g, c in diffs:
            print(f" - {k}: expected {g} got {c}")
        raise SystemExit(1)
    print("Conformance PASSED.")


if __name__ == "__main__":
    main()
