"""Vigil notes module for lab notebook templates and scaffolding."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

__all__ = [
    "create_experiment_entry",
    "create_protocol",
    "generate_index",
    "get_template_path",
]


def get_template_path(template_name: str) -> Path:
    """Get the path to a template file.

    Args:
        template_name: Name of the template (e.g., 'experiment_entry.md')

    Returns:
        Path to the template file

    Raises:
        FileNotFoundError: If template doesn't exist
    """
    template_path = Path(__file__).parent / "templates" / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_name}")
    return template_path


def _slugify(text: str) -> str:
    """Convert text to a URL-safe slug.

    Args:
        text: Text to slugify

    Returns:
        Slugified text (lowercase, hyphens, alphanumeric)
    """
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug


def create_experiment_entry(
    title: str,
    author: str,
    output_dir: Path,
    date: str | None = None,
    status: str = "in_progress",
    tags: list[str] | None = None,
) -> Path:
    """Create a new experiment entry from template.

    Args:
        title: Experiment title
        author: Author name
        output_dir: Directory to write the experiment entry
        date: Date in YYYY-MM-DD format (defaults to today)
        status: Experiment status (in_progress, completed, failed)
        tags: List of tags for the experiment

    Returns:
        Path to the created experiment entry file
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    if tags is None:
        tags = []

    # Generate filename: YYYY-MM-DD_slug.md
    slug = _slugify(title)
    filename = f"{date}_{slug}.md"
    output_path = output_dir / filename

    # Load template
    template_path = get_template_path("experiment_entry.md")
    template_content = template_path.read_text()

    # Replace placeholders
    content = template_content.format(
        date=date,
        author=author,
        title=title,
        status=status,
        tags=", ".join(tags),
    )

    # Write file
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)

    return output_path


def create_protocol(
    title: str,
    author: str,
    output_dir: Path,
    version: str = "1.0",
    validated: str | None = None,
) -> Path:
    """Create a new protocol from template.

    Args:
        title: Protocol title
        author: Author name
        output_dir: Directory to write the protocol
        version: Protocol version
        validated: Validation date in YYYY-MM-DD format

    Returns:
        Path to the created protocol file
    """
    if validated is None:
        validated = datetime.now().strftime("%Y-%m-%d")

    # Generate filename: slug.md
    slug = _slugify(title)
    filename = f"{slug}.md"
    output_path = output_dir / filename

    # Load template
    template_path = get_template_path("protocol.md")
    template_content = template_path.read_text()

    # Replace placeholders
    content = template_content.format(
        title=title,
        version=version,
        author=author,
        validated=validated,
    )

    # Write file
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content)

    return output_path


def generate_index(notes_dir: Path) -> Path:
    """Generate an index of all experiments and protocols.

    Args:
        notes_dir: Root notes directory (e.g., app/notes/)

    Returns:
        Path to the generated index file (README.md)
    """
    experiments_dir = notes_dir / "experiments"
    protocols_dir = notes_dir / "protocols"

    # Collect experiments (sorted by date, newest first)
    experiments: list[tuple[str, Path]] = []
    if experiments_dir.exists():
        for exp_file in sorted(experiments_dir.glob("*.md"), reverse=True):
            # Extract date and title from filename: YYYY-MM-DD_slug.md
            match = re.match(r"(\d{4}-\d{2}-\d{2})_(.+)\.md", exp_file.name)
            if match:
                date_str, slug = match.groups()
                title = slug.replace("-", " ").title()
                experiments.append((f"{date_str}: {title}", exp_file))

    # Collect protocols (sorted alphabetically)
    protocols: list[tuple[str, Path]] = []
    if protocols_dir.exists():
        for proto_file in sorted(protocols_dir.glob("*.md")):
            if proto_file.name.lower() != "readme.md":
                title = proto_file.stem.replace("-", " ").title()
                protocols.append((title, proto_file))

    # Generate index content
    lines = ["# Lab Notebook\n\n"]

    if experiments:
        lines.append("## Recent Experiments\n")
        for title, path in experiments[:10]:  # Show last 10 experiments
            rel_path = path.relative_to(notes_dir)
            lines.append(f"- [{title}]({rel_path})\n")
        lines.append("\n")

    if protocols:
        lines.append("## Protocols\n")
        for title, path in protocols:
            rel_path = path.relative_to(notes_dir)
            lines.append(f"- [{title}]({rel_path})\n")
        lines.append("\n")

    lines.append("## Analysis\n")
    lines.append("See [app/code/receipts/](../code/receipts/) for computational receipts.\n")

    # Write index
    index_path = notes_dir / "README.md"
    index_path.write_text("".join(lines))

    return index_path
