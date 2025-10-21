"""Minimal processing step."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def process_data(input_path: Path, output_path: Path, params: dict) -> None:
    """Process data with a simple threshold filter.

    Args:
        input_path: Path to input CSV or Parquet file
        output_path: Path to output Parquet file
        params: Parameters dict with 'threshold' key
    """
    # Load data
    if input_path.suffix == ".parquet":
        df = pd.read_parquet(input_path)
    else:
        df = pd.read_csv(input_path)

    # Apply threshold filter
    threshold = params.get("threshold", 0.5)
    df_filtered = df[df["value"] >= threshold].copy()

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_filtered.to_parquet(output_path, index=False)

    print(f"Processed {len(df)} rows -> {len(df_filtered)} rows (threshold={threshold})")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python process.py <input> <output> <params_json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    params = json.loads(sys.argv[3])

    process_data(input_path, output_path, params)
