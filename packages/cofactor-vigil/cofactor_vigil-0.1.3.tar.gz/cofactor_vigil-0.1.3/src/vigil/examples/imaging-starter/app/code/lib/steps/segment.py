"""Data processing step for scientific analysis."""

from __future__ import annotations

import argparse
import json
from typing import Any

import polars as pl
import yaml


def run(
    table_handle_path: str, out_path: str, params_path: str = "app/code/configs/params.yaml"
) -> None:
    """Run data processing step on scientific data.

    Args:
        table_handle_path: Path to data handle JSON file
        out_path: Output path for processed data
        params_path: Path to parameters YAML file
    """
    # Load data handle
    with open(table_handle_path, encoding="utf-8") as f:
        handle: dict[str, Any] = json.load(f)

    offline_fallback = handle.get("offline_fallback")
    if offline_fallback:
        lazy_frame = pl.scan_csv(offline_fallback)
    else:
        uri = handle.get("uri")
        if not uri:
            raise ValueError("Data handle missing 'uri'")
        lazy_frame = pl.scan_parquet(uri)

    # Load parameters
    with open(params_path, encoding="utf-8") as f:
        params = yaml.safe_load(f) or {}

    threshold = float(params.get("process", {}).get("threshold", 0.6))

    result = (
        lazy_frame.with_columns(
            (pl.col("value") >= threshold)
            .cast(pl.Int8)
            .alias("processed_value")
        )
        .select(["x", "y", "processed_value"])
        .collect()
    )

    result.write_parquet(out_path)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--table", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--params", default="app/code/configs/params.yaml")
    a = p.parse_args()
    run(a.table, a.out, a.params)
