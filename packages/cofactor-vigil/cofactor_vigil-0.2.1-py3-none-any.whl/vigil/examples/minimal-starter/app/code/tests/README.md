# Tests

This directory is for project-specific tests. The minimal-starter template is intentionally bare-bones,
so no tests are included by default.

## Adding Tests

As you develop your project, add tests here:

```python
# test_my_step.py
from pathlib import Path
from app.code.lib.steps import process

def test_process_filters_correctly(tmp_path):
    """Test that the process step filters data correctly."""
    # Your test here
    pass
```

## Running Tests

```bash
# Run all tests
uv run pytest app/code/tests

# Run with coverage
uv run pytest app/code/tests --cov=app/code --cov-report=term-missing

# Run specific test
uv run pytest app/code/tests/test_my_step.py
```

## Test Structure

Organize tests to mirror your code structure:

```
app/code/tests/
├── test_steps.py          # Tests for lib/steps/
├── test_pipeline.py       # Integration tests for Snakefile
└── conformance/           # Golden baseline tests
    └── metrics_golden.json
```

See the `imaging-starter` template for examples of comprehensive tests.
