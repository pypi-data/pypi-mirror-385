# Lab Notebook

Welcome to your Vigil lab notebook! This directory provides a structured way to document your microscopy experiments and image analysis workflows.

## Quick Start

Create new notes using the Vigil CLI:

```bash
# Create a new experiment entry
vigil notes new experiment "Cell segmentation validation" --author "Your Name"

# Create a new protocol
vigil notes new protocol "Cell culture and imaging protocol" --author "Your Name"

# Regenerate the index after adding notes
vigil notes index
```

## Directory Structure

```
app/notes/
├── README.md              # This file (auto-generated index)
├── experiments/           # Individual experiment entries
│   └── YYYY-MM-DD_title.md
└── protocols/             # Standard operating procedures
    └── protocol-name.md
```

## Integration with Vigil

Lab notebook entries integrate with the imaging pipeline:

1. Document imaging protocols and experimental designs
2. Run image analysis using `vigil run --target segment_cells`
3. Create experiment entries to record observations and results
4. Link to computational receipts and output data
5. Reference protocols in experiment entries

This creates a complete audit trail from sample preparation through image acquisition, analysis, and publication.

## Example Workflow

### 1. Create a Protocol

```bash
vigil notes new protocol "HeLa cell culture and staining" --author "Jane Doe"
```

### 2. Run Analysis

```bash
vigil run --target segment_cells --cores 4
```

### 3. Document Results

```bash
vigil notes new experiment "Initial segmentation results" \
  --author "Jane Doe" \
  --tags "imaging,segmentation,HeLa" \
  --status "completed"
```

### 4. Update Index

```bash
vigil notes index
```

## Tips

- Use consistent tags across experiments for easier searching
- Reference related protocols and receipts in experiment entries
- Update experiment status as work progresses
- Regenerate the index regularly to keep the notebook organized
