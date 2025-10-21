"""Workbench bootstrap configuration builder."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .panels import build_data_panel, build_evidence_panel, build_imaging_panel


def build_bootstrap_config(
    *,
    handles_dir: Path | None = None,
    sample_size: int | None = None,
    evidence_graph_path: Path | None = None,
) -> dict[str, Any]:
    """Assemble the Workbench bootstrap configuration."""

    data_panel_kwargs: dict[str, Any] = {}
    if handles_dir is not None:
        data_panel_kwargs["handles_dir"] = handles_dir
    if sample_size is not None:
        data_panel_kwargs["sample_size"] = sample_size

    panels = [
        build_data_panel(**data_panel_kwargs),
        build_imaging_panel(),
        build_evidence_panel(graph_path=evidence_graph_path),
    ]
    return {"version": 1, "panels": panels}


def write_bootstrap_config(
    *,
    output_path: Path,
    handles_dir: Path | None = None,
    sample_size: int | None = None,
    evidence_graph_path: Path | None = None,
) -> dict[str, Any]:
    """Write the bootstrap configuration to ``output_path`` and return it."""

    config = build_bootstrap_config(
        handles_dir=handles_dir,
        sample_size=sample_size,
        evidence_graph_path=evidence_graph_path,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Workbench bootstrap configuration")
    parser.add_argument(
        "--handles-dir",
        type=Path,
        default=Path("app/data/handles"),
        help="Directory containing *.dhandle.json files",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=None,
        help="Override the default number of rows sampled per table",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("app/code/ui/workbench_bootstrap.json"),
        help="Where to write the bootstrap JSON",
    )
    parser.add_argument(
        "--evidence-graph",
        type=Path,
        default=None,
        help="Override the default evidence graph path",
    )
    args = parser.parse_args()

    write_bootstrap_config(
        output_path=args.out,
        handles_dir=args.handles_dir,
        sample_size=args.sample_size,
        evidence_graph_path=args.evidence_graph,
    )


if __name__ == "__main__":
    main()
