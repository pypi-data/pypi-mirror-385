"""Receipt index management utilities."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

DEFAULT_INDEX_PATH = Path("app/code/receipts/index.json")


class AnchorRecord(TypedDict, total=False):
    """Anchor record metadata."""

    root: str
    bundle: str
    anchoredAt: str
    proofUrl: str | None


class ReceiptEntry(TypedDict, total=False):
    """Receipt entry in the index."""

    path: str
    hash: str
    issuer: str
    vigilUrl: str
    gitRef: str
    capsuleDigest: str
    runletId: str
    startedAt: str
    finishedAt: str
    outputs: list[dict[str, Any]]
    metrics: dict[str, Any]
    glyphs: list[str]
    anchor: AnchorRecord | None


class ReceiptIndex(TypedDict, total=False):
    """Receipt index structure."""

    receipts: list[ReceiptEntry]
    updatedAt: str | None


def _default_index() -> ReceiptIndex:
    """Create a default empty index."""
    return ReceiptIndex(receipts=[], updatedAt=None)


def load_index(path: Path) -> ReceiptIndex:
    """Load receipt index from path."""
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("receipts", [])
        data.setdefault("updatedAt", None)
        return ReceiptIndex(**data)
    return _default_index()


def write_index(path: Path, index: ReceiptIndex) -> None:
    """Write receipt index to path."""
    receipts = index.get("receipts", [])
    receipts.sort(key=lambda entry: entry.get("finishedAt", ""), reverse=True)
    index["receipts"] = receipts
    index["updatedAt"] = datetime.now(UTC).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def upsert_receipt(index: ReceiptIndex, entry: ReceiptEntry) -> None:
    """Add or update a receipt entry in the index."""
    receipts = index.setdefault("receipts", [])
    path = entry.get("path")
    receipts[:] = [existing for existing in receipts if existing.get("path") != path]
    receipts.append(deepcopy(entry))


def mark_receipts_anchored(
    index: ReceiptIndex,
    receipt_paths: list[str],
    anchor: AnchorRecord,
) -> list[str]:
    """Mark receipts as anchored with the given anchor record."""
    updated: list[str] = []
    if not receipt_paths:
        return updated
    receipts = index.get("receipts", [])
    for entry in receipts:
        if entry.get("path") in receipt_paths:
            entry["anchor"] = deepcopy(anchor)
            updated.append(entry["path"])
    return updated


def set_proof_url(index: ReceiptIndex, bundle: str, proof_url: str) -> bool:
    """Set proof URL for receipts anchored to a specific bundle."""
    found = False
    for entry in index.get("receipts", []):
        anchor = entry.get("anchor")
        if anchor and anchor.get("bundle") == bundle:
            anchor["proofUrl"] = proof_url
            found = True
    return found
