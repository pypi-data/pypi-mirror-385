"""Aggregate per-site metrics with a DP-safe routine."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np


DEFAULT_EPSILON = 1.0
DEFAULT_MAX_RECORDS = 500
DEFAULT_MAX_POSITIVES = 500
DEFAULT_SEED = 1337


def _load_metrics(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as metrics_file:
        return json.load(metrics_file)


def _laplace_noise(scale: float, rng: np.random.Generator) -> float:
    return float(rng.laplace(0.0, scale))


def _clip(value: float, limit: float) -> float:
    return float(max(0.0, min(value, limit)))


def run(
    metric_paths: Iterable[str],
    out_path: str,
    epsilon: float = DEFAULT_EPSILON,
    max_records: int = DEFAULT_MAX_RECORDS,
    max_positive: int = DEFAULT_MAX_POSITIVES,
    seed: int = DEFAULT_SEED,
) -> None:
    if epsilon <= 0:
        msg = "Epsilon must be positive for the Laplace mechanism"
        raise ValueError(msg)

    metric_paths = [str(Path(path)) for path in metric_paths]
    metrics = [_load_metrics(Path(path)) for path in metric_paths]

    clipped_records = [_clip(site.get("records", 0), max_records) for site in metrics]
    clipped_positive = [_clip(site.get("positive_labels", 0), max_positive) for site in metrics]

    total_records = float(sum(clipped_records))
    total_positive = float(sum(clipped_positive))

    rng = np.random.default_rng(seed)
    sensitivity_records = float(max_records)
    sensitivity_positive = float(max_positive)

    noisy_records = total_records + _laplace_noise(sensitivity_records / epsilon, rng)
    noisy_positive = total_positive + _laplace_noise(sensitivity_positive / epsilon, rng)

    noisy_records = max(noisy_records, 1e-9)
    noisy_positive = max(noisy_positive, 0.0)
    conversion_rate = min(max(noisy_positive / noisy_records, 0.0), 1.0)

    receipt = {
        "pipeline": "federated",
        "aggregation": {
            "epsilon": epsilon,
            "delta": 0.0,
            "clip_records": max_records,
            "clip_positive_labels": max_positive,
            "noise_seed": seed,
            "mechanism": "laplace",
        },
        "inputs": metric_paths,
        "site_summaries": metrics,
        "noisy_totals": {
            "records": round(noisy_records, 6),
            "positive_labels": round(noisy_positive, 6),
            "conversion_rate": round(conversion_rate, 6),
        },
        "raw_totals": {
            "records": total_records,
            "positive_labels": total_positive,
        },
    }

    output_path = Path(out_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as receipt_file:
        json.dump(receipt, receipt_file, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Aggregate site metrics with DP noise")
    parser.add_argument("--metrics", nargs="+", required=True, help="Metric JSON files to aggregate")
    parser.add_argument("--out", required=True, help="Output path for the aggregated receipt")
    parser.add_argument("--epsilon", type=float, default=DEFAULT_EPSILON, help="Privacy budget epsilon")
    parser.add_argument(
        "--max-records", type=int, default=DEFAULT_MAX_RECORDS, help="Clip per-site record contributions"
    )
    parser.add_argument(
        "--max-positive",
        type=int,
        default=DEFAULT_MAX_POSITIVES,
        help="Clip per-site positive label contributions",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="PRNG seed for reproducible noise")
    args = parser.parse_args()

    run(args.metrics, args.out, args.epsilon, args.max_records, args.max_positive, args.seed)
