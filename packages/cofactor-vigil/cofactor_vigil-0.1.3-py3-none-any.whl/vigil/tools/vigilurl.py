"""Vigil URL generation utilities."""

from __future__ import annotations

import sys
import urllib.parse
from typing import Any

import yaml


def load_manifest() -> tuple[dict[str, Any], str]:
    """Load manifest from current directory."""
    for name in ("vigil.yaml", "bench.yaml", "trail.yaml"):
        try:
            with open(name, encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
        except FileNotFoundError:
            continue
        if cfg:
            return cfg, name
    sys.stderr.write("No vigil.yaml/bench.yaml/trail.yaml found.\n")
    raise SystemExit(1)


def build_vigil_url(cfg: dict[str, Any]) -> str:
    """Build a vigil:// URL from manifest configuration."""
    host = cfg["resolverHost"]
    org = cfg["org"]
    proj = cfg["project"]

    capsule = cfg.get("capsule")
    if not isinstance(capsule, dict):
        msg = "Manifest capsule section must be a mapping with an image pinned by digest."
        raise ValueError(msg)

    image_value = capsule.get("image")
    if not isinstance(image_value, str):
        msg = "Manifest capsule.image must be a string pinned by digest (e.g., repo@sha256:...)."
        raise ValueError(msg)

    if "@" not in image_value:
        msg = "Manifest capsule.image must include an OCI digest (e.g., repo@sha256:...)."
        raise ValueError(msg)

    image = image_value.split("@", 1)[1]
    if not image:
        msg = "Manifest capsule.image must include a digest after '@'."
        raise ValueError(msg)

    inputs = cfg.get("inputs", [])
    params: list[tuple[str, str]] = [("img", image)]
    if inputs:
        params.append(("inputs", inputs[0]))
    query = "&".join(f"{key}={urllib.parse.quote(value, safe=':/')}" for key, value in params)
    return f"vigil://{host}/{org}/{proj}@refs/heads/main?{query}"


def main() -> int:
    """CLI entrypoint for vigilurl command."""
    config, src = load_manifest()
    try:
        url = build_vigil_url(config)
    except ValueError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1

    print(url)
    if src != "vigil.yaml":
        sys.stderr.write(f"[deprecation] Using {src}; please migrate to vigil.yaml\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
