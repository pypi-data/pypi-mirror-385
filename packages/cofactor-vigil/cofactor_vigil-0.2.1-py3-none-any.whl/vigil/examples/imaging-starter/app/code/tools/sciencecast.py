"""Generate Sciencecast timeline JSON for the latest pipeline run."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class TimelineConfig:
    """Configuration inputs for generating a timeline."""

    metrics_path: Path
    processed_path: Path
    output_path: Path
    pipeline_name: str
    schema_path: Path | None = None


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _file_summary(path: Path) -> dict[str, Any]:
    stats = path.stat()
    return {
        "path": str(path),
        "size_bytes": stats.st_size,
        "modified_at": datetime.fromtimestamp(stats.st_mtime, tz=UTC).isoformat(),
    }


def build_timeline(config: TimelineConfig) -> dict[str, Any]:
    metrics = _load_json(config.metrics_path)

    processed_details = _file_summary(config.processed_path)
    metrics_details = {
        "path": str(config.metrics_path),
        "metrics": metrics,
    }

    run_id = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    generated_at = datetime.now(tz=UTC).isoformat()

    events = [
        {
            "id": "ingest",
            "offset_seconds": 0.0,
            "label": "Load microscopy handle",
            "narration": "Retrieve offline sample from the typed data handle and stage it for processing.",
            "details": {
                "input_handle": "app/data/handles/data.parquet.dhandle.json",
            },
        },
        {
            "id": "segment",
            "offset_seconds": 4.0,
            "label": "Segment tiles",
            "narration": "Run the segmentation step to derive processed tiles ready for downstream analysis.",
            "details": processed_details,
        },
        {
            "id": "metrics",
            "offset_seconds": 12.0,
            "label": "Score precision/recall",
            "narration": "Compare processed output against the ground truth and report accuracy metrics.",
            "details": metrics_details,
        },
    ]

    timeline: dict[str, Any] = {
        "metadata": {
            "run_id": run_id,
            "generated_at": generated_at,
            "pipeline": config.pipeline_name,
            "inputs": ["app/data/handles/data.parquet.dhandle.json", "app/code/configs/params.yaml"],
            "artifacts": {
                "processed": str(config.processed_path),
                "metrics": str(config.metrics_path),
            },
        },
        "events": events,
    }

    return timeline


def write_timeline(config: TimelineConfig) -> None:
    timeline = build_timeline(config)
    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    with config.output_path.open("w", encoding="utf-8") as handle:
        json.dump(timeline, handle, indent=2)
        handle.write("\n")


def parse_args() -> TimelineConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", required=True, type=Path, help="Path to metrics JSON produced by the pipeline")
    parser.add_argument("--processed", required=True, type=Path, help="Path to processed parquet artifact")
    parser.add_argument("--out", required=True, type=Path, help="Where to write the Sciencecast timeline JSON")
    parser.add_argument(
        "--pipeline-name",
        default="app/code/pipelines/Snakefile",
        help="Identifier for the pipeline run to include in metadata",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        help="Optional path to the timeline schema. Used for validation tooling in future iterations.",
    )
    args = parser.parse_args()
    return TimelineConfig(
        metrics_path=args.metrics,
        processed_path=args.processed,
        output_path=args.out,
        pipeline_name=args.pipeline_name,
        schema_path=args.schema,
    )


def main() -> None:
    config = parse_args()
    write_timeline(config)


if __name__ == "__main__":
    main()
