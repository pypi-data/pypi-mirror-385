"""Generate sciencecast timeline from genomics pipeline artifacts."""

import json
import sys
from datetime import datetime
from pathlib import Path


def main():
    """Create sciencecast timeline JSON."""
    if len(sys.argv) < 2:
        print("Usage: sciencecast.py <output_json>")
        sys.exit(1)

    output_path = Path(sys.argv[1])

    # Define artifact paths
    artifacts_dir = Path("app/code/artifacts")
    filtered_variants = artifacts_dir / "filtered_variants.parquet"
    annotated_variants = artifacts_dir / "annotated_variants.parquet"
    metrics_json = artifacts_dir / "variant_metrics.json"

    # Load metrics if available
    metrics = {}
    if metrics_json.exists():
        with metrics_json.open("r") as f:
            metrics = json.load(f)

    # Build timeline
    timeline = {
        "title": "Genomics Pipeline Timeline",
        "description": "Variant filtering, annotation, and QC metrics pipeline",
        "created_at": datetime.now().isoformat(),
        "events": [
            {
                "timestamp": datetime.now().isoformat(),
                "event": "pipeline_start",
                "description": "Started genomics analysis pipeline",
            },
            {
                "timestamp": datetime.now().isoformat(),
                "event": "filter_complete",
                "description": f"Filtered variants to {metrics.get('total_variants', 'N/A')} high-quality calls",
                "artifact": str(filtered_variants),
            },
            {
                "timestamp": datetime.now().isoformat(),
                "event": "annotation_complete",
                "description": "Added functional annotations to variants",
                "artifact": str(annotated_variants),
                "details": {
                    "unique_genes": metrics.get("unique_genes", 0),
                    "pathogenicity": metrics.get("pathogenicity_distribution", {}),
                },
            },
            {
                "timestamp": datetime.now().isoformat(),
                "event": "metrics_computed",
                "description": "Computed comprehensive QC metrics",
                "artifact": str(metrics_json),
                "details": {
                    "mean_quality": metrics.get("mean_quality_score", 0),
                    "mean_depth": metrics.get("mean_depth", 0),
                    "ti_tv_ratio": metrics.get("ti_tv_ratio", 0),
                },
            },
        ],
        "summary": {
            "total_variants": metrics.get("total_variants", 0),
            "unique_genes": metrics.get("unique_genes", 0),
            "mean_quality_score": metrics.get("mean_quality_score", 0),
            "ti_tv_ratio": metrics.get("ti_tv_ratio", 0),
        },
    }

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save timeline
    with output_path.open("w") as f:
        json.dump(timeline, f, indent=2)

    print(f"Generated sciencecast timeline: {output_path}")
    print(f"  Total variants: {timeline['summary']['total_variants']}")
    print(f"  Unique genes: {timeline['summary']['unique_genes']}")
    print(f"  Ti/Tv ratio: {timeline['summary']['ti_tv_ratio']:.2f}")


if __name__ == "__main__":
    main()
