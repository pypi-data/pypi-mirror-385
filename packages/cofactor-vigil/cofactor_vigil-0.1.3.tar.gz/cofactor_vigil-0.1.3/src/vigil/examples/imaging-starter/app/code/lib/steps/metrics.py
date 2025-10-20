"""Metrics calculation step for scientific evaluation."""

from __future__ import annotations

import argparse
import json
from typing import Any

import polars as pl


def run(processed_path: str, handle_path: str, out_path: str) -> None:
    """Calculate metrics against ground truth.

    Args:
        processed_path: Path to processed data
        handle_path: Path to data handle JSON file
        out_path: Output path for metrics JSON
    """
    # Load processed data
    processed = pl.scan_parquet(processed_path)

    # Load ground truth data
    with open(handle_path, encoding="utf-8") as f:
        handle: dict[str, Any] = json.load(f)
    base = (
        pl.scan_csv(handle["offline_fallback"])
        .select(["x", "y", "ground_truth"])
    )

    # Merge and calculate metrics
    df = processed.join(base, on=["x", "y"], how="left").collect()

    tp = (df["processed_value"] == 1) & (df["ground_truth"] == 1)
    tn = (df["processed_value"] == 0) & (df["ground_truth"] == 0)
    fp = (df["processed_value"] == 1) & (df["ground_truth"] == 0)
    fn = (df["processed_value"] == 0) & (df["ground_truth"] == 1)

    tp_count = int(tp.sum())
    tn_count = int(tn.sum())
    fp_count = int(fp.sum())
    fn_count = int(fn.sum())
    total = df.height

    precision = tp_count / (tp_count + fp_count) if (tp_count + fp_count) else 0.0
    recall = tp_count / (tp_count + fn_count) if (tp_count + fn_count) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    accuracy = (tp_count + tn_count) / total if total else 0.0

    metrics = {
        "n": total,
        "tp": tp_count,
        "tn": tn_count,
        "fp": fp_count,
        "fn": fn_count,
        "accuracy": round(accuracy, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--processed", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--table_handle", default="app/data/handles/data.parquet.dhandle.json")
    a = p.parse_args()
    run(a.processed, a.table_handle, a.out)
