# Vigil CLI

Observable, collaborative, reproducible science platform.

## Installation

### Base Installation

```bash
# Install core CLI with uv
uv tool install cofactor-vigil

# Or with pip
pip install cofactor-vigil
```

The base installation includes only the core CLI commands (`new`, `dev`, `build`, `run`, `promote`, `anchor`, `doctor`, etc.).

### MCP Server Installation

To use the MCP server (`vigil mcp serve`), install with the `mcp` extras:

```bash
# Install with MCP server support
uv tool install "cofactor-vigil[mcp]"

# Or with pip
pip install "cofactor-vigil[mcp]"
```

The `mcp` extras include:
- `mcp>=1.1.0` - MCP protocol server
- `polars>=0.20.0` - Fast data frame library for data previews

## Quick Start

```bash
# Create a new project from a template
vigil new imaging-starter my-project
cd my-project

# Install dependencies
uv sync

# Preview the pipeline (dry-run)
vigil dev

# Execute the pipeline
vigil run --cores 4

# Promote artifacts to receipts
vigil promote

# Anchor receipts with Merkle proofs
vigil anchor
```

## Commands

### Project Management

- `vigil new <template> [path]` - Create a new project from a template
- `vigil new --list` - List available templates

### Development

- `vigil dev` - Dry-run the pipeline and preview the DAG
- `vigil build` - Execute the pipeline without promotion
- `vigil run` - Execute targets and optionally promote
- `vigil conformance` - Check outputs against golden baselines (project-specific, not all templates include this)

### Receipt Management

- `vigil promote` - Generate Vigil receipts from artifacts
- `vigil anchor` - Create Merkle anchors for receipts
- `vigil url` - Print the vigil:// URL for the project
- `vigil verify` - Verify receipt checksums and attestations

### Health & Maintenance

- `vigil doctor` - Run repository health checks
- `vigil spec --sync` - Sync workspace.spec.json with vigil.yaml
- `vigil spec --dry-run` - Preview workspace spec changes

### Documentation & Collaboration

- `vigil card init` - Create experiment or dataset cards
- `vigil card lint` - Validate card format and required fields
- `vigil notes new` - Create timestamped lab notebook entries
- `vigil notes index` - Regenerate lab notebook index

### Workbench & AI

- `vigil ui bootstrap` - Generate Workbench configuration
- `vigil mcp serve` - Start the MCP server for assistants
- `vigil ai propose` - Generate auto-target suggestions
- `vigil ai apply` - Execute auto-target proposal

## Templates

Available starter templates:

- **imaging-starter**: Full-featured imaging pipeline with sciencecast timeline
- **minimal-starter**: Smallest viable template for getting started

## Documentation

- [Getting Started](../../docs/getting-started.md)
- [CLI Reference](../../docs/cli-reference.md)
- [Creating Custom Templates](../../docs/creating-starters.md)

## License

Apache-2.0
