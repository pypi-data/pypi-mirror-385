"""Utilities for updating Vigil capsule digests across the repository.

This module provides a small CLI that rewrites ``vigil.yaml`` and the
associated ``.vigil/workspace.spec.json`` file with a new capsule image
digest.  It also updates any ancillary documentation that references the
previous digest so that humans see consistent metadata after a release.

The command is intended for automation (for example in GitHub Actions) but
is also safe to run manually when preparing a release candidate.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Iterable, Sequence  # noqa: TCH003
from pathlib import Path

import typer
import yaml
from vigil.tools import workspace_spec

_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-fA-F]{64}$")

BASE_DIR = Path(__file__).resolve().parents[3]
_KNOWN_DOC_PATHS: Sequence[Path] = (
    Path("README.md"),
    Path("app/notes/arcade/README.md"),
    Path("app/notes/method/METHODCARD.md"),
    Path("app/notes/method/methodcard.json"),
)


def _replace_in_files(old: str, new: str, files: Iterable[Path]) -> list[Path]:
    """Replace ``old`` with ``new`` in the provided text files."""

    touched: list[Path] = []
    for path in files:
        if not path.exists() or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # Skip binary blobs – the digest should not live there.
            continue
        updated = text.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            touched.append(path)
    return touched


def _discover_digest_references(old_digest: str, base_dir: Path, manifest_path: Path) -> list[Path]:
    """Return git-tracked files that reference ``old_digest``."""

    git_dir = base_dir / ".git"
    if not git_dir.exists():
        return []

    result = subprocess.run(
        ["git", "grep", "-lz", old_digest],
        cwd=base_dir,
        check=False,
        capture_output=True,
    )
    if result.returncode not in (0, 1):  # pragma: no cover - defensive
        sys.stderr.write(result.stderr.decode("utf-8", "ignore"))
        raise RuntimeError("git grep failed while locating digest references")

    files: list[Path] = []
    for raw in result.stdout.split(b"\x00"):
        if not raw:
            continue
        path = (base_dir / raw.decode("utf-8")).resolve()
        if path == manifest_path:
            continue
        files.append(path)
    return files


def _update_manifest(digest: str, manifest_path: Path) -> tuple[str, str]:
    """Update ``vigil.yaml`` with ``digest`` and return image metadata."""

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    capsule = data.get("capsule")
    if not isinstance(capsule, dict) or "image" not in capsule:
        raise ValueError("vigil.yaml does not contain capsule.image")

    image: str = capsule["image"]
    if "@" not in image:
        raise ValueError("capsule.image is not pinned by digest")

    image_ref, old_digest = image.split("@", 1)
    new_image = f"{image_ref}@{digest}"
    capsule["image"] = new_image

    manifest_path.write_text(
        yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )
    return image_ref, old_digest


def _update_workspace_spec(base_dir: Path) -> Path:
    """Synchronise ``.vigil/workspace.spec.json`` with ``vigil.yaml``."""

    spec, target = workspace_spec.sync_workspace_spec(base_dir)
    workspace_spec.write_workspace_spec(spec, target)
    return target


def _gather_known_docs(base_dir: Path) -> list[Path]:
    """Return documentation files that should mirror the manifest digest."""

    docs: list[Path] = []
    for rel_path in _KNOWN_DOC_PATHS:
        candidate = (base_dir / rel_path).resolve()
        if candidate.exists() and candidate.is_file():
            docs.append(candidate)

    notebooks_dir = base_dir / "app/notes/notebooks"
    if notebooks_dir.exists():
        for path in sorted(notebooks_dir.rglob("*")):
            if path.is_file():
                docs.append(path.resolve())

    return docs


def _unique_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(resolved)
    return unique


def run(
    digest: str,
    *,
    base_dir: Path = BASE_DIR,
    paths_output: Path | None = None,
) -> list[Path]:
    """Re-pin the Vigil capsule image to ``digest`` across the repository."""

    if not _DIGEST_PATTERN.fullmatch(digest):
        raise typer.BadParameter("Digest must look like sha256:<64 hex characters>")

    base_dir = base_dir.resolve()
    manifest_path = base_dir / workspace_spec.MANIFEST_NAME

    image_ref, old_digest = _update_manifest(digest, manifest_path)

    spec_path = _update_workspace_spec(base_dir)

    touched_docs: list[Path] = []
    if old_digest:
        references = _discover_digest_references(old_digest, base_dir, manifest_path)
        known_docs = _gather_known_docs(base_dir)
        doc_candidates = _unique_paths([*known_docs, *references])
        touched_docs = _replace_in_files(old_digest, digest, doc_candidates)
    else:  # pragma: no cover - defensive, manifests should always be pinned
        known_docs = _gather_known_docs(base_dir)
        touched_docs = _replace_in_files(old_digest, digest, known_docs)

    typer.echo(f"Pinned capsule image: {image_ref}@{digest}")
    typer.echo(f"Updated manifest at {manifest_path.relative_to(base_dir)}")
    typer.echo(f"Updated workspace spec at {spec_path.relative_to(base_dir)}")

    touched_paths = _unique_paths([manifest_path, spec_path, *touched_docs])
    rel_paths = [path.relative_to(base_dir).as_posix() for path in touched_paths]

    if touched_docs:
        doc_paths = ", ".join(path.relative_to(base_dir).as_posix() for path in touched_docs)
        typer.echo(f"Updated documentation references: {doc_paths}")

    typer.echo("Touched files:")
    for rel_path in rel_paths:
        typer.echo(f"- {rel_path}")

    if paths_output is not None:
        target = paths_output
        if not target.is_absolute():
            target = (base_dir / target).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = "\n".join(rel_paths)
        if payload:
            payload = f"{payload}\n"
        target.write_text(payload, encoding="utf-8")

    return touched_paths


def main(
    digest: str = typer.Argument(..., help="New sha256 digest (without registry prefix)"),
    paths_output: Path | None = typer.Option(
        None,
        help="Optional file to write the newline-separated list of touched files",
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
    ),
    base_dir: Path = typer.Option(
        BASE_DIR,
        help="Repository root containing vigil.yaml",
        exists=True,
        file_okay=False,
        resolve_path=True,
    ),
) -> None:
    run(digest, base_dir=base_dir, paths_output=paths_output)


if __name__ == "__main__":
    typer.run(main)
