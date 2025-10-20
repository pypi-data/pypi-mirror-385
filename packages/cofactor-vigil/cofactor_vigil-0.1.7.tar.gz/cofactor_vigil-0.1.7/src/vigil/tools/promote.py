"""Receipt promotion utilities - generate receipts from artifacts."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import subprocess
import time
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

import yaml

from vigil.tools import attestation as attestation_module
from vigil.tools import receipt_index, signing


class Artifact(TypedDict):
    """Artifact metadata."""

    uri: str
    checksum: str
    kind: str


class ReceiptMetrics(TypedDict, total=False):
    """Receipt metrics structure."""

    n: int
    tp: int
    tn: int
    fp: int
    fn: int
    accuracy: float
    precision: float
    recall: float
    f1: float


def sha256(path: Path | str) -> str:
    """Return the Vigil-prefixed SHA256 digest for ``path``."""

    file_path = Path(path)
    with file_path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256")
    return f"sha256:{digest.hexdigest()}"


def load_metrics(path: Path) -> ReceiptMetrics:
    """Load metrics from JSON file, falling back to an empty mapping."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ReceiptMetrics()
    except json.JSONDecodeError:
        return ReceiptMetrics()

    if not isinstance(raw, dict):
        return ReceiptMetrics()

    metrics = ReceiptMetrics()
    for key, value in raw.items():
        if isinstance(key, str):
            metrics[key] = value  # type: ignore[literal-required]
    return metrics


def _iter_files(root: Path) -> Iterable[Path]:
    """Yield all files under ``root`` sorted by relative path."""

    if not root.exists():
        return []

    return sorted((path for path in root.rglob("*") if path.is_file()), key=lambda path: path.as_posix())


def _load_manifest() -> dict[str, Any]:
    """Load vigil.yaml manifest from current directory."""
    for name in ("vigil.yaml", "bench.yaml", "trail.yaml"):
        try:
            with open(name, encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
        except FileNotFoundError:
            continue
        if isinstance(cfg, Mapping):
            return dict(cfg)
    return {}


def _profile_from_env(profile: str | None) -> str | None:
    """Get profile from argument or environment."""
    if profile:
        stripped = profile.strip()
        if stripped:
            return stripped
    for key in ("PIPELINE_PROFILE", "SNAKEMAKE_PROFILE"):
        value = os.environ.get(key)
        if value:
            stripped = value.strip()
            if stripped:
                return stripped
    return None


def _load_attestation_blob(attestation_path: Path) -> dict[str, Any]:
    """Load TEE attestation blob."""
    data = attestation_path.read_bytes()
    attestation: dict[str, Any] = {
        "path": attestation_path.as_posix(),
    }
    try:
        decoded = data.decode("utf-8")
        attestation["encoding"] = "utf-8"
        attestation["statement"] = json.loads(decoded)
    except (UnicodeDecodeError, json.JSONDecodeError):
        attestation["encoding"] = "base64"
        attestation["statement"] = base64.b64encode(data).decode("ascii")
    return attestation


def main(
    indir: str,
    outdir: str,
    vigil_url: str,
    profile: str | None,
    attestation_blob: str | None = None,
    *,
    attest: bool = False,
    signing_key: str | None = None,
    attestation: str | None = None,
    ) -> None:
    """Generate receipts from artifacts."""

    if attestation is not None and attestation_blob is None:
        attestation_blob = attestation

    input_root = Path(indir)
    output_root = Path(outdir)
    output_root.mkdir(parents=True, exist_ok=True)

    artifacts: list[Artifact] = []
    metrics: ReceiptMetrics = ReceiptMetrics()
    for file_path in _iter_files(input_root):
        artifact: Artifact = {
            "uri": file_path.as_posix(),
            "checksum": sha256(file_path),
            "kind": "file",
        }
        artifacts.append(artifact)
        if file_path.name == "metrics.json":
            metrics = load_metrics(file_path)

    # Add metadata for observability
    try:
        git_ref = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except subprocess.CalledProcessError:
        git_ref = "unknown"

    manifest = _load_manifest()
    capsule_section = manifest.get("capsule")
    if isinstance(capsule_section, Mapping):
        capsule = capsule_section.get("image", "unknown")
    else:
        capsule = "unknown"
    capsule_digest = capsule.split("@", 1)[1] if "@" in capsule else "unknown"

    started_at = os.environ.get("RUN_STARTED_AT") or datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    finished_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    detected_profile = _profile_from_env(profile)

    runlet_id = f"rl_{int(time.time())}"
    receipt: dict[str, Any] = {
        "issuer": "Vigil",
        "runletId": runlet_id,
        "vigilUrl": vigil_url,
        "gitRef": git_ref,
        "capsuleDigest": capsule_digest,
        "inputs": [],
        "outputs": artifacts,
        "metrics": metrics,
        "startedAt": started_at,
        "finishedAt": finished_at,
        "glyphs": ["RECEIPT"],
        "anchor": None,
        "signature": "UNSIGNED-DEV",
    }

    if detected_profile:
        receipt["profile"] = detected_profile

    if detected_profile and detected_profile.lower() == "tee":
        if not attestation_blob:
            raise ValueError("TEE profile selected but no attestation blob path was provided")
        attestation_path = Path(attestation_blob)
        if not attestation_path.exists():
            raise FileNotFoundError(f"Attestation blob not found: {attestation_path}")
        glyphs = receipt.setdefault("glyphs", [])
        if "TEE" not in glyphs:
            glyphs.append("TEE")
        receipt["attestation"] = _load_attestation_blob(attestation_path)

    glyphs = receipt.setdefault("glyphs", [])
    if artifacts and "DATA_TABLE" not in glyphs:
        glyphs.append("DATA_TABLE")

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = output_root / f"receipt_{timestamp}.json"
    out.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    # Generate SLSA provenance attestation if requested
    if attest:
        # Extract metrics as byproducts
        byproducts = []
        for artifact in artifacts:
            if "metrics.json" in artifact["uri"]:
                byproducts.append(artifact)

        # Determine cores from environment or profile
        cores = None
        cores_env = os.environ.get("CORES")
        if cores_env:
            try:
                cores = int(cores_env)
            except ValueError:
                pass

        attestation_statement = attestation_module.generate_attestation(
            receipt_path=out,
            vigil_url=vigil_url,
            git_ref=git_ref,
            capsule_digest=capsule_digest,
            runlet_id=runlet_id,
            started_at=started_at,
            finished_at=finished_at,
            profile=detected_profile,
            cores=cores,
            inputs=[],
            outputs=[dict(a) for a in artifacts],
            byproducts=[dict(b) for b in byproducts],
        )

        attestation_out = output_root / f"attestation_{timestamp}.json"
        attestation_module.save_attestation(attestation_statement, attestation_out)
        print(f"Attestation: {attestation_out.as_posix()}")

        # Sign attestation if signing key is available
        if signing_key or os.environ.get("VIGIL_SIGNING_KEY"):
            try:
                key_path = Path(signing_key) if signing_key else None
                signing.sign_attestation(
                    attestation_path=attestation_out,
                    private_key_path=key_path,
                )
                sig_path = attestation_out.with_suffix(attestation_out.suffix + ".sig")
                print(f"Signature: {sig_path.as_posix()}")
            except ImportError as e:
                print(f"Warning: Could not sign attestation: {e}")
            except Exception as e:
                print(f"Warning: Signing failed: {e}")

    run_node_id = f"run:{receipt['runletId']}"
    code_node_id = f"code:{git_ref}"
    environment_node_id = (
        f"environment:{capsule_digest}" if capsule_digest != "unknown" else "environment:unknown"
    )

    data_nodes = [
        {
            "id": f"data:{artifact['uri']}",
            "type": "Data",
            "uri": artifact["uri"],
            "checksum": artifact["checksum"],
            "kind": artifact["kind"],
        }
        for artifact in artifacts
    ]

    graph_nodes: list[dict[str, Any]] = [
        {
            "id": run_node_id,
            "type": "Run",
            "gitRef": git_ref,
            "capsuleDigest": capsule_digest,
            "startedAt": started_at,
            "finishedAt": finished_at,
        },
        {
            "id": code_node_id,
            "type": "Code",
            "gitRef": git_ref,
        },
        {
            "id": environment_node_id,
            "type": "Environment",
            "capsuleDigest": capsule_digest,
            "profile": detected_profile,
        },
    ]
    graph_nodes.extend(data_nodes)

    graph_edges: list[dict[str, Any]] = [
        {
            "from": code_node_id,
            "to": run_node_id,
            "type": "defines",
        },
        {
            "from": environment_node_id,
            "to": run_node_id,
            "type": "executedIn",
        },
    ]
    graph_edges.extend(
        {"from": run_node_id, "to": data_node["id"], "type": "produced"} for data_node in data_nodes
    )

    glyph_metadata: list[dict[str, Any]] = [
        {"glyph": "RECEIPT", "nodes": [run_node_id]},
    ]
    if data_nodes:
        glyph_metadata.append(
            {
                "glyph": "DATA_TABLE",
                "nodes": [node["id"] for node in data_nodes],
            }
        )
    if "TEE" in glyphs:
        glyph_metadata.append({"glyph": "TEE", "nodes": [environment_node_id]})

    graph = {
        "nodes": graph_nodes,
        "edges": graph_edges,
        "glyphs": glyph_metadata,
        "receiptPath": out.as_posix(),
    }
    evidence_path = output_root / "evidence_graph.json"
    evidence_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    repo_root = Path(os.getcwd()).resolve()
    receipt_abs = out.resolve()
    try:
        receipt_rel = receipt_abs.relative_to(repo_root).as_posix()
    except ValueError:
        receipt_rel = receipt_abs.as_posix()
    index_path = (output_root / "index.json").resolve()
    index = receipt_index.load_index(index_path)
    entry: receipt_index.ReceiptEntry = {
        "path": receipt_rel,
        "hash": sha256(out.as_posix()),
        "issuer": receipt["issuer"],
        "vigilUrl": vigil_url,
        "gitRef": git_ref,
        "capsuleDigest": capsule_digest,
        "runletId": receipt["runletId"],
        "startedAt": started_at,
        "finishedAt": finished_at,
        "outputs": artifacts,  # type: ignore[typeddict-item]
        "metrics": dict(metrics),
        "glyphs": list(receipt["glyphs"]),
        "anchor": None,
    }
    receipt_index.upsert_receipt(index, entry)
    receipt_index.write_index(index_path, index)

    print(out.as_posix())


def cli() -> None:
    """CLI entrypoint for promote command."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="i", default="app/code/artifacts")
    ap.add_argument("--out", dest="o", default="app/code/receipts")
    ap.add_argument(
        "--vigil-url",
        dest="vigil_url",
        default="vigil://labs.example/acme-lab/imaging-starter@refs/heads/main",
    )
    ap.add_argument("--profile", dest="profile", default=None)
    ap.add_argument("--attestation", dest="attestation_blob", default=None)
    ap.add_argument(
        "--attest",
        dest="attest",
        action="store_true",
        help="Generate SLSA provenance attestation",
    )
    ap.add_argument(
        "--signing-key",
        dest="signing_key",
        default=None,
        help="Path to Ed25519 private key for signing (PEM format)",
    )
    args = ap.parse_args()
    main(
        args.i,
        args.o,
        args.vigil_url,
        args.profile,
        args.attestation_blob,
        attest=args.attest,
        signing_key=args.signing_key,
    )


if __name__ == "__main__":
    cli()
