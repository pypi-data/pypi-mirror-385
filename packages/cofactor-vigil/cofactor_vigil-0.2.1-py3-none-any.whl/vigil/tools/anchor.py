"""Utilities for anchoring Vigil receipts with Merkle proofs."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from collections.abc import Iterable, Sequence  # noqa: TCH003
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vigil.tools import receipt_index

DEFAULT_RECEIPT_DIR = Path("app/code/receipts")
DEFAULT_STATE_PATH = Path("app/code/anchors/state.json")
DEFAULT_BUNDLE_DIR = Path("app/code/anchors/proofs")
DEFAULT_MANIFEST_PATH = Path("app/code/anchors/latest.json")
DEFAULT_INDEX_PATH = receipt_index.DEFAULT_INDEX_PATH


@dataclass
class AnchorResult:
    root: str | None
    bundle_path: Path | None
    new_receipts: list[Path]
    processed_receipts: list[Path]


def _sha256_file(path: Path) -> bytes:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            h.update(chunk)
    return h.digest()


def _prefixed_hex(digest: bytes) -> str:
    return "sha256:" + digest.hex()


def _load_state(path: Path) -> dict[str, Any]:
    if path.exists():
        with path.open("r", encoding="utf-8") as fh:
            try:
                data = json.load(fh)
            except json.JSONDecodeError as exc:
                raise ValueError(f"State file {path} is not valid JSON") from exc
    else:
        data = {"processed": {}, "anchors": []}
    data.setdefault("processed", {})
    data.setdefault("anchors", [])
    return data  # type: ignore[no-any-return]


def _save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")
    tmp_path.replace(path)


def _merkle_levels(leaves: Sequence[bytes]) -> list[list[bytes]]:
    if not leaves:
        raise ValueError("Cannot build a Merkle tree without leaves")
    levels: list[list[bytes]] = [list(leaves)]
    while len(levels[-1]) > 1:
        current = levels[-1]
        next_level: list[bytes] = []
        for idx in range(0, len(current), 2):
            left = current[idx]
            right = current[idx + 1] if idx + 1 < len(current) else left
            next_level.append(hashlib.sha256(left + right).digest())
        levels.append(next_level)
    return levels


def _merkle_proof(levels: Sequence[Sequence[bytes]], index: int) -> list[dict[str, str]]:
    proof: list[dict[str, str]] = []
    position = index
    for depth in range(len(levels) - 1):
        layer = levels[depth]
        is_right = position % 2 == 1
        sibling_idx = position - 1 if is_right else position + 1
        if sibling_idx >= len(layer):
            sibling = layer[position]
        else:
            sibling = layer[sibling_idx]
        proof.append(
            {
                "position": "left" if is_right else "right",
                "hash": _prefixed_hex(sibling),
            }
        )
        position //= 2
    return proof


def _relative_paths(paths: Iterable[Path], root: Path) -> list[Path]:
    rel_paths: list[Path] = []
    for path in paths:
        try:
            rel_paths.append(path.relative_to(root))
        except ValueError:
            rel_paths.append(path)
    return rel_paths


def anchor_receipts(
    receipts_dir: Path,
    state_path: Path,
    bundle_dir: Path,
    manifest_path: Path,
    index_path: Path | None = None,
    proof_url: str | None = None,
) -> AnchorResult:
    receipts_dir = receipts_dir.resolve()
    bundle_dir = bundle_dir.resolve()
    manifest_path = manifest_path.resolve()
    repo_root = Path(os.getcwd()).resolve()
    resolved_index = (index_path or DEFAULT_INDEX_PATH).resolve()

    state = _load_state(state_path.resolve())
    processed: dict[str, str] = state["processed"]

    all_receipts = sorted(
        path
        for path in receipts_dir.rglob("*.json")
        if path.is_file()
        and path.resolve() != resolved_index
        and path.name not in {"index.json", "evidence_graph.json"}
    )
    new_receipts: list[Path] = []
    leaf_digests: list[bytes] = []
    leaf_paths: list[Path] = []

    for receipt_path in all_receipts:
        digest = _sha256_file(receipt_path)
        try:
            rel = receipt_path.relative_to(repo_root)
        except ValueError:
            rel = receipt_path.resolve()
        prefixed = _prefixed_hex(digest)
        prev_hash = processed.get(Path(rel).as_posix())
        if prev_hash == prefixed:
            continue
        new_receipts.append(receipt_path)
        leaf_digests.append(digest)
        leaf_paths.append(rel)

    manifest: dict[str, object]
    if not leaf_digests:
        manifest = {
            "generated_at": dt.datetime.now(dt.UTC).isoformat(),
            "root": None,
            "bundle_path": None,
            "new_receipts": [],
            "total_receipts": len(processed),
            "proof_url": None,
        }
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return AnchorResult(None, None, [], _relative_paths(all_receipts, repo_root))

    levels = _merkle_levels(leaf_digests)
    root_digest = levels[-1][0]
    root_hex = _prefixed_hex(root_digest)

    bundle_dir.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    bundle_path = bundle_dir / f"bundle_{timestamp}.json"

    leaves_payload = [
        {"path": path.as_posix(), "hash": _prefixed_hex(digest)}
        for path, digest in zip(leaf_paths, leaf_digests, strict=False)
    ]
    proofs = {
        path.as_posix(): _merkle_proof(levels, idx)
        for idx, path in enumerate(leaf_paths)
    }

    bundle = {
        "algorithm": "sha256",
        "root": root_hex,
        "generated_at": dt.datetime.now(dt.UTC).isoformat(),
        "leaves": leaves_payload,
        "proofs": proofs,
    }
    bundle_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")

    for path, digest in zip(leaf_paths, leaf_digests, strict=False):
        processed[Path(path).as_posix()] = _prefixed_hex(digest)

    try:
        bundle_rel = bundle_path.relative_to(repo_root).as_posix()
    except ValueError:
        bundle_rel = bundle_path.resolve().as_posix()
    anchor_record = {
        "root": root_hex,
        "bundle": bundle_rel,
        "receipts": [Path(path).as_posix() for path in leaf_paths],
        "generated_at": bundle["generated_at"],
        "proof_url": proof_url,
    }
    state["anchors"].append(anchor_record)
    _save_state(state_path, state)

    manifest = {
        "generated_at": bundle["generated_at"],
        "root": root_hex,
        "bundle_path": bundle_rel,
        "new_receipts": [Path(path).as_posix() for path in leaf_paths],
        "total_receipts": len(processed),
        "proof_url": proof_url,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    index = receipt_index.load_index(resolved_index)
    anchor_info = receipt_index.AnchorRecord(
        root=root_hex,
        bundle=bundle_rel,
        anchoredAt=str(bundle["generated_at"]),
        proofUrl=proof_url,
    )
    receipt_index.mark_receipts_anchored(
        index,
        [Path(path).as_posix() for path in leaf_paths],
        anchor_info,
    )
    receipt_index.write_index(resolved_index, index)

    return AnchorResult(root_hex, bundle_path, new_receipts, _relative_paths(all_receipts, repo_root))


def record_proof(
    bundle_path: Path,
    proof_url: str,
    state_path: Path,
    manifest_path: Path,
    index_path: Path | None = None,
) -> None:
    repo_root = Path(os.getcwd()).resolve()
    bundle_rel = bundle_path.resolve().relative_to(repo_root).as_posix()

    state = _load_state(state_path.resolve())
    found_in_state = False
    for anchor_entry in state["anchors"]:
        if anchor_entry.get("bundle") == bundle_rel:
            anchor_entry["proof_url"] = proof_url
            found_in_state = True
    if not found_in_state:
        raise ValueError(f"Bundle {bundle_rel} not found in state")
    _save_state(state_path, state)

    manifest: dict[str, object]
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {}
    if manifest.get("bundle_path") == bundle_rel:
        manifest["proof_url"] = proof_url
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    resolved_index = (index_path or DEFAULT_INDEX_PATH).resolve()
    index = receipt_index.load_index(resolved_index)
    if not receipt_index.set_proof_url(index, bundle_rel, proof_url):
        raise ValueError(f"Bundle {bundle_rel} not found in receipt index")
    receipt_index.write_index(resolved_index, index)


def verify_receipt(bundle_path: Path, receipt_path: Path) -> bool:
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    algorithm = bundle.get("algorithm")
    if algorithm != "sha256":
        raise ValueError(f"Unsupported algorithm {algorithm!r}")
    leaves: list[dict[str, str]] = bundle.get("leaves", [])
    proofs: dict[str, list[dict[str, str]]] = bundle.get("proofs", {})

    digest = _sha256_file(receipt_path)
    prefixed = _prefixed_hex(digest)

    rel_path = None
    for leaf in leaves:
        if leaf.get("hash") == prefixed:
            rel_path = leaf.get("path")
            break
    if rel_path is None:
        raise ValueError("Receipt hash not found in bundle")

    proof_steps = proofs.get(rel_path, [])
    current = digest
    for step in proof_steps:
        sibling_hex = step["hash"]
        if not sibling_hex.startswith("sha256:"):
            raise ValueError("Invalid hash prefix in proof")
        sibling = bytes.fromhex(sibling_hex.split(":", 1)[1])
        if step.get("position") == "left":
            current = hashlib.sha256(sibling + current).digest()
        else:
            current = hashlib.sha256(current + sibling).digest()

    root_hex = bundle.get("root")
    if not isinstance(root_hex, str) or not root_hex.startswith("sha256:"):
        raise ValueError("Invalid root encoding in bundle")
    return current.hex() == root_hex.split(":", 1)[1]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Anchor Vigil receipts with Merkle proofs")
    sub = parser.add_subparsers(dest="command", required=True)

    anchor_cmd = sub.add_parser("anchor", help="Scan receipts and emit a Merkle proof bundle")
    anchor_cmd.add_argument("--receipts", type=Path, default=DEFAULT_RECEIPT_DIR)
    anchor_cmd.add_argument("--state", type=Path, default=DEFAULT_STATE_PATH)
    anchor_cmd.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLE_DIR)
    anchor_cmd.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    anchor_cmd.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)
    anchor_cmd.add_argument("--proof-url", dest="proof_url", default=None)

    verify_cmd = sub.add_parser("verify", help="Verify a receipt against a proof bundle")
    verify_cmd.add_argument("bundle", type=Path)
    verify_cmd.add_argument("receipt", type=Path)

    record_cmd = sub.add_parser("record-proof", help="Attach a proof URL to anchored receipts")
    record_cmd.add_argument("bundle", type=Path)
    record_cmd.add_argument("--proof-url", required=True)
    record_cmd.add_argument("--state", type=Path, default=DEFAULT_STATE_PATH)
    record_cmd.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    record_cmd.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "anchor":
        result = anchor_receipts(
            args.receipts,
            args.state,
            args.bundle_dir,
            args.manifest,
            args.index,
            args.proof_url,
        )
        if result.root:
            print(json.dumps({"root": result.root, "bundle": str(result.bundle_path)}, indent=2))
        else:
            print(json.dumps({"root": None, "bundle": None, "message": "no new receipts"}, indent=2))
        return 0

    if args.command == "verify":
        ok = verify_receipt(args.bundle, args.receipt)
        print("verified" if ok else "verification failed")
        return 0 if ok else 1

    if args.command == "record-proof":
        record_proof(args.bundle, args.proof_url, args.state, args.manifest, args.index)
        print(json.dumps({"bundle": str(args.bundle), "proofUrl": args.proof_url}, indent=2))
        return 0

    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
