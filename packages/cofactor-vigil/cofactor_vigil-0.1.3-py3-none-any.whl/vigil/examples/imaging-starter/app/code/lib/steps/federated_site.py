"""Simulate a federated site run and emit per-site metrics and receipts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import polars as pl


def _load_handle(handle_path: Path) -> dict[str, Any]:
    with handle_path.open(encoding="utf-8") as handle_file:
        return json.load(handle_file)


def _read_site_sample(handle: dict[str, Any]) -> pl.DataFrame:
    offline_path = Path(handle["offline_fallback"])
    if not offline_path.exists():
        msg = f"Offline sample not found: {offline_path}"
        raise FileNotFoundError(msg)
    return pl.read_csv(offline_path)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run(site_id: str, handle_path: str, metrics_out: str, receipt_out: str, threshold: float = 0.5) -> None:
    """Simulate a site run by scoring rows and summarising metrics."""
    handle_file = Path(handle_path)
    metrics_path = Path(metrics_out)
    receipt_path = Path(receipt_out)

    handle = _load_handle(handle_file)
    offline_path = Path(handle["offline_fallback"])

    df = _read_site_sample(handle)

    records = df.height
    positive_labels = int(df["label"].sum())
    high_score = int((df["score"] >= threshold).sum())
    mean_score = float(df["score"].mean()) if records else 0.0

    metrics = {
        "site_id": site_id,
        "records": records,
        "positive_labels": positive_labels,
        "high_score": high_score,
        "mean_score": round(mean_score, 6),
        "threshold": threshold,
    }

    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", encoding="utf-8") as metrics_file:
        json.dump(metrics, metrics_file, indent=2)

    receipt = {
        "site_id": site_id,
        "handle": handle.get("uri", ""),
        "offline_fallback": str(offline_path),
        "sample_digest": _sha256_file(offline_path),
        "metrics_path": str(metrics_path),
        "metrics": metrics,
    }

    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with receipt_path.open("w", encoding="utf-8") as receipt_file:
        json.dump(receipt, receipt_file, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate a federated site run")
    parser.add_argument("--site", required=True, help="Site identifier (e.g. site_a)")
    parser.add_argument("--handle", required=True, help="Path to the site's DataHandle JSON")
    parser.add_argument("--metrics-out", required=True, help="Where to write the metrics JSON")
    parser.add_argument("--receipt-out", required=True, help="Where to write the site receipt JSON")
    parser.add_argument("--threshold", type=float, default=0.5, help="Score threshold for high-score counts")
    args = parser.parse_args()

    run(args.site, args.handle, args.metrics_out, args.receipt_out, args.threshold)
