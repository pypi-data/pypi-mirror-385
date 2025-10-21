---
title: __PROJECT__
description: __DESCRIPTION__
author: __AUTHOR_NAME__
email: __AUTHOR_EMAIL__
license: __LICENSE__
created: __CREATED__
tags: [genomics, variant-calling, ngs, quality-control, reproducible]
status: active
version: 1.0
domain: genomics
---

# Genomics Starter — Vigil Template

> A batteries-included template for reproducible genomics analysis with Vigil receipts.

## Overview

This template demonstrates a complete genomics analysis workflow with Vigil receipts, including:

- Reproducible pipelines via Snakemake (filter → annotate → metrics → sciencecast)
- Typed data handles with offline fallbacks for large files
- Automatic provenance tracking with receipts
- Modern tooling (uv, Ruff, pytest, MyPy)
- AI agent integration via MCP
- Supply chain security with capsule-first design
- Large file handling strategies for NGS data (BAM, VCF, CRAM)

**Vigil URL:**

```
vigil://labs.example/__ORG__/__PROJECT__@refs/heads/main?img=sha256:0000000000000000000000000000000000000000000000000000000000000000&inputs=s3://genomics-bucket/cohort-2024/
```

## What's Included

- ✅ **Reproducible pipelines** via Snakemake with filter → annotate → metrics → sciencecast
- ✅ **Typed data handles** with offline CSV/Parquet fallbacks for large genomics files
- ✅ **Vigil receipts** for automatic provenance tracking
- ✅ **Modern tooling**: uv, Ruff, pytest, MyPy
- ✅ **AI agent hooks** ready for MCP-based assistants
- ✅ **Capsule-first** supply chain with policy guards
- ✅ **Large file strategies** for NGS data (BAM, VCF, CRAM files)

## Hypothesis

This template demonstrates that genomics analysis workflows—from variant calling to annotation and QC—can be made fully reproducible, auditable, and collaborative using Vigil's receipt-based provenance system. By combining standard quality filters with automated metrics and timeline visualization, we show that scientific rigor in genomics doesn't require complex tooling overhead.

## Methods

The analysis pipeline implements a four-stage workflow:

1. **Filtering** - Quality-based variant filtering (PHRED scores, depth, allele frequency)
2. **Annotation** - Variant annotation with gene information and functional impact
3. **Metrics** - Comprehensive QC metrics (Ti/Tv ratio, depth distribution, variant counts)
4. **Visualization** - Timeline generation for sciencecast replay

All processing occurs within a containerized environment (capsule) with pinned dependencies, ensuring reproducibility across systems. Data handles provide typed references to datasets with offline fallbacks for disconnected development.

## Quick Start

```bash
# Install Vigil CLI (if not already installed)
uv tool install cofactor-vigil

# Create new project from genomics-starter
vigil new genomics-starter my-genomics-project
cd my-genomics-project

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

# Get vigil:// URL
vigil url
```

## Pipeline Overview

The default Snakemake workflow chains four steps:

1. **filter** (`app/code/lib/steps/filter.py`)
   - Loads variant data from data handle
   - Applies quality filters (PHRED ≥ 30, depth ≥ 20x, AF ≥ 0.01)
   - Filters by variant type (SNV, INDEL)
   - Outputs `app/code/artifacts/filtered_variants.parquet`

2. **annotate** (`app/code/lib/steps/annotate.py`)
   - Annotates variants with gene information
   - Adds functional impact predictions
   - Adds population frequency data
   - Outputs `app/code/artifacts/annotated_variants.parquet`

3. **metrics** (`app/code/lib/steps/metrics.py`)
   - Computes comprehensive QC metrics:
     - Ti/Tv ratio (transition/transversion)
     - Depth distribution statistics
     - Variant counts by type, chromosome, gene
     - Allele frequency spectrum
   - Emits `app/code/artifacts/variant_metrics.json`

4. **sciencecast** (`app/code/tools/sciencecast.py`)
   - Combines artifacts into timeline JSON
   - Records events, metadata, file summaries
   - Outputs `app/notes/sciencecast/main_pipeline_replay.json`

## Repository Layout

```
genomics-starter/
├── vigil.yaml                      # Manifest: capsule, inputs, policies
├── .vigil/workspace.spec.json      # Generated workspace spec
├── capsule/                        # Container recipe
├── app/
│   ├── code/
│   │   ├── pipelines/Snakefile     # Main workflow
│   │   ├── lib/steps/              # Pure processing steps
│   │   ├── tools/                  # Genomics tools (vcf_utils, bam_utils)
│   │   ├── configs/
│   │   │   ├── params/             # Pipeline parameters
│   │   │   └── profiles/           # Snakemake profiles
│   │   ├── artifacts/              # Output directory
│   │   ├── receipts/               # Receipt directory
│   │   └── tests/                  # Conformance + unit tests
│   ├── data/
│   │   ├── handles/                # Typed data references (VCF, BAM)
│   │   └── samples/                # Offline CSV/Parquet fallbacks
│   └── notes/
│       ├── notebooks/              # Jupyter notebooks
│       ├── sciencecast/            # Timeline viewer
│       └── method/                 # Method card
└── .github/workflows/              # CI: checks, preview, release
```

## Key Commands

All core commands use the `vigil` CLI:

### Development

```bash
vigil dev                           # Dry-run + DAG preview
vigil run --cores 4                 # Execute full pipeline
vigil run --target metrics          # Execute specific target
vigil run --promote                 # Execute + promote to receipts
```

### Receipt Management

```bash
vigil promote                       # Generate receipts from artifacts
vigil verify app/code/receipts/receipt_*.json  # Verify checksums
vigil url                           # Print vigil:// URL
vigil spec --sync                   # Sync workspace specification
```

### Health & Maintenance

```bash
vigil doctor                        # Validate capsule, storage, version
vigil spec --sync                   # Sync workspace.spec.json
vigil spec --dry-run                # Preview workspace spec changes
```

## Data Handles & Large File Strategies

Genomics workflows often involve large files (BAM, CRAM, VCF.gz). This template demonstrates several strategies:

### Strategy 1: Remote Storage with Offline Fallback

For large files, use remote storage (S3, GCS) with a small sample for offline development:

```json
{
  "uri": "s3://genomics-bucket/cohort-2024/variants.vcf.gz",
  "format": "vcf",
  "offline_fallback": "app/data/samples/variants_sample.csv",
  "schema": {
    "chromosome": "string",
    "position": "integer",
    "ref_allele": "string",
    "alt_allele": "string"
  }
}
```

The pipeline prefers the remote URI when available, but falls back to the sample CSV for disconnected development.

### Strategy 2: Parquet for Intermediate Results

Convert large text files (VCF, BED) to Parquet format for efficient columnar storage:

```python
import pandas as pd
import pyarrow.parquet as pq

# Read VCF-like data
df = pd.read_csv("variants.csv")

# Write to Parquet with compression
df.to_parquet(
    "filtered_variants.parquet",
    compression="snappy",
    index=False
)
```

Parquet files are typically 5-10x smaller than CSV and much faster to query.

### Strategy 3: Indexed Access for BAM/CRAM

For alignment files, create data handles that reference indexed files:

```json
{
  "uri": "s3://genomics-bucket/sample_001.cram",
  "format": "cram",
  "index_uri": "s3://genomics-bucket/sample_001.cram.crai",
  "reference_uri": "s3://genomics-bucket/references/GRCh38.fa",
  "offline_fallback": "app/data/samples/sample_001_summary.json"
}
```

Use tools like `samtools view` with region queries to extract only needed data.

### Strategy 4: Checksum Manifests

For very large datasets, use manifest files with checksums:

```json
{
  "manifest_uri": "s3://genomics-bucket/cohort-manifest.json",
  "format": "manifest",
  "total_size_gb": 2500,
  "file_count": 1000,
  "offline_fallback": "app/data/samples/cohort_subset_manifest.json"
}
```

The manifest contains checksums for each file, enabling verification without downloading.

## Data Ethics

This template uses **synthetic genomics data only** with no real subjects or identifiable information. The sample data is generated for demonstration and testing purposes.

**Consent**: Not applicable (synthetic data)
**PII**: No personally identifiable information
**Sensitive Data**: No sensitive genetic information (synthetic only)
**IRB Review**: Not required (synthetic data)
**De-identification**: Not applicable (data never contained real subjects)

When using this template with real genomics data, ensure:
- Appropriate institutional review board (IRB) approval
- Subject consent for genetic data collection and analysis
- Proper de-identification of metadata (patient IDs, dates, locations)
- Compliance with genetic data regulations (GINA, HIPAA, GDPR)
- Secure storage and access controls for sensitive data

See `app/data/README.md` for dataset-specific ethics documentation.

## Results

Using this template with the default parameters, you can expect:

**Variant Quality Metrics** (with default filters):
- Mean PHRED quality score: 45-60
- Mean sequencing depth: 30-50x
- Ti/Tv ratio: ~2.0 (expected for whole-genome)
- Pass rate: 70-85% (depending on initial quality)

**Provenance Outputs**:
- Complete receipts with git refs, capsule digests, input/output tracking
- Evidence graphs showing data lineage
- Indexed receipts for efficient lookup
- Optional SLSA attestations with cryptographic signatures

**Reproducibility**:
- Deterministic results across runs with same inputs
- Portable capsules run on any Docker-compatible system
- Offline-capable with sample data fallbacks

## Reuse

This template is designed for adaptation to real genomics workflows:

**For Basic Use**:
1. Replace sample data with your variant datasets
2. Adjust quality filter thresholds for your sequencing platform
3. Update annotation sources (dbSNP, ClinVar, gnomAD)
4. Run conformance checks to validate results

**For Advanced Workflows**:
1. Add variant calling from BAM files (GATK, FreeBayes)
2. Integrate structural variant detection (Manta, Delly)
3. Add copy number variation analysis
4. Implement population genetics metrics

**For Clinical Genomics**:
1. Add pathogenicity prediction (CADD, REVEL)
2. Integrate clinical databases (ClinVar, OMIM)
3. Add trio analysis for germline variants
4. Implement ACMG/AMP classification

See the [Vigil documentation](https://docs.vigil.science) for guidance on extending templates.

## Extending the Template

1. Add new data handles in `app/data/handles/` with matching samples in `app/data/samples/`
2. Create new processing steps in `app/code/lib/steps/`
3. Wire them into `app/code/pipelines/Snakefile`
4. Update `app/code/tests/` with unit tests or golden metrics
5. Regenerate sciencecast timelines and receipts

## Common Genomics Tools Integration

This template provides utilities for common genomics tools:

### VCF Processing
```python
from app.code.tools.vcf_utils import read_vcf, filter_vcf, annotate_vcf

# Read VCF file
variants = read_vcf("variants.vcf.gz")

# Apply quality filters
filtered = filter_vcf(variants, min_qual=30, min_depth=20)

# Annotate with gene info
annotated = annotate_vcf(filtered, annotation_db="ensembl")
```

### BAM Processing
```python
from app.code.tools.bam_utils import compute_coverage, extract_region

# Compute coverage statistics
coverage = compute_coverage("sample.bam", regions="exons.bed")

# Extract specific region
reads = extract_region("sample.bam", "chr17:41196312-41277500")
```

## Performance Considerations

For large genomics datasets:

1. **Use indexed formats**: BAM, CRAM, VCF.gz with tabix indexes
2. **Parallelize by chromosome**: Split processing across chromosomes
3. **Use memory-efficient formats**: Parquet instead of CSV, CRAM instead of BAM
4. **Stream large files**: Don't load entire files into memory
5. **Use temp directories**: Configure Snakemake temp dirs on fast storage

## CI & Supply Chain

- GitHub Actions replicate local checks, run conformance, publish preview links
- `uv.lock` guarantees reproducible environments
- Capsule digests ensure supply chain integrity
- `.github/workflows/release.yml` builds/signs capsules, generates SBOMs

## License

Apache-2.0 (see LICENSE)
