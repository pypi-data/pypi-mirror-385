"""Test receipt_index utilities."""

from __future__ import annotations

from pathlib import Path  # noqa: TCH003

from vigil.tools import receipt_index


def test_load_index_nonexistent(tmp_path: Path):
    """Test loading a nonexistent index returns empty structure."""
    index_path = tmp_path / "index.json"
    index = receipt_index.load_index(index_path)

    assert isinstance(index, dict)
    assert "receipts" in index
    assert "updatedAt" in index
    assert isinstance(index["receipts"], list)
    assert index["updatedAt"] is None


def test_write_and_load_index(tmp_path: Path):
    """Test writing and loading an index."""
    index_path = tmp_path / "index.json"

    # Create a sample index
    sample_index: receipt_index.ReceiptIndex = {
        "receipts": [
            {
                "path": "receipt_1.json",
                "hash": "sha256:abc123",
                "issuer": "Vigil",
                "vigilUrl": "vigil://test",
                "gitRef": "main",
                "capsuleDigest": "sha256:def456",
                "runletId": "rl_1",
                "startedAt": "2024-01-01T00:00:00Z",
                "finishedAt": "2024-01-01T01:00:00Z",
                "outputs": [],
                "metrics": {},
                "anchor": None,
            }
        ],
    }

    # Write it (note: write_index(path, index) signature)
    receipt_index.write_index(index_path, sample_index)

    # Read it back
    loaded = receipt_index.load_index(index_path)

    # Check structure (note: updatedAt will be set by write_index)
    assert len(loaded["receipts"]) == 1
    assert loaded["receipts"][0]["hash"] == "sha256:abc123"
    assert loaded["receipts"][0]["path"] == "receipt_1.json"
    assert loaded["updatedAt"] is not None  # Set during write
