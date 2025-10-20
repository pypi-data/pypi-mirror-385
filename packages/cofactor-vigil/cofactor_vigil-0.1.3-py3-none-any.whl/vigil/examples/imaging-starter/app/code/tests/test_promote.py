from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from vigil.tools import promote


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure time-based environment variables are unset for determinism."""

    monkeypatch.delenv("RUN_STARTED_AT", raising=False)


def _write_sample_artifacts(root: Path) -> None:
    artifact_dir = root / "artifacts"
    artifact_dir.mkdir()
    (artifact_dir / "metrics.json").write_text(json.dumps({"accuracy": 0.9}), encoding="utf-8")
    (artifact_dir / "output.txt").write_text("hello", encoding="utf-8")


def _write_manifest(root: Path, data: Any) -> None:
    (root / "vigil.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


def _run_promote(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    manifest_data: Any | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _write_sample_artifacts(tmp_path)

    if manifest_data is None:
        manifest_data = {
            "capsule": {
                "image": "ghcr.io/example/capsule@sha256:deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
            }
        }
    _write_manifest(tmp_path, manifest_data)
    monkeypatch.chdir(tmp_path)

    fixed_epoch = 1_700_000_000
    fixed_struct = promote.time.gmtime(fixed_epoch)
    monkeypatch.setattr(promote.time, "time", lambda: fixed_epoch)
    monkeypatch.setattr(promote.time, "gmtime", lambda: fixed_struct)
    monkeypatch.setattr(
        promote.subprocess,
        "check_output",
        lambda *_, **__: "abcdef1234567890abcdef1234567890abcdef12\n",
    )

    out_dir = tmp_path / "receipts"
    promote.main(
        indir=str(tmp_path / "artifacts"),
        outdir=str(out_dir),
        vigil_url="vigil://example/run",
        profile=None,
        attestation_blob=None,
        attest=False,
        signing_key=None,
    )

    evidence_graph_path = out_dir / "evidence_graph.json"
    with evidence_graph_path.open(encoding="utf-8") as fh:
        graph: dict[str, Any] = json.load(fh)

    index_path = out_dir / "index.json"
    with index_path.open(encoding="utf-8") as fh:
        index: dict[str, Any] = json.load(fh)
    return graph, index


def test_evidence_graph_structure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    graph, index = _run_promote(tmp_path, monkeypatch)

    node_types = {node["type"] for node in graph["nodes"]}
    assert {"Run", "Data", "Code", "Environment"} <= node_types

    run_nodes = [node for node in graph["nodes"] if node["type"] == "Run"]
    assert len(run_nodes) == 1
    run_node = run_nodes[0]
    assert "gitRef" in run_node and "startedAt" in run_node

    code_nodes = [node for node in graph["nodes"] if node["type"] == "Code"]
    assert len(code_nodes) == 1
    assert code_nodes[0]["gitRef"].startswith("abcdef")

    data_nodes = [node for node in graph["nodes"] if node["type"] == "Data"]
    assert {Path(node["uri"]).name for node in data_nodes} == {"metrics.json", "output.txt"}

    edge_types = {edge["type"] for edge in graph["edges"]}
    assert "defines" in edge_types
    assert "executedIn" in edge_types
    assert sum(1 for edge in graph["edges"] if edge["type"] == "produced") == len(data_nodes)

    glyph_index = {entry["glyph"]: entry["nodes"] for entry in graph.get("glyphs", [])}
    assert "RECEIPT" in glyph_index
    assert set(glyph_index.get("DATA_TABLE", [])) == {node["id"] for node in data_nodes}

    receipts = index.get("receipts", [])
    assert receipts, "index should contain at least one receipt entry"
    entry = receipts[0]
    assert entry["issuer"] == "Vigil"
    assert entry["anchor"] is None
    assert entry["glyphs"] and "RECEIPT" in entry["glyphs"]
    assert entry["metrics"] == {"accuracy": 0.9}
    assert all("checksum" in output for output in entry["outputs"])
    assert entry["gitRef"].startswith("abcdef")
    assert entry["vigilUrl"] == "vigil://example/run"
    assert entry["capsuleDigest"] == "sha256:deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    assert entry["startedAt"] <= entry["finishedAt"]


def test_promote_receipt_path_in_graph(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    graph, index = _run_promote(tmp_path, monkeypatch)
    receipt_path = graph.get("receiptPath")
    assert receipt_path, "graph should record the receipt path"
    assert Path(receipt_path).exists()

    receipts = index.get("receipts", [])
    stored_paths = {entry["path"] for entry in receipts}
    receipt_abs = Path(receipt_path).resolve()
    stored_abs_paths = {
        (tmp_path / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
        for path in stored_paths
    }
    assert receipt_abs in stored_abs_paths


def test_promote_handles_invalid_capsule(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    graph, index = _run_promote(
        tmp_path,
        monkeypatch,
        manifest_data={"capsule": "not-a-mapping"},
    )

    env_nodes = [node for node in graph["nodes"] if node["type"] == "Environment"]
    assert env_nodes, "environment node should be present"
    assert env_nodes[0]["capsuleDigest"] == "unknown"

    receipts = index.get("receipts", [])
    assert receipts, "receipts should exist"
    assert receipts[0]["capsuleDigest"] == "unknown"

