"""CI policy checks for reproducible capsule releases."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence  # noqa: TCH003
from pathlib import Path

_CAPSULE_DIR = Path("capsule")
_MANIFEST = Path("vigil.yaml")
_WORKSPACE_SPEC = Path(".vigil/workspace.spec.json")
_DIGEST_LINE = re.compile(r"image:\s*\S+@sha256:[0-9a-fA-F]{64}")
_LATEST_PATTERN = re.compile(r":latest\b", re.IGNORECASE)
_COMMENT_PREFIXES = ("#", "//", "<!--")

_SKIP_SUFFIXES = {
    ".md",
    ".rst",
    ".txt",
    ".log",
    ".lock",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
}


class PolicyError(Exception):
    """Raised when a CI policy violation is detected."""


def _run_git(args: Sequence[str], *, check: bool = True, text: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", *args], check=False, capture_output=True, text=text)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr}")
    return result


def _fetch_ref(ref: str) -> bool:
    result = _run_git(["fetch", "--depth=2", "origin", ref], check=False)
    return result.returncode == 0


def _determine_base_ref(explicit: str | None) -> str:
    if explicit:
        if not _fetch_ref(explicit):
            raise RuntimeError(f"Failed to fetch explicit base ref '{explicit}'")
        return f"origin/{explicit}"

    env_base = os.environ.get("GITHUB_BASE_REF")
    if env_base and _fetch_ref(env_base):
        return f"origin/{env_base}"

    default_branch = os.environ.get("GITHUB_DEFAULT_BRANCH", "main")
    if _fetch_ref(default_branch):
        return f"origin/{default_branch}"

    # Fallback to the previous commit.
    head_parent = _run_git(["rev-parse", "HEAD^"], check=False)
    if head_parent.returncode == 0:
        return head_parent.stdout.strip()

    raise RuntimeError("Unable to determine a base revision for policy checks")


def _changed_files(base_ref: str) -> list[Path]:
    result = _run_git(["diff", "--name-only", f"{base_ref}...HEAD"])
    return [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]


def _iter_added_lines(base_ref: str, path: Path) -> Iterable[str]:
    result = _run_git(["diff", "--unified=0", f"{base_ref}...HEAD", "--", str(path)])
    for line in result.stdout.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            yield line[1:]


def _should_check_latest(path: Path) -> bool:
    if path.suffix.lower() in _SKIP_SUFFIXES:
        return False
    return (
        path.name == "Dockerfile"
        or path.suffix.lower() in {".dockerfile", ".yml", ".yaml", ".json", ".py", ".sh"}
        or path.suffix == ""
    )


def _check_no_latest(base_ref: str, files: Iterable[Path]) -> None:
    violations: list[str] = []
    for path in files:
        if not _should_check_latest(path):
            continue
        for line in _iter_added_lines(base_ref, path):
            stripped = line.strip()
            if not stripped or any(stripped.startswith(prefix) for prefix in _COMMENT_PREFIXES):
                continue
            if _LATEST_PATTERN.search(line):
                violations.append(f"{path}: contains ':latest' in added line -> {line.strip()}")
    if violations:
        details = "\n".join(violations)
        raise PolicyError(f"Detected mutable ':latest' tags in diff:\n{details}")


def _check_digest_updates(base_ref: str, files: list[Path]) -> None:
    manifest_changed = _MANIFEST in files
    workspace_changed = _WORKSPACE_SPEC in files
    capsule_changed = any(path.is_relative_to(_CAPSULE_DIR) for path in files)

    errors: list[str] = []
    if manifest_changed and not workspace_changed:
        errors.append("vigil.yaml changed without updating .vigil/workspace.spec.json")

    if capsule_changed and not manifest_changed:
        errors.append("Capsule build files changed but vigil.yaml was not updated with a new digest")

    if capsule_changed and manifest_changed:
        digest_line_added = any(
            _DIGEST_LINE.search(line)
            for line in _iter_added_lines(base_ref, _MANIFEST)
        )
        if not digest_line_added:
            errors.append("vigil.yaml must update capsule.image digest when capsule/ changes")

    if errors:
        raise PolicyError("; ".join(errors))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enforce capsule release policies")
    parser.add_argument(
        "--base",
        help="Explicit git ref to diff against (defaults to GITHUB_BASE_REF or origin/main)",
    )
    args = parser.parse_args(argv)

    base_ref = _determine_base_ref(args.base)
    files = _changed_files(base_ref)

    try:
        _check_no_latest(base_ref, files)
        _check_digest_updates(base_ref, files)
    except PolicyError as exc:
        sys.stderr.write(f"CI policy violation: {exc}\n")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
