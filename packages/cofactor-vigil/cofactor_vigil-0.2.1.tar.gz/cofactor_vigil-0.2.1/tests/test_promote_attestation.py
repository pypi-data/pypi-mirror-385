"""Integration tests for promote with attestation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from vigil.tools import promote


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure time-based environment variables are unset for determinism."""
    monkeypatch.delenv("RUN_STARTED_AT", raising=False)
    monkeypatch.delenv("VIGIL_SIGNING_KEY", raising=False)


def test_promote_with_attestation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test promote generates attestation when --attest is used."""
    # Setup
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    (artifact_dir / "metrics.json").write_text(json.dumps({"accuracy": 0.95}), encoding="utf-8")
    (artifact_dir / "output.txt").write_text("test output", encoding="utf-8")

    manifest_data = {
        "capsule": {
            "image": "ghcr.io/example/capsule@sha256:deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        }
    }
    (tmp_path / "vigil.yaml").write_text(yaml.safe_dump(manifest_data), encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    # Mock time and git
    fixed_epoch = 1_700_000_000
    fixed_struct = promote.time.gmtime(fixed_epoch)
    monkeypatch.setattr(promote.time, "time", lambda: fixed_epoch)
    monkeypatch.setattr(promote.time, "gmtime", lambda: fixed_struct)
    monkeypatch.setattr(
        promote.subprocess,
        "check_output",
        lambda *_, **__: "abcdef1234567890abcdef1234567890abcdef12\n",
    )

    # Run promote with attestation
    out_dir = tmp_path / "receipts"
    promote.main(
        indir=str(artifact_dir),
        outdir=str(out_dir),
        vigil_url="vigil://example/test@main",
        profile="cpu",
        attestation_blob=None,
        attest=True,
    )

    # Verify receipt was created
    receipt_files = list(out_dir.glob("receipt_*.json"))
    assert len(receipt_files) == 1
    receipt_path = receipt_files[0]

    # Verify attestation was created
    attestation_files = list(out_dir.glob("attestation_*.json"))
    assert len(attestation_files) == 1
    attestation_path = attestation_files[0]

    # Load and verify attestation structure
    attestation = json.loads(attestation_path.read_text(encoding="utf-8"))

    assert attestation["_type"] == "https://in-toto.io/Statement/v1"
    assert attestation["predicateType"] == "https://slsa.dev/provenance/v1"

    # Verify subject points to receipt
    assert len(attestation["subject"]) == 1
    subject = attestation["subject"][0]
    assert subject["name"] == receipt_path.name
    assert "sha256" in subject["digest"]

    # Verify predicate structure
    predicate = attestation["predicate"]
    assert "buildDefinition" in predicate
    assert "runDetails" in predicate

    # Verify buildDefinition
    build_def = predicate["buildDefinition"]
    assert build_def["buildType"] == "https://vigil.science/build/v1"

    ext_params = build_def["externalParameters"]
    assert ext_params["vigilUrl"] == "vigil://example/test@main"
    assert ext_params["gitRef"] == "abcdef1234567890abcdef1234567890abcdef12"

    int_params = build_def["internalParameters"]
    assert (
        int_params["capsuleDigest"]
        == "sha256:deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    )
    assert int_params["profile"] == "cpu"

    # Verify resolved dependencies (outputs)
    deps = build_def["resolvedDependencies"]
    assert len(deps) == 2
    dep_uris = {dep["uri"] for dep in deps}
    assert any("metrics.json" in uri for uri in dep_uris)
    assert any("output.txt" in uri for uri in dep_uris)

    # Verify runDetails
    run_details = predicate["runDetails"]
    builder = run_details["builder"]
    assert builder["id"] == "https://vigil.science/builder/v1"

    metadata = run_details["metadata"]
    assert metadata["invocationId"].startswith("rl_")
    assert "startedOn" in metadata
    assert "finishedOn" in metadata

    # Verify byproducts (metrics)
    byproducts = run_details["byproducts"]
    assert len(byproducts) == 1
    assert "metrics.json" in byproducts[0]["name"]


def test_promote_without_attestation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test promote does not generate attestation when --attest is not used."""
    # Setup
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir()
    (artifact_dir / "output.txt").write_text("test", encoding="utf-8")

    manifest_data = {"capsule": {"image": "ghcr.io/example/capsule@sha256:deadbeef"}}
    (tmp_path / "vigil.yaml").write_text(yaml.safe_dump(manifest_data), encoding="utf-8")

    monkeypatch.chdir(tmp_path)

    # Mock time and git
    fixed_epoch = 1_700_000_000
    fixed_struct = promote.time.gmtime(fixed_epoch)
    monkeypatch.setattr(promote.time, "time", lambda: fixed_epoch)
    monkeypatch.setattr(promote.time, "gmtime", lambda: fixed_struct)
    monkeypatch.setattr(promote.subprocess, "check_output", lambda *_, **__: "abc123\n")

    # Run promote without attestation
    out_dir = tmp_path / "receipts"
    promote.main(
        indir=str(artifact_dir),
        outdir=str(out_dir),
        vigil_url="vigil://example/test",
        profile=None,
        attestation_blob=None,
        attest=False,
    )

    # Verify receipt was created
    receipt_files = list(out_dir.glob("receipt_*.json"))
    assert len(receipt_files) == 1

    # Verify no attestation was created
    attestation_files = list(out_dir.glob("attestation_*.json"))
    assert len(attestation_files) == 0
