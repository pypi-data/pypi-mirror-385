from __future__ import annotations

import json
from pathlib import Path  # noqa: TCH003
from subprocess import CompletedProcess

from vigil.tools import doctor


def _write_manifest(path: Path, digest: str, extensions: list[str] | None = None) -> tuple[str, list[str]]:
    """Write a minimal Vigil manifest and return capsule metadata."""

    if extensions is None:
        extensions = ["snakemake"]

    image = "ghcr.io/acme/capsule@" + digest

    lines = [
        "version: 1",
        "capsule:",
        f"  image: {image}",
    ]

    if extensions:
        lines.append("  extensions:")
        lines.extend(f"    - {ext}" for ext in extensions)
    else:
        lines.append("  extensions: []")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return image, extensions


def test_perform_checks_all_ok(tmp_path, monkeypatch) -> None:
    base = tmp_path
    manifest = base / "vigil.yaml"
    image, extensions = _write_manifest(manifest, "sha256:" + "a" * 64)

    workspace_spec = base / ".vigil" / "workspace.spec.json"
    workspace_spec.parent.mkdir(parents=True)
    workspace_spec.write_text(
        json.dumps({"capsule": {"image": image, "extensions": extensions}}, indent=2) + "\n",
        encoding="utf-8",
    )

    handles_dir = base / "app" / "data" / "handles"
    handles_dir.mkdir(parents=True)
    samples_dir = base / "app" / "data" / "samples"
    samples_dir.mkdir(parents=True)
    fallback = samples_dir / "data.csv"
    fallback.write_text("value\n1\n", encoding="utf-8")
    handle_payload = {
        "uri": "s3://example/demo.parquet",
        "format": "parquet",
        "offline_fallback": "app/data/samples/data.csv",
    }
    (handles_dir / "demo.dhandle.json").write_text(json.dumps(handle_payload), encoding="utf-8")

    profiles_dir = base / "app" / "code" / "configs" / "profiles"
    profiles_dir.mkdir(parents=True)
    (profiles_dir / "cpu.yaml").write_text("cores: 4\n", encoding="utf-8")

    monkeypatch.setattr(
        doctor,
        "_run_nvidia_smi",
        lambda: CompletedProcess(["nvidia-smi"], 0, "GPU available", ""),
    )

    results = doctor.perform_checks(base)
    status_by_code = {result.code: result.status for result in results}

    assert status_by_code == {
        "capsule_digest": doctor.Severity.OK,
        "workspace_spec_alignment": doctor.Severity.OK,
        "storage_reachability": doctor.Severity.OK,
        "gpu_availability": doctor.Severity.OK,
        "profile_paths": doctor.Severity.OK,
    }

    report = doctor.build_report(results)
    assert report["summary"]["status"] == doctor.Severity.OK.value
    assert report["summary"]["errors"] == 0


def test_perform_checks_with_errors(tmp_path, monkeypatch) -> None:
    base = tmp_path
    manifest = base / "vigil.yaml"
    _write_manifest(manifest, "latest")  # Missing digest indicator

    handles_dir = base / "app" / "data" / "handles"
    handles_dir.mkdir(parents=True)
    handle_payload = {
        "uri": "s3://example/demo.parquet",
        "format": "parquet",
        "offline_fallback": "app/data/samples/missing.csv",
    }
    (handles_dir / "demo.dhandle.json").write_text(json.dumps(handle_payload), encoding="utf-8")

    # Profiles directory intentionally omitted to trigger an error.

    monkeypatch.setattr(
        doctor,
        "_run_nvidia_smi",
        lambda: CompletedProcess(["nvidia-smi"], 1, "", "No devices were found"),
    )

    results = doctor.perform_checks(base)
    status_by_code = {result.code: result.status for result in results}

    assert status_by_code["capsule_digest"] == doctor.Severity.ERROR
    assert status_by_code["workspace_spec_alignment"] == doctor.Severity.ERROR
    assert status_by_code["storage_reachability"] == doctor.Severity.ERROR
    assert status_by_code["profile_paths"] == doctor.Severity.ERROR
    assert status_by_code["gpu_availability"] == doctor.Severity.WARNING

    summary = doctor.build_summary(results)
    assert summary["status"] == doctor.Severity.ERROR.value
    assert summary["errors"] >= 2
