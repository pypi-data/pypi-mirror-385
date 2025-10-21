"""Vigil: Observable, collaborative, reproducible science platform.

This package provides the core Vigil CLI and tools for creating reproducible
scientific workflows with automatic provenance tracking.

Example:
    Install the CLI globally:
        $ uv tool install cofactor-vigil

    Create a new project:
        $ vigil new imaging-starter my-project
        $ cd my-project
        $ vigil run --cores 4
        $ vigil promote
"""

from vigil import tools

__version__ = "0.1.7"
__all__ = ["tools", "__version__"]
