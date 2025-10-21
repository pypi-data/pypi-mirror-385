"""Utilities for resolving paths inside the imaging starter project."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def ensure_project_on_path() -> None:
    """Ensure the imaging starter project root is importable."""

    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def project_path(path: str | Path) -> Path:
    """Return ``path`` as an absolute path rooted at the project if needed."""

    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate
