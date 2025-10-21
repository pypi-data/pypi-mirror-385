"""Utilities for synchronising Vigil workspace specifications.

This module centralises the logic for reading ``vigil.yaml`` and the
``.vigil/workspace.spec.json`` file.  Keeping the parsing code in one place
allows both generators and validation tooling to rely on a consistent view of
the canonical capsule metadata.  The helper also exposes a small CLI that can
rewrite the workspace spec so that the capsule image digest and extension list
stay aligned with the manifest.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import typer
import yaml

MANIFEST_NAME = "vigil.yaml"
WORKSPACE_SPEC_PATH = Path(".vigil") / "workspace.spec.json"

# SHA256 digest pattern: sha256: followed by exactly 64 hex characters
_DIGEST_PATTERN = re.compile(r"^sha256:[0-9a-fA-F]{64}$")


def _resolve_spec_path(base_path: Path, spec_path: Path | None) -> Path:
    """Resolve a workspace spec path against ``base_path``."""

    target = spec_path or WORKSPACE_SPEC_PATH
    if not target.is_absolute():
        target = (base_path / target).resolve()
    return target


def load_manifest(base_path: Path) -> dict[str, Any]:
    """Load ``vigil.yaml`` if present, returning an empty mapping otherwise."""

    manifest_path = base_path / MANIFEST_NAME
    if not manifest_path.exists():
        return {}
    try:
        with manifest_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - defensive, unlikely
        raise ValueError(f"Failed to parse {manifest_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{manifest_path} should contain a mapping")
    return data


def load_workspace_spec(base_path: Path, spec_path: Path | None = None) -> dict[str, Any]:
    """Load the workspace spec JSON if present, returning an empty mapping."""

    target = _resolve_spec_path(base_path, spec_path)
    if not target.exists():
        return {}
    try:
        with target.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive, unlikely
        raise ValueError(f"Failed to parse {target}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{target} should contain a JSON object")
    return data


def _ensure_capsule(spec: dict[str, Any]) -> dict[str, Any]:
    capsule = spec.get("capsule")
    if not isinstance(capsule, dict):
        capsule = {}
        spec["capsule"] = capsule
    return capsule


def _normalise_extensions(extensions: list[Any]) -> list[str]:
    return [str(ext) for ext in extensions]


def _validate_image_digest(image: str) -> None:
    """Validate that the image contains a valid sha256 digest.

    Args:
        image: The image string (e.g., "ghcr.io/org/image@sha256:abc123...")

    Raises:
        ValueError: If the image doesn't contain a valid sha256 digest
    """
    if "@" not in image:
        raise ValueError(f"Capsule image must be pinned with @digest, got: {image}")

    digest = image.split("@", 1)[1]
    if not _DIGEST_PATTERN.match(digest):
        raise ValueError(
            f"Capsule image digest must be sha256 with 64 hex characters, got: {digest}"
        )


def _validate_extensions(extensions: list[Any]) -> None:
    """Validate that extensions is a list of strings.

    Args:
        extensions: The extensions list to validate

    Raises:
        ValueError: If extensions is not a list or contains non-string values
    """
    if not isinstance(extensions, list):
        raise ValueError(f"Capsule extensions must be a list, got: {type(extensions).__name__}")

    for i, ext in enumerate(extensions):
        if not isinstance(ext, str | int | float | bool):
            raise ValueError(
                f"Capsule extension at index {i} has invalid type {type(ext).__name__}, "
                f"expected string-convertible value"
            )


def sync_workspace_spec(
    base_path: Path,
    spec_path: Path | None = None,
) -> tuple[dict[str, Any], Path]:
    """Return a workspace spec whose capsule metadata mirrors ``vigil.yaml``.

    This function validates that:
    - capsule.image contains a valid sha256 digest
    - capsule.extensions is a list of string-convertible values

    Args:
        base_path: Repository root path
        spec_path: Optional custom path for workspace.spec.json

    Returns:
        Tuple of (validated spec dict, target path)

    Raises:
        ValueError: If manifest is missing, malformed, or validation fails
    """
    manifest = load_manifest(base_path)
    if not manifest:
        raise ValueError("Manifest vigil.yaml not found or empty")

    capsule_manifest = manifest.get("capsule")
    if not isinstance(capsule_manifest, dict):
        raise ValueError("Manifest capsule section is missing or malformed")

    image = capsule_manifest.get("image")
    extensions = capsule_manifest.get("extensions")
    if not image:
        raise ValueError("Manifest is missing capsule.image")
    if not isinstance(extensions, list):
        raise ValueError("Manifest is missing capsule.extensions list")

    # Validate image digest format
    _validate_image_digest(image)

    # Validate extensions format
    _validate_extensions(extensions)

    spec = load_workspace_spec(base_path, spec_path) or {}
    capsule_spec = _ensure_capsule(spec)
    capsule_spec["image"] = image
    capsule_spec["extensions"] = _normalise_extensions(extensions)

    target = _resolve_spec_path(base_path, spec_path)
    return spec, target


def write_workspace_spec(spec: dict[str, Any], target: Path) -> None:
    """Persist ``spec`` to ``target`` with canonical formatting.

    Canonical formatting includes:
    - Sorted keys for deterministic output
    - 2-space indentation
    - Trailing newline

    Args:
        spec: The workspace specification dict to write
        target: Path where the spec should be written
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(spec, indent=2, sort_keys=True)
    target.write_text(f"{payload}\n", encoding="utf-8")


def run_command(
    base_path: Path = typer.Option(
        Path("."), exists=True, file_okay=False, resolve_path=True, help="Repository root"
    ),
    spec_path: Path | None = typer.Option(
        WORKSPACE_SPEC_PATH,
        file_okay=True,
        dir_okay=False,
        resolve_path=False,
        help="Path to workspace spec relative to the repository root",
    ),
    dry_run: bool = typer.Option(False, help="Print updated spec to stdout instead of writing"),
) -> None:
    """CLI entrypoint that synchronises the workspace spec with the manifest.

    Validates capsule metadata and writes canonical JSON with sorted keys.
    Use --dry-run to preview changes without modifying files.
    """
    spec, target = sync_workspace_spec(base_path, spec_path)
    if dry_run:
        # Output canonical JSON (sorted keys) with trailing newline for --dry-run
        payload = json.dumps(spec, indent=2, sort_keys=True)
        typer.echo(f"{payload}\n", nl=False)
        raise typer.Exit(code=0)

    write_workspace_spec(spec, target)
    typer.echo(f"Updated workspace spec at {target}")


def main() -> None:
    """Entrypoint compatible with ``python app/code/tools/workspace_spec.py``."""

    typer.run(run_command)


if __name__ == "__main__":
    main()
