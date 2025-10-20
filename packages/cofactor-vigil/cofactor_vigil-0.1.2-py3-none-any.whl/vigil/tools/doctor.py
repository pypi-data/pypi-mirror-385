"""Repository health checks for Vigil capsules.

This module implements a small "doctor" utility that validates several
repository conventions before running larger pipelines.  The checks focus on
four main areas:

* Capsule digests – ensure ``vigil.yaml`` pins an image by digest.
* Storage reachability – verify local offline fallbacks for data handles.
* GPU availability – surface whether ``nvidia-smi`` can detect a device.
* Profile paths – confirm Snakemake profile configuration files exist.

The CLI exposes a ``doctor`` command (see ``pyproject.toml``) that prints a
structured report either as JSON or as a simple table.  Downstream tooling can
use the JSON payload to make decisions based on the status codes while humans
can quickly eyeball the table view.
"""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Iterable  # noqa: TCH003
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

try:  # pragma: no cover - import resolution differs for script/module runs
    from .workspace_spec import (
        MANIFEST_NAME,
        WORKSPACE_SPEC_PATH,
        load_manifest,
        load_workspace_spec,
    )
except ImportError:  # pragma: no cover - fallback for ``python app/code/tools/doctor.py``
    from workspace_spec import (  # type: ignore
        MANIFEST_NAME,
        WORKSPACE_SPEC_PATH,
        load_manifest,
        load_workspace_spec,
    )


class Severity(str, Enum):
    """Represents the severity of a health-check outcome."""

    OK = "ok"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class CheckResult:
    """A structured result for an individual health check."""

    code: str
    status: Severity
    message: str
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "code": self.code,
            "status": self.status.value,
            "message": self.message,
        }
        if self.details:
            data["details"] = self.details
        return data


class OutputFormat(str, Enum):
    """Valid output formats for the CLI."""

    JSON = "json"
    TABLE = "table"


_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-fA-F]{64}$")


def check_capsule_digest(base_path: Path, allow_unpinned: bool = False) -> CheckResult:
    """Validate that the Vigil capsule image uses an immutable digest."""

    manifest = load_manifest(base_path)
    manifest_path = base_path / MANIFEST_NAME
    if not manifest:
        return CheckResult(
            code="capsule_digest",
            status=Severity.ERROR,
            message=f"Missing manifest: {manifest_path}",
        )

    capsule = manifest.get("capsule", {})
    image = capsule.get("image") if isinstance(capsule, dict) else None
    if not image or "@" not in image:
        severity = Severity.WARNING if allow_unpinned else Severity.ERROR
        return CheckResult(
            code="capsule_digest",
            status=severity,
            message="Capsule image is not pinned by digest",
        )

    digest = image.split("@", 1)[1]
    if not _DIGEST_PATTERN.match(digest):
        severity = Severity.WARNING if allow_unpinned else Severity.ERROR
        return CheckResult(
            code="capsule_digest",
            status=severity,
            message=f"Capsule digest has unexpected format: {digest}",
        )

    return CheckResult(
        code="capsule_digest",
        status=Severity.OK,
        message="Capsule image is pinned by a valid sha256 digest",
        details={"image": image, "digest": digest},
    )


def _resolve_spec_path(base_path: Path) -> Path:
    path = WORKSPACE_SPEC_PATH
    if not path.is_absolute():
        return (base_path / path).resolve()
    return path


def check_workspace_spec_alignment(base_path: Path) -> CheckResult:
    """Ensure the workspace spec mirrors capsule metadata from the manifest."""

    manifest = load_manifest(base_path)
    manifest_path = base_path / MANIFEST_NAME
    if not manifest:
        return CheckResult(
            code="workspace_spec_alignment",
            status=Severity.ERROR,
            message=f"Missing manifest: {manifest_path}",
        )

    try:
        spec = load_workspace_spec(base_path)
    except ValueError as exc:
        return CheckResult(
            code="workspace_spec_alignment",
            status=Severity.ERROR,
            message=str(exc),
        )

    spec_path = _resolve_spec_path(base_path)
    if not spec:
        return CheckResult(
            code="workspace_spec_alignment",
            status=Severity.ERROR,
            message=f"Missing workspace spec: {spec_path}",
        )

    capsule_manifest = manifest.get("capsule")
    capsule_spec = spec.get("capsule")
    if not isinstance(capsule_manifest, dict) or not isinstance(capsule_spec, dict):
        return CheckResult(
            code="workspace_spec_alignment",
            status=Severity.ERROR,
            message="Capsule sections in manifest or workspace spec are malformed",
        )

    manifest_image = capsule_manifest.get("image")
    spec_image = capsule_spec.get("image")
    manifest_extensions = capsule_manifest.get("extensions")
    spec_extensions = capsule_spec.get("extensions")

    mismatches: dict[str, Any] = {}
    if not manifest_image:
        mismatches["manifest_image"] = "missing"
    if manifest_image != spec_image:
        mismatches["image"] = {"manifest": manifest_image, "workspace": spec_image}

    if not isinstance(manifest_extensions, list):
        mismatches["manifest_extensions"] = "missing"
    if not isinstance(spec_extensions, list):
        mismatches["workspace_extensions"] = "missing"
    elif isinstance(manifest_extensions, list) and spec_extensions != manifest_extensions:
        mismatches["extensions"] = {
            "manifest": manifest_extensions,
            "workspace": spec_extensions,
        }

    if mismatches:
        return CheckResult(
            code="workspace_spec_alignment",
            status=Severity.ERROR,
            message="Workspace spec is out of sync with vigil.yaml",
            details=mismatches,
        )

    return CheckResult(
        code="workspace_spec_alignment",
        status=Severity.OK,
        message="Workspace spec capsule metadata matches vigil.yaml",
        details={
            "image": manifest_image,
            "extensions": manifest_extensions,
            "spec_path": spec_path.as_posix(),
        },
    )


def _load_data_handle(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)  # type: ignore[no-any-return]


def check_storage_reachability(base_path: Path) -> CheckResult:
    """Check that all data handles provide reachable offline fallbacks."""

    handles_dir = base_path / "app" / "data" / "handles"
    if not handles_dir.exists():
        return CheckResult(
            code="storage_reachability",
            status=Severity.WARNING,
            message=f"Data handles directory missing: {handles_dir}",
        )

    checked = 0
    missing_fallbacks: list[str] = []
    malformed: list[str] = []
    for handle_path in sorted(handles_dir.glob("*.dhandle.json")):
        checked += 1
        try:
            payload = _load_data_handle(handle_path)
        except json.JSONDecodeError:
            malformed.append(handle_path.name)
            continue

        fallback = payload.get("offline_fallback")
        if not fallback:
            missing_fallbacks.append(handle_path.name)
            continue

        fallback_path = (base_path / fallback).resolve()
        if not fallback_path.exists():
            missing_fallbacks.append(handle_path.name)

    if malformed:
        return CheckResult(
            code="storage_reachability",
            status=Severity.ERROR,
            message="Malformed data handle definitions",
            details={"malformed": malformed},
        )

    if missing_fallbacks:
        return CheckResult(
            code="storage_reachability",
            status=Severity.ERROR,
            message="Offline fallbacks are missing",
            details={
                "handles_missing_fallbacks": missing_fallbacks,
                "checked": checked,
            },
        )

    return CheckResult(
        code="storage_reachability",
        status=Severity.OK,
        message=f"All {checked} data handles have reachable offline fallbacks",
        details={"checked": checked},
    )


def _run_nvidia_smi() -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603  # External command is deliberate
        ["nvidia-smi"],
        capture_output=True,
        text=True,
        check=False,
        timeout=5,
    )


def check_gpu_availability() -> CheckResult:
    """Determine if a CUDA-capable GPU is visible via ``nvidia-smi``."""

    try:
        result = _run_nvidia_smi()
    except FileNotFoundError:
        return CheckResult(
            code="gpu_availability",
            status=Severity.WARNING,
            message="nvidia-smi not found; GPU availability unknown",
        )
    except subprocess.SubprocessError as exc:  # pragma: no cover - defensive
        return CheckResult(
            code="gpu_availability",
            status=Severity.WARNING,
            message=f"nvidia-smi failed: {exc}",
        )

    if result.returncode == 0:
        return CheckResult(
            code="gpu_availability",
            status=Severity.OK,
            message="CUDA GPU detected via nvidia-smi",
        )

    return CheckResult(
        code="gpu_availability",
        status=Severity.WARNING,
        message="nvidia-smi reported no GPU",
        details={"stderr": result.stderr.strip()},
    )


def check_profile_paths(base_path: Path) -> CheckResult:
    """Ensure that Snakemake profile configuration files exist."""

    profiles_dir = base_path / "app" / "code" / "configs" / "profiles"
    if not profiles_dir.exists():
        return CheckResult(
            code="profile_paths",
            status=Severity.ERROR,
            message=f"Profiles directory missing: {profiles_dir}",
        )

    profiles = sorted(p for p in profiles_dir.glob("*.yaml") if p.is_file())
    if not profiles:
        return CheckResult(
            code="profile_paths",
            status=Severity.ERROR,
            message="No Snakemake profile YAML files found",
        )

    return CheckResult(
        code="profile_paths",
        status=Severity.OK,
        message=f"Found {len(profiles)} Snakemake profile(s)",
        details={"profiles": [p.as_posix() for p in profiles]},
    )


def perform_checks(base_path: Path, allow_unpinned: bool = False) -> list[CheckResult]:
    """Run all doctor checks for the given repository base path."""

    return [
        check_capsule_digest(base_path, allow_unpinned=allow_unpinned),
        check_workspace_spec_alignment(base_path),
        check_storage_reachability(base_path),
        check_gpu_availability(),
        check_profile_paths(base_path),
    ]


def build_summary(results: Iterable[CheckResult]) -> dict[str, Any]:
    """Aggregate check severities into a single summary mapping."""

    counts = {Severity.OK: 0, Severity.WARNING: 0, Severity.ERROR: 0}
    worst = Severity.OK
    for result in results:
        counts[result.status] += 1
        if result.status == Severity.ERROR:
            worst = Severity.ERROR
        elif result.status == Severity.WARNING and worst != Severity.ERROR:
            worst = Severity.WARNING

    return {
        "status": worst.value,
        "ok": counts[Severity.OK],
        "warnings": counts[Severity.WARNING],
        "errors": counts[Severity.ERROR],
    }


def build_report(results: Iterable[CheckResult]) -> dict[str, Any]:
    """Construct the full JSON report returned by the CLI."""

    results_list = list(results)
    return {
        "checks": [result.to_dict() for result in results_list],
        "summary": build_summary(results_list),
    }


def _print_table(report: dict[str, Any]) -> None:
    table = Table(title="Vigil Doctor Report")
    table.add_column("Code", style="bold")
    table.add_column("Status")
    table.add_column("Message", overflow="fold")
    for check in report["checks"]:
        table.add_row(check["code"], check["status"], check["message"])

    summary = report["summary"]
    footer = (
        f"Overall: {summary['status']} • "
        f"ok={summary['ok']} warning={summary['warnings']} error={summary['errors']}"
    )
    console = Console()
    console.print(table)
    console.print(footer)


def run_command(
    output_format: OutputFormat = typer.Option(OutputFormat.JSON, case_sensitive=False),
    base_path: Path = typer.Option(Path("."), exists=True, file_okay=False, resolve_path=True),
    allow_unpinned: bool = typer.Option(
        False, "--allow-unpinned", help="Allow unpinned capsule images (for development only)"
    ),
) -> None:
    """Execute doctor checks and print the report."""

    results = perform_checks(base_path, allow_unpinned=allow_unpinned)
    report = build_report(results)

    if output_format == OutputFormat.JSON:
        typer.echo(json.dumps(report, indent=2))
    else:
        _print_table(report)

    exit_code = 0 if report["summary"]["status"] != Severity.ERROR.value else 1
    raise typer.Exit(code=exit_code)


def main() -> None:
    """Entrypoint compatible with ``python app/code/tools/doctor.py``."""

    typer.run(run_command)


if __name__ == "__main__":
    main()
