"""Integration test for receipt index happy path.

This test verifies that:
1. vigil promote always updates app/code/receipts/index.json
2. vigil anchor updates index.json with anchor metadata
3. vigil anchor --record-proof annotates proofs in index.json
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from vigil.tools import anchor, promote, receipt_index


@pytest.fixture()
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    """Set up a complete workspace with all necessary directories."""
    monkeypatch.chdir(tmp_path)

    # Create directory structure
    artifacts_dir = tmp_path / "app/code/artifacts"
    receipts_dir = tmp_path / "app/code/receipts"
    anchors_dir = tmp_path / "app/code/anchors"

    artifacts_dir.mkdir(parents=True)
    receipts_dir.mkdir(parents=True)
    anchors_dir.mkdir(parents=True)

    # Create a simple vigil.yaml
    (tmp_path / "vigil.yaml").write_text(
        """
version: 1
org: test-org
project: test-project
capsule:
  image: ghcr.io/test/capsule@sha256:deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef
""",
        encoding="utf-8",
    )

    # Create sample artifacts
    (artifacts_dir / "metrics.json").write_text(
        json.dumps({"accuracy": 0.95, "precision": 0.92}), encoding="utf-8"
    )
    (artifacts_dir / "output.csv").write_text("id,value\n1,100\n2,200\n", encoding="utf-8")

    return {
        "root": tmp_path,
        "artifacts": artifacts_dir,
        "receipts": receipts_dir,
        "anchors": anchors_dir,
        "index": receipts_dir / "index.json",
    }


def test_promote_creates_and_updates_index(
    workspace: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that promote creates index.json if it doesn't exist and updates it."""
    # Mock time for deterministic output
    fixed_epoch = 1_700_000_000
    promote.time.gmtime(fixed_epoch)
    monkeypatch.setattr(promote.time, "time", lambda: fixed_epoch)
    monkeypatch.setattr(promote.time, "strftime", lambda fmt, t: "2023-11-14T22:13:20Z")
    monkeypatch.setattr(
        promote.subprocess,
        "check_output",
        lambda *_, **__: "abc123def456abc123def456abc123def456abc1\n",
    )

    # Verify index doesn't exist yet
    assert not workspace["index"].exists()

    # Run promote
    promote.main(
        indir=workspace["artifacts"].as_posix(),
        outdir=workspace["receipts"].as_posix(),
        vigil_url="vigil://test/project@refs/heads/main",
        profile=None,
        attestation_blob=None,
        attest=False,
        signing_key=None,
    )

    # Verify index was created
    assert workspace["index"].exists()

    # Load and verify index structure
    index = receipt_index.load_index(workspace["index"])
    assert "receipts" in index
    assert "updatedAt" in index
    assert len(index["receipts"]) == 1

    # Verify receipt entry
    entry = index["receipts"][0]
    assert entry["issuer"] == "Vigil"
    assert entry["vigilUrl"] == "vigil://test/project@refs/heads/main"
    assert entry["gitRef"].startswith("abc123")
    assert entry["anchor"] is None  # Not anchored yet
    assert "RECEIPT" in entry["glyphs"]
    assert entry["metrics"]["accuracy"] == 0.95

    # Get the first receipt path
    entry["path"]

    # Run promote again - this creates a new receipt file due to timestamp
    # Note: Because timestamps change, promote creates a new receipt file
    # The index upserts based on path, so same-named receipts replace each other
    # But different timestamps mean different files, hence different paths
    (workspace["artifacts"] / "new_data.json").write_text(
        json.dumps({"new": "data"}), encoding="utf-8"
    )

    fixed_epoch2 = 1_700_001_000
    monkeypatch.setattr(promote.time, "time", lambda: fixed_epoch2)
    monkeypatch.setattr(promote.time, "strftime", lambda fmt, t: "20231114T221520Z")

    promote.main(
        indir=workspace["artifacts"].as_posix(),
        outdir=workspace["receipts"].as_posix(),
        vigil_url="vigil://test/project@refs/heads/main",
        profile=None,
        attestation_blob=None,
        attest=False,
        signing_key=None,
    )

    # Verify index was updated - should have 2 receipts with different timestamps/paths
    index2 = receipt_index.load_index(workspace["index"])
    # Actually, promote creates receipt with unique timestamp, so we should have 2
    # But the second promote picks up ALL artifacts including the old ones,
    # so it creates just ONE new receipt that includes all artifacts
    # The receipt path is based on timestamp, so it's different
    assert len(index2["receipts"]) == 2  # Two separate receipt files


def test_anchor_updates_index_with_anchor_info(
    workspace: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that anchor updates index.json with anchor metadata."""
    # First, create some receipts
    monkeypatch.setattr(
        promote.subprocess,
        "check_output",
        lambda *_, **__: "abc123def456abc123def456abc123def456abc1\n",
    )

    # Create two receipts with different timestamps
    for i in range(2):
        fixed_epoch = 1_700_000_000 + i * 1000
        timestamp_str = f"2023-11-14T22:13:{20+i}0Z"

        monkeypatch.setattr(promote.time, "time", lambda epoch=fixed_epoch: epoch)
        monkeypatch.setattr(promote.time, "strftime", lambda fmt, t, ts=timestamp_str: ts)

        (workspace["artifacts"] / f"artifact_{i}.txt").write_text(
            f"data {i}", encoding="utf-8"
        )

        promote.main(
            indir=workspace["artifacts"].as_posix(),
            outdir=workspace["receipts"].as_posix(),
            vigil_url="vigil://test/project@refs/heads/main",
            profile=None,
            attestation_blob=None,
        )

    # Verify receipts exist without anchor info
    index_before = receipt_index.load_index(workspace["index"])
    assert len(index_before["receipts"]) == 2
    assert all(entry["anchor"] is None for entry in index_before["receipts"])

    # Run anchor
    state_path = workspace["anchors"] / "state.json"
    bundle_dir = workspace["anchors"] / "proofs"
    manifest_path = workspace["anchors"] / "latest.json"

    result = anchor.anchor_receipts(
        workspace["receipts"],
        state_path,
        bundle_dir,
        manifest_path,
        workspace["index"],
    )

    # Verify anchor was created
    assert result.root is not None
    assert result.bundle_path is not None
    assert result.bundle_path.exists()

    # Verify index was updated with anchor info
    index_after = receipt_index.load_index(workspace["index"])
    assert len(index_after["receipts"]) == 2

    # All receipts should now have anchor info
    for entry in index_after["receipts"]:
        assert entry["anchor"] is not None
        assert entry["anchor"]["root"] == result.root
        assert "bundle" in entry["anchor"]
        assert "anchoredAt" in entry["anchor"]
        assert entry["anchor"]["proofUrl"] is None  # Not set yet


def test_anchor_record_proof_updates_index(
    workspace: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that record_proof updates index.json with proof URLs."""
    # First, create and anchor receipts
    monkeypatch.setattr(
        promote.subprocess,
        "check_output",
        lambda *_, **__: "abc123def456abc123def456abc123def456abc1\n",
    )

    fixed_epoch = 1_700_000_000
    fixed_struct = promote.time.gmtime(fixed_epoch)
    monkeypatch.setattr(promote.time, "time", lambda: fixed_epoch)
    monkeypatch.setattr(promote.time, "gmtime", lambda: fixed_struct)

    promote.main(
        indir=workspace["artifacts"].as_posix(),
        outdir=workspace["receipts"].as_posix(),
        vigil_url="vigil://test/project@refs/heads/main",
        profile=None,
        attestation_blob=None,
        attest=False,
        signing_key=None,
    )

    state_path = workspace["anchors"] / "state.json"
    bundle_dir = workspace["anchors"] / "proofs"
    manifest_path = workspace["anchors"] / "latest.json"

    result = anchor.anchor_receipts(
        workspace["receipts"],
        state_path,
        bundle_dir,
        manifest_path,
        workspace["index"],
    )

    # Verify no proof URL yet
    index_before = receipt_index.load_index(workspace["index"])
    for entry in index_before["receipts"]:
        assert entry["anchor"] is not None
        assert entry["anchor"]["proofUrl"] is None

    # Record a proof URL
    proof_url = "https://proofs.example.com/bundle/abc123"
    assert result.bundle_path is not None
    anchor.record_proof(
        result.bundle_path,
        proof_url,
        state_path,
        manifest_path,
        workspace["index"],
    )

    # Verify index was updated with proof URL
    index_after = receipt_index.load_index(workspace["index"])
    for entry in index_after["receipts"]:
        assert entry["anchor"] is not None
        assert entry["anchor"]["proofUrl"] == proof_url


def test_complete_happy_path(
    workspace: dict[str, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test the complete happy path: promote -> anchor -> record-proof."""
    # Mock git and time
    monkeypatch.setattr(
        promote.subprocess,
        "check_output",
        lambda *_, **__: "def789abc123def789abc123def789abc123def7\n",
    )
    fixed_epoch = 1_700_000_000
    monkeypatch.setattr(promote.time, "time", lambda: fixed_epoch)
    monkeypatch.setattr(promote.time, "strftime", lambda fmt, t: "2023-11-14T22:13:20Z")

    # Step 1: Promote artifacts
    promote.main(
        indir=workspace["artifacts"].as_posix(),
        outdir=workspace["receipts"].as_posix(),
        vigil_url="vigil://test/project@refs/heads/main",
        profile=None,
        attestation_blob=None,
        attest=False,
        signing_key=None,
    )

    # Verify index exists with receipt
    index1 = receipt_index.load_index(workspace["index"])
    assert len(index1["receipts"]) == 1
    assert index1["receipts"][0]["anchor"] is None
    assert index1["updatedAt"] is not None

    # Step 2: Anchor receipts
    state_path = workspace["anchors"] / "state.json"
    bundle_dir = workspace["anchors"] / "proofs"
    manifest_path = workspace["anchors"] / "latest.json"

    result = anchor.anchor_receipts(
        workspace["receipts"],
        state_path,
        bundle_dir,
        manifest_path,
        workspace["index"],
    )

    # Verify index has anchor info
    index2 = receipt_index.load_index(workspace["index"])
    assert len(index2["receipts"]) == 1
    assert index2["receipts"][0]["anchor"] is not None
    assert index2["receipts"][0]["anchor"]["root"] == result.root
    assert index2["receipts"][0]["anchor"]["proofUrl"] is None

    # Step 3: Record proof URL
    proof_url = "https://proofs.example.com/bundle/final"
    assert result.bundle_path is not None
    anchor.record_proof(
        result.bundle_path,
        proof_url,
        state_path,
        manifest_path,
        workspace["index"],
    )

    # Verify complete index
    index3 = receipt_index.load_index(workspace["index"])
    assert len(index3["receipts"]) == 1

    final_entry = index3["receipts"][0]
    assert final_entry["issuer"] == "Vigil"
    assert final_entry["vigilUrl"] == "vigil://test/project@refs/heads/main"
    assert final_entry["anchor"] is not None
    assert final_entry["anchor"]["root"] == result.root
    assert final_entry["anchor"]["proofUrl"] == proof_url
    assert final_entry["metrics"]["accuracy"] == 0.95
    assert "RECEIPT" in final_entry["glyphs"]

    # Verify the index file actually exists and is valid JSON
    assert workspace["index"].exists()
    raw_data = json.loads(workspace["index"].read_text(encoding="utf-8"))
    assert raw_data["receipts"][0]["anchor"]["proofUrl"] == proof_url
