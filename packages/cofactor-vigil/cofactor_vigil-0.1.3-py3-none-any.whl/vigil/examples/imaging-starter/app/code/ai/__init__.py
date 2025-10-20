"""AI tool-calling / Suggestion Cell utilities."""

from __future__ import annotations

from typing import Any

__all__ = ["AutoTargetAgent"]


def __getattr__(name: str) -> Any:
    if name == "AutoTargetAgent":
        from app.code.ai.auto_target import AutoTargetAgent as _AutoTargetAgent

        return _AutoTargetAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
