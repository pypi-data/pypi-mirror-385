"""Tests for vigil.cards module."""

from __future__ import annotations

import tempfile
from pathlib import Path

from typer.testing import CliRunner
from vigil import cli
from vigil.cards.linter import lint_card, lint_dataset_card, lint_experiment_card
from vigil.cards.schemas import DatasetCardSchema, ExperimentCardSchema

runner = CliRunner()


# ============================================================================
# SCHEMA TESTS
# ============================================================================


def test_experiment_card_schema_required_fields():
    """Test that ExperimentCardSchema has correct required fields."""
    required = ExperimentCardSchema.get_required_fields()
    assert "title" in required
    assert "description" in required
    assert "author" in required
    assert "email" in required
    assert "license" in required
    assert "created" in required


def test_experiment_card_schema_optional_fields():
    """Test that ExperimentCardSchema has correct optional fields."""
    optional = ExperimentCardSchema.get_optional_fields()
    assert "tags" in optional


def test_experiment_card_schema_required_sections():
    """Test that ExperimentCardSchema has correct required sections."""
    sections = ExperimentCardSchema.get_required_sections()
    assert "# " in sections
    assert "## Overview" in sections
    assert "## Hypothesis" in sections
    assert "## Methods" in sections
    assert "## Data Ethics" in sections
    assert "## Results" in sections
    assert "## Reuse" in sections


def test_dataset_card_schema_required_fields():
    """Test that DatasetCardSchema has correct required fields."""
    required = DatasetCardSchema.get_required_fields()
    assert "title" in required
    assert "description" in required
    assert "license" in required


def test_dataset_card_schema_optional_fields():
    """Test that DatasetCardSchema has correct optional fields."""
    optional = DatasetCardSchema.get_optional_fields()
    assert "size" in optional
    assert "splits" in optional
    assert "schema" in optional
    assert "consent" in optional
    assert "pii" in optional


def test_dataset_card_schema_required_sections():
    """Test that DatasetCardSchema has correct required sections."""
    sections = DatasetCardSchema.get_required_sections()
    assert "# " in sections
    assert "## Description" in sections
    assert "## Schema" in sections
    assert "## Splits" in sections
    assert "## Ethics & Privacy" in sections
    assert "## Usage" in sections


# ============================================================================
# LINTER TESTS - VALID CARDS
# ============================================================================


def test_lint_valid_experiment_card():
    """Test linting a valid experiment card."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Project
description: A test project
author: Test Author
email: test@example.com
license: Apache-2.0
created: 2025-01-20
tags: [test, demo]
---

# Test Project

## Overview
Overview content

## Hypothesis
Hypothesis content

## Methods
Methods content

## Data Ethics
Ethics content

## Results
Results content

## Reuse
Reuse content
""")

        result = lint_experiment_card(card_path)
        assert result.valid
        assert len(result.errors) == 0


def test_lint_valid_dataset_card():
    """Test linting a valid dataset card."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Dataset
description: A test dataset
license: CC-BY-4.0
size: 1000 rows
splits:
  - train
  - test
schema:
  - name: id
    type: int
  - name: value
    type: float
consent: IRB-approved
pii: none
---

# Test Dataset

## Description
Description content

## Schema
Schema content

## Splits
Splits content

## Ethics & Privacy
Ethics content

## Usage
Usage content
""")

        result = lint_dataset_card(card_path)
        assert result.valid
        assert len(result.errors) == 0


# ============================================================================
# LINTER TESTS - INVALID CARDS
# ============================================================================


def test_lint_experiment_card_missing_required_field():
    """Test linting experiment card with missing required field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Project
description: A test project
author: Test Author
# Missing email
license: Apache-2.0
created: 2025-01-20
---

# Test Project

## Overview
Content

## Hypothesis
Content

## Methods
Content

## Data Ethics
Content

## Results
Content

## Reuse
Content
""")

        result = lint_experiment_card(card_path)
        assert not result.valid
        assert any("email" in error for error in result.errors)


def test_lint_experiment_card_invalid_email():
    """Test linting experiment card with invalid email format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Project
description: A test project
author: Test Author
email: not-an-email
license: Apache-2.0
created: 2025-01-20
---

# Test Project

## Overview
Content

## Hypothesis
Content

## Methods
Content

## Data Ethics
Content

## Results
Content

## Reuse
Content
""")

        result = lint_experiment_card(card_path)
        assert not result.valid
        assert any("email" in error.lower() for error in result.errors)


def test_lint_experiment_card_invalid_date():
    """Test linting experiment card with invalid date format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Project
description: A test project
author: Test Author
email: test@example.com
license: Apache-2.0
created: 01/20/2025
---

# Test Project

## Overview
Content

## Hypothesis
Content

## Methods
Content

## Data Ethics
Content

## Results
Content

## Reuse
Content
""")

        result = lint_experiment_card(card_path)
        assert not result.valid
        assert any("date" in error.lower() for error in result.errors)


def test_lint_experiment_card_missing_section():
    """Test linting experiment card with missing required section."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Project
description: A test project
author: Test Author
email: test@example.com
license: Apache-2.0
created: 2025-01-20
---

# Test Project

## Overview
Content

## Hypothesis
Content

## Methods
Content

## Data Ethics
Content

## Results
Content

# Missing Reuse section
""")

        result = lint_experiment_card(card_path)
        assert not result.valid
        assert any("Reuse" in error for error in result.errors)


def test_lint_experiment_card_unknown_license_warning():
    """Test linting experiment card with unknown license (warning, not error)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Project
description: A test project
author: Test Author
email: test@example.com
license: Custom-License-1.0
created: 2025-01-20
---

# Test Project

## Overview
Content

## Hypothesis
Content

## Methods
Content

## Data Ethics
Content

## Results
Content

## Reuse
Content
""")

        result = lint_experiment_card(card_path)
        # Should be valid but with warnings
        assert result.valid
        assert len(result.warnings) > 0
        assert any("license" in warning.lower() for warning in result.warnings)


def test_lint_dataset_card_missing_required_field():
    """Test linting dataset card with missing required field."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Dataset
# Missing description
license: CC-BY-4.0
---

# Test Dataset

## Description
Content

## Schema
Content

## Splits
Content

## Ethics & Privacy
Content

## Usage
Content
""")

        result = lint_dataset_card(card_path)
        assert not result.valid
        assert any("description" in error for error in result.errors)


def test_lint_dataset_card_invalid_schema():
    """Test linting dataset card with invalid schema format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Dataset
description: A test dataset
license: CC-BY-4.0
schema:
  - name: id
    # Missing type
  - invalid_item
---

# Test Dataset

## Description
Content

## Schema
Content

## Splits
Content

## Ethics & Privacy
Content

## Usage
Content
""")

        result = lint_dataset_card(card_path)
        assert not result.valid
        assert any("schema" in error.lower() for error in result.errors)


def test_lint_card_no_front_matter():
    """Test linting card without front-matter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""# Test Project

Just markdown content without YAML front-matter.
""")

        result = lint_experiment_card(card_path)
        assert not result.valid
        assert any("front-matter" in error.lower() for error in result.errors)


def test_lint_card_file_not_found():
    """Test linting non-existent card file."""
    result = lint_experiment_card(Path("/nonexistent/path/README.md"))
    assert not result.valid
    assert any("not found" in error.lower() for error in result.errors)


def test_lint_card_auto_detect_type():
    """Test auto-detection of card type based on path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Dataset card in data directory
        data_dir = Path(tmpdir) / "app" / "data"
        data_dir.mkdir(parents=True)
        card_path = data_dir / "README.md"
        card_path.write_text("""---
title: Test Dataset
description: A test dataset
license: CC-BY-4.0
---

# Test Dataset

## Description
Content

## Schema
Content

## Splits
Content

## Ethics & Privacy
Content

## Usage
Content
""")

        # Should auto-detect as dataset
        result = lint_card(card_path)
        assert result.valid


# ============================================================================
# CLI TESTS
# ============================================================================


def test_vigil_card_help():
    """Test that 'vigil card --help' shows card commands."""
    result = runner.invoke(cli.app, ["card", "--help"])
    assert result.exit_code == 0
    assert "lint" in result.stdout
    assert "init" in result.stdout


def test_vigil_card_init_experiment():
    """Test creating an experiment card with 'vigil card init experiment'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "README.md"
        result = runner.invoke(
            cli.app, ["card", "init", "experiment", "--output", str(output_path)]
        )

        assert result.exit_code == 0
        assert output_path.exists()

        # Verify template was copied
        content = output_path.read_text()
        assert "---" in content
        assert "title:" in content
        assert "## Overview" in content
        assert "## Hypothesis" in content


def test_vigil_card_init_dataset():
    """Test creating a dataset card with 'vigil card init dataset'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "data_README.md"
        result = runner.invoke(cli.app, ["card", "init", "dataset", "--output", str(output_path)])

        assert result.exit_code == 0
        assert output_path.exists()

        # Verify template was copied
        content = output_path.read_text()
        assert "---" in content
        assert "title:" in content
        assert "## Description" in content
        assert "## Schema" in content


def test_vigil_card_init_invalid_type():
    """Test that 'vigil card init' rejects invalid card types."""
    result = runner.invoke(cli.app, ["card", "init", "invalid_type"])
    assert result.exit_code == 1
    assert "Unknown card type" in result.stdout or "invalid_type" in result.stdout


def test_vigil_card_init_file_exists():
    """Test that 'vigil card init' fails if output file exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "README.md"
        output_path.write_text("existing content")

        result = runner.invoke(
            cli.app, ["card", "init", "experiment", "--output", str(output_path)]
        )

        assert result.exit_code == 1
        assert "already exists" in result.stdout


def test_vigil_card_lint_valid():
    """Test linting a valid card with 'vigil card lint'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Project
description: A test project
author: Test Author
email: test@example.com
license: Apache-2.0
created: 2025-01-20
---

# Test Project

## Overview
Content

## Hypothesis
Content

## Methods
Content

## Data Ethics
Content

## Results
Content

## Reuse
Content
""")

        result = runner.invoke(cli.app, ["card", "lint", str(card_path)])
        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()


def test_vigil_card_lint_invalid():
    """Test linting an invalid card with 'vigil card lint'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Project
# Missing required fields
---

# Test Project

Some content
""")

        result = runner.invoke(cli.app, ["card", "lint", str(card_path)])
        assert result.exit_code == 1
        assert "Errors:" in result.stdout or "error" in result.stdout.lower()


def test_vigil_card_lint_file_not_found():
    """Test linting non-existent file."""
    result = runner.invoke(cli.app, ["card", "lint", "/nonexistent/path/README.md"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_vigil_card_lint_with_type_option():
    """Test linting with explicit type specification."""
    with tempfile.TemporaryDirectory() as tmpdir:
        card_path = Path(tmpdir) / "README.md"
        card_path.write_text("""---
title: Test Dataset
description: A test dataset
license: CC-BY-4.0
---

# Test Dataset

## Description
Content

## Schema
Content

## Splits
Content

## Ethics & Privacy
Content

## Usage
Content
""")

        result = runner.invoke(cli.app, ["card", "lint", str(card_path), "--type", "dataset"])
        assert result.exit_code == 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_card_workflow_experiment():
    """Integration test: Create, edit, and lint experiment card."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Create card
        card_path = Path(tmpdir) / "README.md"
        result = runner.invoke(cli.app, ["card", "init", "experiment", "--output", str(card_path)])
        assert result.exit_code == 0
        assert card_path.exists()

        # Step 2: Lint the template (should be valid)
        result = runner.invoke(cli.app, ["card", "lint", str(card_path)])
        assert result.exit_code == 0

        # Step 3: Break the card
        card_path.write_text("# Broken card\nNo front-matter")

        # Step 4: Lint should fail
        result = runner.invoke(cli.app, ["card", "lint", str(card_path)])
        assert result.exit_code == 1


def test_card_workflow_dataset():
    """Integration test: Create, edit, and lint dataset card."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Step 1: Create card
        card_path = Path(tmpdir) / "dataset_README.md"
        result = runner.invoke(cli.app, ["card", "init", "dataset", "--output", str(card_path)])
        assert result.exit_code == 0
        assert card_path.exists()

        # Step 2: Lint the template (should be valid)
        result = runner.invoke(cli.app, ["card", "lint", str(card_path), "--type", "dataset"])
        assert result.exit_code == 0
