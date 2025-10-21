"""Card linter for validating Experiment and Dataset cards against schemas."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from vigil.cards.schemas import DatasetCardSchema, ExperimentCardSchema


@dataclass
class LintResult:
    """Result of linting a card."""

    valid: bool
    errors: list[str]
    warnings: list[str]


def _parse_card_file(path: Path) -> tuple[dict[str, Any] | None, str]:
    """Parse a card file into front-matter and content.

    Args:
        path: Path to the card file

    Returns:
        Tuple of (front_matter dict, content string)
    """
    content = path.read_text()

    # Extract YAML front-matter
    # Pattern: --- at start, YAML content, --- to close
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return None, content

    yaml_content = match.group(1)
    markdown_content = match.group(2)

    try:
        front_matter = yaml.safe_load(yaml_content)
    except yaml.YAMLError:
        return None, markdown_content

    return front_matter, markdown_content


def _validate_email(email: str) -> bool:
    """Validate email format."""
    # Simple email validation
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def _validate_license(license_id: str) -> bool:
    """Validate license identifier against common SPDX identifiers."""
    # Common open source licenses
    valid_licenses = {
        "Apache-2.0",
        "MIT",
        "BSD-2-Clause",
        "BSD-3-Clause",
        "GPL-2.0",
        "GPL-3.0",
        "LGPL-2.1",
        "LGPL-3.0",
        "CC-BY-4.0",
        "CC-BY-SA-4.0",
        "CC0-1.0",
        "Unlicense",
        "ISC",
        "MPL-2.0",
    }
    return license_id in valid_licenses


def _validate_iso_date(date_value: Any) -> bool:
    """Validate ISO date format (YYYY-MM-DD).

    Args:
        date_value: Date value (string or datetime.date)

    Returns:
        True if valid ISO date format
    """
    # YAML parser may convert dates to datetime.date objects
    # Accept both strings and datetime.date objects
    import datetime

    if isinstance(date_value, datetime.date):
        return True

    if not isinstance(date_value, str):
        return False

    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return bool(re.match(pattern, date_value))


def _check_sections(content: str, required_sections: list[str]) -> list[str]:
    """Check that all required sections are present in content.

    Args:
        content: Markdown content
        required_sections: List of required section headers

    Returns:
        List of missing section headers
    """
    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)
    return missing


def lint_experiment_card(path: Path) -> LintResult:
    """Lint an Experiment Card.

    Args:
        path: Path to the experiment card (README.md)

    Returns:
        LintResult with validation status and messages
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return LintResult(valid=False, errors=[f"File not found: {path}"], warnings=[])

    # Parse card
    front_matter, content = _parse_card_file(path)

    if front_matter is None:
        errors.append("No valid YAML front-matter found")
        return LintResult(valid=False, errors=errors, warnings=warnings)

    # Check required fields
    required_fields = ExperimentCardSchema.get_required_fields()
    for field in required_fields:
        if field not in front_matter:
            errors.append(f"Missing required field: {field}")

    # Validate email if present
    if "email" in front_matter:
        if not _validate_email(front_matter["email"]):
            errors.append(f"Invalid email format: {front_matter['email']}")

    # Validate license if present
    if "license" in front_matter:
        if not _validate_license(front_matter["license"]):
            warnings.append(
                f"Unknown license identifier: {front_matter['license']}. "
                "Consider using SPDX identifiers."
            )

    # Validate date format if present
    if "created" in front_matter:
        if not _validate_iso_date(front_matter["created"]):
            errors.append(f"Invalid date format: {front_matter['created']}. Use YYYY-MM-DD")

    # Check required sections
    required_sections = ExperimentCardSchema.get_required_sections()
    missing_sections = _check_sections(content, required_sections)
    for section in missing_sections:
        errors.append(f"Missing required section: {section}")

    # Check optional fields
    if "tags" in front_matter:
        if not isinstance(front_matter["tags"], list):
            errors.append("Field 'tags' must be a list")

    valid = len(errors) == 0
    return LintResult(valid=valid, errors=errors, warnings=warnings)


def lint_dataset_card(path: Path) -> LintResult:
    """Lint a Dataset Card.

    Args:
        path: Path to the dataset card (app/data/README.md)

    Returns:
        LintResult with validation status and messages
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return LintResult(valid=False, errors=[f"File not found: {path}"], warnings=[])

    # Parse card
    front_matter, content = _parse_card_file(path)

    if front_matter is None:
        errors.append("No valid YAML front-matter found")
        return LintResult(valid=False, errors=errors, warnings=warnings)

    # Check required fields
    required_fields = DatasetCardSchema.get_required_fields()
    for field in required_fields:
        if field not in front_matter:
            errors.append(f"Missing required field: {field}")

    # Validate license if present
    if "license" in front_matter:
        if not _validate_license(front_matter["license"]):
            warnings.append(
                f"Unknown license identifier: {front_matter['license']}. "
                "Consider using SPDX identifiers."
            )

    # Check required sections
    required_sections = DatasetCardSchema.get_required_sections()
    missing_sections = _check_sections(content, required_sections)
    for section in missing_sections:
        errors.append(f"Missing required section: {section}")

    # Validate schema field if present
    if "schema" in front_matter:
        schema = front_matter["schema"]
        if not isinstance(schema, list):
            errors.append("Field 'schema' must be a list of field definitions")
        else:
            for i, field in enumerate(schema):
                if not isinstance(field, dict):
                    errors.append(f"Schema field {i} must be a dict with 'name' and 'type'")
                    continue
                if "name" not in field:
                    errors.append(f"Schema field {i} missing 'name'")
                if "type" not in field:
                    errors.append(f"Schema field {i} missing 'type'")

    # Validate splits field if present
    if "splits" in front_matter:
        if not isinstance(front_matter["splits"], list):
            errors.append("Field 'splits' must be a list")

    valid = len(errors) == 0
    return LintResult(valid=valid, errors=errors, warnings=warnings)


def lint_card(path: Path, card_type: str | None = None) -> LintResult:
    """Lint a card (auto-detect type or use specified type).

    Args:
        path: Path to the card file
        card_type: Type of card ("experiment" or "dataset"). If None, auto-detect.

    Returns:
        LintResult with validation status and messages
    """
    if card_type is None:
        # Auto-detect based on path
        if "data" in str(path):
            card_type = "dataset"
        else:
            card_type = "experiment"

    if card_type == "experiment":
        return lint_experiment_card(path)
    elif card_type == "dataset":
        return lint_dataset_card(path)
    else:
        return LintResult(
            valid=False,
            errors=[f"Unknown card type: {card_type}. Use 'experiment' or 'dataset'"],
            warnings=[],
        )
