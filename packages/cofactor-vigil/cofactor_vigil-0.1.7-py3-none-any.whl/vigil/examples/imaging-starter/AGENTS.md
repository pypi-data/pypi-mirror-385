# AI Agents Guide

This repository is designed to work seamlessly with AI agents and assistants. Here's how to interact with it effectively.

## Available Tools

### Core Commands
- `vigil run --cores 4` - Run the full pipeline locally
- `vigil promote` - Generate receipts for artifacts
- `uv run conformance` - Check against golden metrics
- `vigil url` - Generate shareable VigilURL
- `vigil doctor` - Run health checks

### AI Tool-Calling Verbs
The repository exposes these verbs for AI agents:

1. **preview_data** - Examine data handles and samples
2. **run_target** - Execute specific pipeline targets
3. **promote** - Generate receipts for completed runs

## Data Structure

### Inputs
- `app/data/handles/` - Typed data handles with S3 URIs and offline fallbacks
- `app/data/samples/` - Small sample datasets for offline development

### Outputs
- `app/code/artifacts/` - Pipeline outputs (gitignored)
- `app/code/receipts/` - Generated receipts with checksums (gitignored)

### Configuration
- `vigil.yaml` - Main configuration file
- `app/code/configs/params.yaml` - Pipeline parameters
- `app/code/configs/profiles/` - Environment-specific configs (cpu, gpu, slurm)

## Best Practices for AI Agents

1. **Use vigil CLI for core commands** - `vigil run`, `vigil promote`, `vigil doctor`
2. **Check conformance** - Run `uv run conformance` before promoting artifacts
3. **Generate receipts** - Use `vigil promote` for all meaningful outputs
4. **Respect offline mode** - Sample data allows development without S3 access
5. **Use typed data handles** - Leverage the dhandle.json format for data pointers

## Notebook Integration

- `app/notes/notebooks/` - Jupyter notebooks for exploration
- Use "Send selection to Notebook" feature for AI-generated code cells
- Notebooks are git-tracked for reproducibility

## CI/CD Integration

- GitHub Actions run conformance checks on PRs
- Vigil preview links are automatically generated
- All checks use `uv run` for consistency

## Troubleshooting

- If `uv` is not available, install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- For S3 access issues, check that sample data exists in `app/data/samples/`
- Conformance failures indicate pipeline changes - update golden metrics if intentional
