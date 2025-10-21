from __future__ import annotations

import argparse
import csv
import json
from collections.abc import Iterable  # noqa: TCH003
from dataclasses import dataclass
from pathlib import Path

from app.code.lib.paths import project_path

DATA_PATH = project_path("app/data/samples/data.csv")


@dataclass
class Metrics:
    n: int
    tp: int
    tn: int
    fp: int
    fn: int
    accuracy: float
    precision: float
    recall: float
    f1: float

    def to_dict(self) -> dict[str, float | int]:
        return {
            "n": self.n,
            "tp": self.tp,
            "tn": self.tn,
            "fp": self.fp,
            "fn": self.fn,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
        }


def _safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _load_ground_truth(path: Path = DATA_PATH) -> dict[int, int]:
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if "x" not in reader.fieldnames or "ground_truth" not in reader.fieldnames:
            msg = "Ground truth CSV must contain 'x' and 'ground_truth' columns"
            raise ValueError(msg)
        truth: dict[int, int] = {}
        for row in reader:
            truth[int(row["x"])] = int(row["ground_truth"])
    if not truth:
        raise ValueError(f"No rows found in ground truth CSV: {path}")
    return truth


def _load_predictions(path: Path) -> dict[int, int]:
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or {"x", "prediction"} - set(reader.fieldnames):
            msg = "Submission must contain 'x' and 'prediction' columns"
            raise ValueError(msg)
        predictions: dict[int, int] = {}
        for row in reader:
            x = int(row["x"])
            predictions[x] = int(row["prediction"])
    if not predictions:
        raise ValueError(f"No rows found in submission CSV: {path}")
    return predictions


def score_submission(path: Path) -> Metrics:
    truth = _load_ground_truth()
    predictions = _load_predictions(path)

    missing = set(truth) - set(predictions)
    if missing:
        missing_display = ", ".join(str(x) for x in sorted(missing))
        msg = f"Submission missing predictions for x values: {missing_display}"
        raise ValueError(msg)

    extra = set(predictions) - set(truth)
    if extra:
        extra_display = ", ".join(str(x) for x in sorted(extra))
        msg = f"Submission contains unknown x values: {extra_display}"
        raise ValueError(msg)

    tp = tn = fp = fn = 0
    for x, label in truth.items():
        pred = predictions[x]
        if pred not in (0, 1):
            raise ValueError(f"Prediction for x={x} must be 0 or 1, got {pred}")
        if label == 1 and pred == 1:
            tp += 1
        elif label == 0 and pred == 0:
            tn += 1
        elif label == 0 and pred == 1:
            fp += 1
        else:
            fn += 1

    n = len(truth)
    accuracy = _safe_div(tp + tn, n)
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _safe_div(2 * precision * recall, precision + recall)
    return Metrics(n=n, tp=tp, tn=tn, fp=fp, fn=fn, accuracy=accuracy, precision=precision, recall=recall, f1=f1)


def _format_metrics(metrics: Metrics) -> str:
    lines: list[str] = ["Metric        Value", "---------------------"]
    lines.append(f"N             {metrics.n}")
    lines.append(f"TP            {metrics.tp}")
    lines.append(f"TN            {metrics.tn}")
    lines.append(f"FP            {metrics.fp}")
    lines.append(f"FN            {metrics.fn}")
    lines.append(f"Accuracy      {metrics.accuracy:.3f}")
    lines.append(f"Precision     {metrics.precision:.3f}")
    lines.append(f"Recall        {metrics.recall:.3f}")
    lines.append(f"F1            {metrics.f1:.3f}")
    return "\n".join(lines)


def main(submission: Path, metrics_out: Path | None) -> None:
    metrics = score_submission(submission)
    print(_format_metrics(metrics))
    if metrics_out is not None:
        metrics_out.write_text(json.dumps(metrics.to_dict(), indent=2), encoding="utf-8")


def cli(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Score a Vigil arcade submission.")
    parser.add_argument("submission", type=Path, help="Path to CSV with x,prediction columns")
    parser.add_argument(
        "--metrics-out",
        type=Path,
        default=None,
        help="Optional path to write metrics.json compatible output",
    )
    args = parser.parse_args(argv)
    main(args.submission, args.metrics_out)


if __name__ == "__main__":
    cli()
