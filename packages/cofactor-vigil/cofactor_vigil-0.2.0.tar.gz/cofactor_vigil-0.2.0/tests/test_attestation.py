"""Tests for SLSA provenance and attestation generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from vigil.tools import attestation


@pytest.fixture
def sample_receipt(tmp_path: Path) -> Path:
    """Create a sample receipt file for testing."""
    receipt_data = {
        "issuer": "Vigil",
        "runletId": "rl_1234567890",
        "vigilUrl": "vigil://example/test@main",
        "gitRef": "abc123",
        "outputs": [],
    }
    receipt_path = tmp_path / "receipt_test.json"
    receipt_path.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")
    return receipt_path


def test_compute_sha256(tmp_path: Path) -> None:
    """Test SHA256 computation."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world", encoding="utf-8")

    digest = attestation.compute_sha256(test_file)

    # Verify it's a hex string
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_compute_content_sha256() -> None:
    """Test SHA256 computation from content."""
    content = "hello world"
    digest = attestation.compute_content_sha256(content)

    # Verify it's a hex string
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)

    # Test with bytes
    digest2 = attestation.compute_content_sha256(content.encode("utf-8"))
    assert digest == digest2


def test_generate_attestation_basic(sample_receipt: Path) -> None:
    """Test basic attestation generation."""
    statement = attestation.generate_attestation(
        receipt_path=sample_receipt,
        vigil_url="vigil://example/test@main",
        git_ref="abc123",
        capsule_digest="sha256:deadbeef",
        runlet_id="rl_1234567890",
        started_at="2025-01-20T12:00:00Z",
        finished_at="2025-01-20T12:05:00Z",
    )

    # Verify in-toto statement structure
    assert statement["_type"] == "https://in-toto.io/Statement/v1"
    assert statement["predicateType"] == "https://slsa.dev/provenance/v1"

    # Verify subject
    assert len(statement["subject"]) == 1
    subject = statement["subject"][0]
    assert subject["name"] == "receipt_test.json"
    assert "sha256" in subject["digest"]
    assert len(subject["digest"]["sha256"]) == 64


def test_generate_attestation_slsa_structure(sample_receipt: Path) -> None:
    """Test SLSA provenance structure in attestation."""
    outputs = [
        {"uri": "output1.txt", "checksum": "sha256:abc123"},
        {"uri": "output2.txt", "checksum": "sha256:def456"},
    ]

    statement = attestation.generate_attestation(
        receipt_path=sample_receipt,
        vigil_url="vigil://example/test@main",
        git_ref="abc123",
        capsule_digest="sha256:deadbeef",
        runlet_id="rl_1234567890",
        started_at="2025-01-20T12:00:00Z",
        finished_at="2025-01-20T12:05:00Z",
        profile="cpu",
        cores=4,
        outputs=outputs,
    )

    predicate = statement["predicate"]

    # Verify buildDefinition
    assert "buildDefinition" in predicate
    build_def = predicate["buildDefinition"]
    assert build_def["buildType"] == "https://vigil.science/build/v1"

    # Verify external parameters
    ext_params = build_def["externalParameters"]
    assert ext_params["vigilUrl"] == "vigil://example/test@main"
    assert ext_params["gitRef"] == "abc123"
    assert ext_params["inputs"] == []

    # Verify internal parameters
    int_params = build_def["internalParameters"]
    assert int_params["capsuleDigest"] == "sha256:deadbeef"
    assert int_params["profile"] == "cpu"
    assert int_params["cores"] == 4

    # Verify resolved dependencies
    deps = build_def["resolvedDependencies"]
    assert len(deps) == 2
    assert deps[0]["uri"] == "output1.txt"
    assert deps[0]["digest"]["sha256"] == "abc123"
    assert deps[1]["uri"] == "output2.txt"
    assert deps[1]["digest"]["sha256"] == "def456"


def test_generate_attestation_run_details(sample_receipt: Path) -> None:
    """Test runDetails in SLSA provenance."""
    byproducts = [
        {"uri": "metrics.json", "checksum": "sha256:metrics123"},
    ]

    statement = attestation.generate_attestation(
        receipt_path=sample_receipt,
        vigil_url="vigil://example/test@main",
        git_ref="abc123",
        capsule_digest="sha256:deadbeef",
        runlet_id="rl_1234567890",
        started_at="2025-01-20T12:00:00Z",
        finished_at="2025-01-20T12:05:00Z",
        byproducts=byproducts,
    )

    predicate = statement["predicate"]

    # Verify runDetails
    assert "runDetails" in predicate
    run_details = predicate["runDetails"]

    # Verify builder
    builder = run_details["builder"]
    assert builder["id"] == "https://vigil.science/builder/v1"

    # Verify metadata
    metadata = run_details["metadata"]
    assert metadata["invocationId"] == "rl_1234567890"
    assert metadata["startedOn"] == "2025-01-20T12:00:00Z"
    assert metadata["finishedOn"] == "2025-01-20T12:05:00Z"

    # Verify byproducts
    bp_list = run_details["byproducts"]
    assert len(bp_list) == 1
    assert bp_list[0]["name"] == "metrics.json"
    assert bp_list[0]["digest"]["sha256"] == "metrics123"


def test_save_attestation(sample_receipt: Path, tmp_path: Path) -> None:
    """Test saving attestation to file."""
    statement = attestation.generate_attestation(
        receipt_path=sample_receipt,
        vigil_url="vigil://example/test@main",
        git_ref="abc123",
        capsule_digest="sha256:deadbeef",
        runlet_id="rl_1234567890",
        started_at="2025-01-20T12:00:00Z",
        finished_at="2025-01-20T12:05:00Z",
    )

    output_path = tmp_path / "attestation.json"
    attestation.save_attestation(statement, output_path)

    # Verify file exists and is valid JSON
    assert output_path.exists()
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded == statement
