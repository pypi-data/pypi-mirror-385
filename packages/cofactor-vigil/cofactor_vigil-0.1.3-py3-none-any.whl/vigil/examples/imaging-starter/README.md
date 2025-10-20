---
title: __PROJECT__
description: __DESCRIPTION__
author: __AUTHOR_NAME__
email: __AUTHOR_EMAIL__
license: __LICENSE__
created: __CREATED__
tags: [imaging, microscopy, analysis, starter]
status: active
version: 1.0
domain: microscopy
---

# Imaging Starter — Vigil Template

> A batteries-included template for reproducible microscopy analysis with Vigil receipts.

## Overview

This template demonstrates a complete microscopy analysis workflow with Vigil receipts, including:

- Reproducible pipelines via Snakemake (process → metrics → sciencecast)
- Typed data handles with offline fallbacks
- Automatic provenance tracking with receipts
- Modern tooling (uv, Ruff, pytest, MyPy)
- AI agent integration via MCP
- Supply chain security with capsule-first design

**Vigil URL:**

```
vigil://labs.example/acme-lab/imaging-starter@refs/heads/main?img=sha256:58b3e701ed9da8768554a21ffe7fa9afd995702d002b4b5d4798365a79310277&inputs=s3://demo-bucket/microscopy/
```

## What's Included

- ✅ **Reproducible pipelines** via Snakemake with process → metrics → sciencecast
- ✅ **Typed data handles** with offline CSV fallbacks
- ✅ **Vigil receipts** for automatic provenance tracking
- ✅ **Modern tooling**: uv, Ruff, pytest, MyPy
- ✅ **AI agent hooks** ready for MCP-based assistants
- ✅ **Capsule-first** supply chain with policy guards

## Hypothesis

This template demonstrates that microscopy analysis workflows can be made fully reproducible, auditable, and collaborative using Vigil's receipt-based provenance system. By combining threshold-based segmentation with automated metrics and timeline visualization, we show that scientific rigor doesn't require complex tooling overhead.

## Methods

The analysis pipeline implements a three-stage workflow:

1. **Segmentation** - Threshold-based cell detection from microscopy images
2. **Validation** - Comparison against ground truth with standard ML metrics
3. **Visualization** - Timeline generation for sciencecast replay

All processing occurs within a containerized environment (capsule) with pinned dependencies, ensuring reproducibility across systems. Data handles provide typed references to datasets with offline fallbacks for disconnected development.

## Quick Start

```bash
# From the Vigil monorepo root:
vigil new imaging-starter my-imaging-project
cd my-imaging-project

# Install dependencies
uv sync

# Preview the pipeline (dry-run)
vigil dev

# Execute the pipeline
vigil run --cores 4

# Promote artifacts to receipts
vigil promote

# Check health
vigil doctor
```

## Pipeline Overview

The default Snakemake workflow chains three steps:

1. **process** (`app/code/lib/steps/segment.py`)
   - Loads data handle from `app/data/handles/data.parquet.dhandle.json`
   - Uses offline CSV fallback when offline
   - Applies threshold from `app/code/configs/params.yaml`
   - Outputs `app/code/artifacts/processed.parquet`

2. **metrics** (`app/code/lib/steps/metrics.py`)
   - Compares processed output to ground truth
   - Computes accuracy, precision, recall, F1
   - Emits `app/code/artifacts/metrics.json`

3. **sciencecast** (`app/code/tools/sciencecast.py`)
   - Combines artifacts into timeline JSON
   - Records events, metadata, file summaries
   - Outputs `app/notes/sciencecast/main_pipeline_replay.json`

## Repository Layout

```
imaging-starter/
├── vigil.yaml                      # Manifest: capsule, inputs, policies
├── .vigil/workspace.spec.json      # Generated workspace spec
├── capsule/                        # Container recipe
├── app/
│   ├── code/
│   │   ├── pipelines/Snakefile     # Main workflow
│   │   ├── lib/steps/              # Pure processing steps
│   │   ├── tools/                  # Vigil tooling (promote, anchor, etc.)
│   │   ├── ai/mcp/                 # MCP server + auto-target agent
│   │   ├── ui/                     # Workbench bootstrap
│   │   └── tests/                  # Conformance + unit tests
│   ├── data/
│   │   ├── handles/                # Typed data references
│   │   └── samples/                # Offline CSV/Parquet fallbacks
│   └── notes/
│       ├── notebooks/              # Jupyter notebooks
│       ├── sciencecast/            # Timeline viewer
│       └── method/                 # Method card
└── .github/workflows/              # CI: checks, preview, release, anchor
```

## Key Commands

All core commands use the `vigil` CLI (install globally: `uv tool install cofactor-vigil`):

### Development

```bash
vigil dev                           # Dry-run + DAG preview
vigil run --cores 4                 # Execute full pipeline
vigil run --target metrics          # Execute specific target
vigil run --promote                 # Execute + promote to receipts
uv run conformance                  # Check against golden baseline (domain-specific)
```

### Receipt Management

```bash
vigil promote                       # Generate receipts from artifacts
vigil anchor                        # Create Merkle bundles
vigil url                           # Print vigil:// URL
vigil spec sync                     # Sync workspace specification
```

### Profiles

```bash
vigil run --profile cpu             # Use CPU profile
vigil run --profile gpu             # Use GPU profile
vigil run --profile slurm           # Use SLURM profile
vigil run --profile tee             # Use TEE profile + attestation
```

### Health & Maintenance

```bash
vigil doctor                        # Validate capsule, storage, GPU
vigil spec sync                     # Sync workspace.spec.json
vigil spec --dry-run                # Preview workspace spec changes
```

Note: Core tools (promote, doctor, anchor, vigilurl, workspace_spec) are provided by the `vigil` package. Domain-specific tools (conformance, sciencecast, ci_guard) remain in `app/code/tools/`.

### AI & Workbench

```bash
vigil mcp serve                     # Start MCP server
vigil ui bootstrap                  # Generate workbench config
vigil ai propose                    # Generate suggestions
vigil ai apply                      # Execute suggestions
```

## Data Handles

Data access runs through `.dhandle.json` descriptors:

```json
{
  "uri": "s3://demo-bucket/microscopy/data.parquet",
  "format": "parquet",
  "offline_fallback": "app/data/samples/data.csv",
  "schema": { ... },
  "consent": { ... }
}
```

The pipeline prefers offline fallbacks when present, enabling fully disconnected development.

## Receipts & Provenance

`vigil promote` walks `app/code/artifacts/` and produces:

- `app/code/receipts/receipt_*.json` - Vigil receipt with git refs, capsule digests, metrics
- `app/code/receipts/evidence_graph.json` - Provenance graph
- `app/code/receipts/index.json` - Receipt index

Receipts inherit glyph metadata (`RECEIPT`, `DATA_TABLE`, optional `TEE`) and are ready for signed anchors.

## Federated Variant

A federated A/B simulation is available:

```bash
vigil run --pipeline federated --cores 2
```

This simulates two study sites producing per-site receipts with DP aggregation.

## Data Ethics

This template uses **synthetic microscopy data only** with no real subjects or identifiable information. The sample data is generated for demonstration and testing purposes.

**Consent**: Not applicable (synthetic data)
**PII**: No personally identifiable information
**Sensitive Data**: No sensitive information (synthetic only)
**IRB Review**: Not required (synthetic data)
**De-identification**: Not applicable (data never contained real subjects)

When using this template with real microscopy data, ensure:
- Appropriate institutional review board (IRB) approval
- Subject consent for data collection and analysis
- Proper de-identification of any metadata
- Compliance with data sharing and privacy regulations (HIPAA, GDPR, etc.)

See `app/data/README.md` for dataset-specific ethics documentation.

## Results

Using this template with the default parameters, you can expect:

**Segmentation Performance** (with default threshold 0.5):
- Accuracy: ~0.85
- Precision: ~0.80
- Recall: ~0.75
- F1 Score: ~0.77

**Provenance Outputs**:
- Complete receipts with git refs, capsule digests, input/output tracking
- Evidence graphs showing data lineage
- Indexed receipts for efficient lookup
- Optional SLSA attestations with cryptographic signatures

**Reproducibility**:
- Bit-for-bit identical results across runs with same inputs
- Portable capsules run on any Docker-compatible system
- Offline-capable with sample data fallbacks

## Reuse

This template is designed for adaptation to real microscopy workflows:

**For Basic Use**:
1. Replace sample data with your microscopy datasets
2. Adjust threshold parameters for your cell types
3. Update ground truth for your validation approach
4. Run conformance checks to validate results

**For Advanced Workflows**:
1. Add multi-stage segmentation pipelines
2. Integrate ML models (U-Net, Mask R-CNN, etc.)
3. Add multi-channel imaging support
4. Implement custom metrics and validation

**For Production Deployment**:
1. Enable TEE profile for hardware attestation
2. Add signing keys for receipt verification
3. Configure GPU resources for acceleration
4. Set up CI/CD for automated testing

See the [Vigil documentation](https://docs.vigil.science) for guidance on extending templates.

## Extending the Template

1. Add new data handles in `app/data/handles/` with matching samples in `app/data/samples/`
2. Create new processing steps in `app/code/lib/steps/`
3. Wire them into `app/code/pipelines/Snakefile`
4. Update `app/code/tests/` with unit tests or golden metrics
5. Regenerate sciencecast timelines and receipts

## CI & Supply Chain

- GitHub Actions replicate local checks, run conformance, publish preview links
- `uv.lock` guarantees reproducible environments
- `app/code/tools/ci_guard` blocks PRs that modify capsule digests without pinning
- `.github/workflows/release.yml` builds/signs capsules, generates SBOMs, pins digests

## License

Apache-2.0 (see LICENSE)
