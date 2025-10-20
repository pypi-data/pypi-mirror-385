from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections.abc import Iterable  # noqa: TCH003
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from app.code.tools.promote import main as promote_main  # noqa: E402
from app.code.tools.vigilurl import build_vigil_url, load_manifest  # noqa: E402
from app.notes.arcade.score import score_submission  # noqa: E402

ARTIFACT_DIR = Path("app/code/artifacts/arcade")
RECEIPT_DIR = Path("app/code/receipts")


def _print_banner(message: str) -> None:
    print("=" * len(message))
    print(message)
    print("=" * len(message))


def _ensure_file(path: Path) -> None:
    if not path.exists():
        msg = f"Submission file not found: {path}"
        raise FileNotFoundError(msg)
    if path.suffix.lower() != ".csv":
        msg = "Submission must be a CSV file"
        raise ValueError(msg)


def run_workflow(submission: Path, threshold: float, skip_promote: bool) -> None:
    _ensure_file(submission)

    metrics = score_submission(submission)
    _print_banner("Arcade scoring summary")
    print(json.dumps(metrics.to_dict(), indent=2))

    if metrics.accuracy < threshold:
        msg = f"Accuracy {metrics.accuracy:.3f} < required threshold {threshold:.2f}"
        raise SystemExit(msg)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)

    target_csv = ARTIFACT_DIR / "predictions.csv"
    shutil.copyfile(submission, target_csv)

    metrics_path = ARTIFACT_DIR / "metrics.json"
    metrics_path.write_text(json.dumps(metrics.to_dict(), indent=2), encoding="utf-8")

    if skip_promote:
        print("Skipping promote step (requested via --skip-promote).")
        return

    cfg, _ = load_manifest()
    vigil_url = build_vigil_url(cfg)
    promote_main(str(ARTIFACT_DIR), str(RECEIPT_DIR), vigil_url)


def cli(argv: Iterable[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Evaluate and promote an arcade submission.")
    parser.add_argument("--submission", type=Path, required=True, help="Path to predictions CSV")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.9,
        help="Minimum accuracy required to promote (default: 0.9)",
    )
    parser.add_argument(
        "--skip-promote",
        action="store_true",
        help="Run scoring but skip the promote step",
    )
    args = parser.parse_args(argv)

    try:
        run_workflow(args.submission, args.threshold, args.skip_promote)
    except Exception as exc:  # noqa: BLE001 - surface friendly error
        print(f"Error: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    cli()
