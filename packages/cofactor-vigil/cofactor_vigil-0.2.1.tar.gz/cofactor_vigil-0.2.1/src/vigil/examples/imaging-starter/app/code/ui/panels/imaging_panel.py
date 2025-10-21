"""Stub OME-NGFF viewer configuration for the Vigil Workbench."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

DEFAULT_SCENE_SIZE = 64


@dataclass(slots=True)
class DemoScene:
    """Synthetic imaging scene encoded as an OME-NGFF-like payload."""

    name: str
    data: np.ndarray

    def to_panel_payload(self) -> dict[str, Any]:
        """Return a serialisable payload for the Workbench imaging panel."""

        height, width = self.data.shape[-2:]
        return {
            "name": self.name,
            "axes": [
                {"type": "y", "size": height},
                {"type": "x", "size": width},
            ],
            "dtype": str(self.data.dtype),
            "shape": list(self.data.shape),
            "levels": [self.data.tolist()],
            "stats": {
                "min": float(self.data.min()),
                "max": float(self.data.max()),
                "mean": float(self.data.mean()),
            },
            "renderSettings": {
                "palette": "magma",
                "contrastLimits": [float(self.data.min()), float(self.data.max())],
            },
        }


def build_panel(*, size: int = DEFAULT_SCENE_SIZE) -> dict[str, Any]:
    """Return the Workbench configuration for the imaging panel stub."""

    scene = load_demo_scene(size=size)
    return {
        "id": "imaging-panel",
        "label": "OME-NGFF Viewer",
        "type": "omeNgffViewer",
        "scenes": [scene.to_panel_payload()],
        "actions": [
            {
                "label": "Send selection to Notebook",
                "command": "notebook.send_selection",
                "payload": {"scene": scene.name},
            }
        ],
    }


def load_demo_scene(*, size: int = DEFAULT_SCENE_SIZE) -> DemoScene:
    """Create a deterministic synthetic demo image for the viewer."""

    x = np.linspace(0.0, 1.0, size, dtype=np.float32)
    xv, yv = np.meshgrid(x, x)
    image = ((np.sin(np.pi * xv) * np.cos(np.pi * yv) + 1.0) * 127.5).astype(np.uint8)
    return DemoScene(name="Synthetic NGFF", data=image)
