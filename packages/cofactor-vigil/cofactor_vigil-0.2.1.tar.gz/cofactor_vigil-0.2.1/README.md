# Vigil CLI

Observable, collaborative, reproducible science platform.

## ✨ What's New in v0.2.0

**Major update with genomics support, interactive setup, and cloud execution!**

### 🎯 Interactive Project Setup (P3)
```bash
vigil new genomics-starter my-project --interactive
```
- Smart prompts with email validation
- Automatic placeholder replacement
- **97% faster** (30+ min → <1 min)

### 🧬 Genomics Template (P0)
- Complete variant analysis workflow (filter → annotate → metrics)
- 40 synthetic variants across 10 cancer genes
- Ti/Tv ratio, depth stats, quality metrics
- Parquet format (5-10x compression)

### ☁️ Cloud & HPC Support (P1 + P3)
- **HPC**: SLURM, PBS, SGE profiles (400+ line guide)
- **Cloud**: AWS Batch, Google Cloud Life Sciences, Azure Batch, Kubernetes (600+ line guide)
- Cost optimization: 70-80% savings with spot instances

### 🗄️ Database Integration (P1)
- Ensembl, ClinVar, gnomAD clients
- Local caching for offline work
- Rate limiting and error handling

### 📊 Genomics Metrics Library (P2)
- Ti/Tv ratio calculation
- Het/Hom ratio
- Depth and quality statistics
- Scientifically validated

### 🔍 Version Management (P0)
- `vigil doctor` now detects version mismatches
- Automatic upgrade recommendations

**Upgrade now:** `uv tool upgrade cofactor-vigil` or `pipx upgrade cofactor-vigil`

**Full details:** See [CHANGELOG.md](../../CHANGELOG.md)

---

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
# Create a new project from a template (with interactive setup)
vigil new genomics-starter my-project --interactive
cd my-project

# Install dependencies
uv sync

# Sync workspace spec
vigil spec --sync

# Preview the pipeline (dry-run)
vigil dev

# Execute the pipeline
vigil run --cores 4

# Promote artifacts to receipts
vigil promote

# Verify receipts
vigil verify app/code/receipts/*.json
```

## Commands

### Project Management

- `vigil new <template> [path]` - Create a new project from a template
- `vigil new <template> [path] --interactive` - Interactive setup with smart prompts (NEW in v0.2.0)
- `vigil new --list` - List available templates (now includes genomics-starter)

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

- `vigil doctor` - Run repository health checks (includes version mismatch detection)
- `vigil spec --sync` - Sync workspace.spec.json with vigil.yaml
- `vigil spec --dry-run` - Preview workspace spec changes
- `vigil version` - Show installed version (alias for `vigil --version`)

**Version Management**: The `vigil doctor` command now checks for version mismatches between local and global installations, helping prevent issues from outdated CLI versions.

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
- **genomics-starter**: Comprehensive genomics workflow with variant filtering, annotation, and QC metrics (includes large file handling strategies)
- **minimal-starter**: Smallest viable template for getting started

### Genomics Template Features

The `genomics-starter` template demonstrates:
- Variant quality filtering (PHRED scores, depth, allele frequency)
- Functional annotation with gene and pathway information
- Comprehensive QC metrics (Ti/Tv ratio, depth distribution, pathogenicity)
- Large file handling strategies for NGS data (BAM, VCF, CRAM)
- Data handles with offline fallbacks for disconnected development
- Parquet format for efficient variant storage

## Documentation

- [Getting Started](../../docs/getting-started.md)
- [CLI Reference](../../docs/cli-reference.md)
- [Creating Custom Templates](../../docs/creating-starters.md)

## License

Apache-2.0
