"""Card schemas for Experiment and Dataset cards following Hugging Face patterns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ExperimentCardSchema:
    """Schema for Experiment Card (README.md at project root).

    Combines YAML front-matter with Markdown content sections.
    """

    # Required front-matter fields
    title: str
    description: str
    author: str
    email: str
    license: str
    created: str  # ISO date format YYYY-MM-DD

    # Optional front-matter fields
    tags: list[str] | None = None

    # Required markdown sections
    REQUIRED_SECTIONS = [
        "# ",  # Title header
        "## Overview",
        "## Hypothesis",
        "## Methods",
        "## Data Ethics",
        "## Results",
        "## Reuse",
    ]

    @staticmethod
    def get_required_fields() -> list[str]:
        """Return list of required front-matter fields."""
        return ["title", "description", "author", "email", "license", "created"]

    @staticmethod
    def get_optional_fields() -> list[str]:
        """Return list of optional front-matter fields."""
        return ["tags"]

    @staticmethod
    def get_required_sections() -> list[str]:
        """Return list of required markdown sections."""
        return ExperimentCardSchema.REQUIRED_SECTIONS


@dataclass
class DatasetCardSchema:
    """Schema for Dataset Card (app/data/README.md).

    Combines YAML front-matter with Markdown content sections.
    """

    # Required front-matter fields
    title: str
    description: str
    license: str

    # Optional front-matter fields
    size: str | None = None
    splits: list[str] | None = None
    schema_fields: list[dict[str, Any]] | None = None
    consent: str | None = None
    pii: str | None = None

    # Required markdown sections
    REQUIRED_SECTIONS = [
        "# ",  # Title header
        "## Description",
        "## Schema",
        "## Splits",
        "## Ethics & Privacy",
        "## Usage",
    ]

    @staticmethod
    def get_required_fields() -> list[str]:
        """Return list of required front-matter fields."""
        return ["title", "description", "license"]

    @staticmethod
    def get_optional_fields() -> list[str]:
        """Return list of optional front-matter fields."""
        return ["size", "splits", "schema", "consent", "pii"]

    @staticmethod
    def get_required_sections() -> list[str]:
        """Return list of required markdown sections."""
        return DatasetCardSchema.REQUIRED_SECTIONS
