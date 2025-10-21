# Lab Notebook Templates

This directory contains templates for creating structured lab notebook entries.

## Available Templates

### Experiment Entry
Use this template to document individual experiments with standardized metadata:
- Date, author, and status tracking
- Structured sections for materials, methods, results
- Cross-references to computational receipts
- Next steps and action items

### Protocol
Use this template to document standard operating procedures:
- Version control for protocols
- Validation dates
- Materials, equipment, and procedures
- Safety and quality control checkpoints

## Usage

Create new notes using the Vigil CLI:

```bash
# Create a new experiment entry
vigil notes new experiment "Initial segmentation test" --author "Jane Doe"

# Create a new protocol
vigil notes new protocol "Cell culture protocol" --author "Jane Doe"

# Regenerate the index
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

Lab notebook entries are designed to work seamlessly with Vigil's computational receipts:

1. Run experiments using `vigil run`
2. Document outcomes in experiment entries
3. Link to computational receipts in `app/code/receipts/`
4. Cross-reference related protocols and experiments

This creates an auditable trail from lab work to computational analysis to results.
