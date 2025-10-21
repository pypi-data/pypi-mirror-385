"""Evidence graph panel factory for the Vigil Workbench."""

from __future__ import annotations

import json
from pathlib import Path  # noqa: TCH003
from typing import Any

from app.code.lib.paths import project_path

DEFAULT_GRAPH_PATH = project_path("app/code/receipts/evidence_graph.json")


def _load_graph(graph_path: Path) -> dict[str, Any]:
    """Load the evidence graph from ``graph_path``.

    When the file is absent we return an empty graph shell so the Workbench can
    render a placeholder state without raising exceptions.
    """

    if not graph_path.exists():
        return {"nodes": [], "edges": [], "glyphs": []}

    with graph_path.open(encoding="utf-8") as fh:
        graph: dict[str, Any] = json.load(fh)
    return graph


def build_panel(*, graph_path: Path | None = None) -> dict[str, Any]:
    """Return the Workbench panel configuration for the evidence graph."""

    resolved_path = project_path(graph_path) if graph_path else DEFAULT_GRAPH_PATH
    graph = _load_graph(resolved_path)
    return {
        "id": "evidence-panel",
        "label": "Evidence Graph",
        "type": "evidenceGraph",
        "graph": graph,
        "sourcePath": str(resolved_path),
    }


__all__ = ["build_panel"]
