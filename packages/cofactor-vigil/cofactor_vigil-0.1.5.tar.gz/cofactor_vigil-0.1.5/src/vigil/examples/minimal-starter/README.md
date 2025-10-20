---
title: __PROJECT__
description: __DESCRIPTION__
author: __AUTHOR_NAME__
email: __AUTHOR_EMAIL__
license: __LICENSE__
created: __CREATED__
tags: [minimal, starter, template]
status: active
version: 1.0
---

# Minimal Starter — Vigil Template

> The smallest viable Vigil template for getting started quickly.

## Overview

This is the minimal Vigil template demonstrating the core concepts of reproducible science with receipts. It includes:

- ✅ Single data handle with offline CSV fallback
- ✅ One processing step (threshold filter)
- ✅ Minimal Snakemake pipeline
- ✅ Basic receipt promotion
- ✅ Health checks

This is the bare minimum needed for a reproducible Vigil project. Perfect for learning the basics or starting a simple analysis.

## Hypothesis

This template demonstrates that simple data processing workflows can be made fully reproducible with minimal overhead using Vigil's receipt-based approach.

## Methods

The template uses a threshold-based filtering approach to demonstrate the basic Vigil workflow. Data is loaded from a data handle (with offline fallback), processed through a Snakemake pipeline, and promoted to a cryptographically-signed receipt.

## Quick Start

```bash
# Install Vigil CLI (if not already installed)
uv tool install cofactor-vigil

# Create new project
vigil new minimal-starter my-project
cd my-project

# Install dependencies
uv sync

# Preview the pipeline
vigil dev

# Run the pipeline
vigil run --cores 2

# Promote to receipt
vigil promote

# Check health
vigil doctor

# Get vigil:// URL
vigil url
```

## Structure

```
minimal-starter/
├── vigil.yaml                       # Manifest
├── .vigil/workspace.spec.json       # Workspace spec
├── app/
│   ├── code/
│   │   ├── pipelines/Snakefile      # Single rule pipeline
│   │   ├── lib/steps/process.py     # Threshold filter
│   │   ├── tools/                   # promote.py, doctor.py
│   │   ├── artifacts/               # Output directory
│   │   └── receipts/                # Receipt directory
│   └── data/
│       ├── handles/                 # Data handle descriptor
│       └── samples/data.csv         # Offline sample data
```

## Pipeline

The pipeline has one rule that applies a threshold filter:

1. Loads `app/data/samples/data.csv`
2. Filters rows where `value >= threshold` (default: 0.5)
3. Saves to `app/code/artifacts/processed.parquet`

Adjust the threshold in `app/code/configs/params.yaml`.

## Commands

All commands use the `vigil` CLI from the package:

```bash
vigil dev              # Dry-run the pipeline
vigil run              # Execute the pipeline
vigil promote          # Generate receipt
vigil doctor           # Health checks
vigil url              # Print vigil:// URL
vigil spec --sync      # Sync workspace spec
```

The tools are provided by the `vigil` package, not local scripts.

## Data Ethics

This template uses **synthetic data only** with no personally identifiable information (PII) or sensitive content. The sample data is generated for demonstration purposes and does not represent real subjects or experiments.

**Consent**: Not applicable (synthetic data)
**Privacy**: No privacy concerns (synthetic data)
**Ethics Review**: Not required (synthetic data)

When using this template with real data, ensure appropriate consent, IRB approval, and data handling procedures are in place.

## Results

Using this template, you can expect to:

- Generate receipts with complete provenance tracking (git refs, capsule digests, inputs, outputs)
- Produce reproducible artifacts with cryptographic verification
- Establish a baseline workflow for more complex analyses

## Reuse

This template is designed to be extended and adapted:

1. **For simple analyses**: Use as-is with minimal modifications
2. **For complex workflows**: Add more steps, data handles, and validation
3. **As a learning tool**: Study the structure and adapt patterns to your domain

To add more functionality:

1. Add new steps in `app/code/lib/steps/`
2. Update `app/code/pipelines/Snakefile` with new rules
3. Add more data handles in `app/data/handles/`
4. Copy tools from `imaging-starter` as needed

See the [Vigil documentation](https://docs.vigil.science) for guidance on extending templates.

## Next Steps

Once you're comfortable with the basics, check out:

- `imaging-starter` - Full-featured pipeline with metrics and sciencecast

## License

Apache-2.0
