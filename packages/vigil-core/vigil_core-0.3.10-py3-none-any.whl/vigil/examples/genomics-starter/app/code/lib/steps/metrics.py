"""Compute comprehensive genomics QC metrics from annotated variants."""

import json
import sys
from pathlib import Path

import pandas as pd


def compute_ti_tv_ratio(df: pd.DataFrame) -> float:
    """Calculate transition/transversion ratio for SNVs."""
    snvs = df[df["variant_type"] == "SNV"]

    if len(snvs) == 0:
        return 0.0

    # Define transitions and transversions
    transitions = [("A", "G"), ("G", "A"), ("C", "T"), ("T", "C")]
    transversions = [
        ("A", "C"), ("A", "T"), ("C", "A"), ("C", "G"),
        ("G", "C"), ("G", "T"), ("T", "A"), ("T", "G"),
    ]

    ti_count = sum(
        1 for _, row in snvs.iterrows()
        if (row["ref_allele"], row["alt_allele"]) in transitions
    )
    tv_count = sum(
        1 for _, row in snvs.iterrows()
        if (row["ref_allele"], row["alt_allele"]) in transversions
    )

    return ti_count / tv_count if tv_count > 0 else 0.0


def main():
    """Calculate comprehensive genomics QC metrics."""
    if len(sys.argv) < 3:
        print("Usage: metrics.py <input_parquet> <output_json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    # Read annotated variant data
    df = pd.read_parquet(input_path)
    print(f"Computing metrics for {len(df)} annotated variants")

    # Calculate comprehensive metrics
    metrics = {
        # Basic counts
        "total_variants": len(df),
        "unique_patients": df["patient_id"].nunique() if "patient_id" in df.columns else 0,
        "unique_genes": df["gene"].nunique(),
        "unique_chromosomes": df["chromosome"].nunique(),

        # Quality metrics
        "mean_quality_score": float(df["quality_score"].mean()),
        "median_quality_score": float(df["quality_score"].median()),
        "min_quality_score": float(df["quality_score"].min()),
        "max_quality_score": float(df["quality_score"].max()),

        # Coverage/depth metrics
        "mean_depth": float(df["depth"].mean()),
        "median_depth": float(df["depth"].median()),
        "min_depth": int(df["depth"].min()),
        "max_depth": int(df["depth"].max()),

        # Allele frequency metrics
        "mean_allele_frequency": float(df["allele_frequency"].mean()),
        "median_allele_frequency": float(df["allele_frequency"].median()),

        # Variant type distribution
        "variant_types": df["variant_type"].value_counts().to_dict(),

        # Ti/Tv ratio (key QC metric for genomics)
        "ti_tv_ratio": float(compute_ti_tv_ratio(df)),

        # Genotype distribution
        "genotype_distribution": df["genotype"].value_counts().to_dict(),

        # Chromosome distribution
        "variants_per_chromosome": df["chromosome"].value_counts().to_dict(),

        # Top affected genes
        "top_genes": df["gene"].value_counts().head(10).to_dict(),

        # Annotation metrics
        "variant_effects": df["variant_effect"].value_counts().to_dict() if "variant_effect" in df.columns else {},
        "pathogenicity_distribution": df["pathogenicity"].value_counts().to_dict() if "pathogenicity" in df.columns else {},

        # Quality tier distribution
        "quality_tiers": df["quality_tier"].value_counts().to_dict() if "quality_tier" in df.columns else {},
        "depth_tiers": df["depth_tier"].value_counts().to_dict() if "depth_tier" in df.columns else {},
    }

    print(f"Computed metrics:")
    print(f"  {metrics['total_variants']} variants across {metrics['unique_genes']} genes")
    print(f"  {metrics['unique_chromosomes']} chromosomes")
    print(f"  Mean quality score: {metrics['mean_quality_score']:.1f}")
    print(f"  Mean coverage depth: {metrics['mean_depth']:.1f}x")
    print(f"  Ti/Tv ratio: {metrics['ti_tv_ratio']:.2f}")
    print(f"  Pathogenicity:")
    for category, count in metrics.get("pathogenicity_distribution", {}).items():
        print(f"    {category}: {count}")

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save metrics
    with output_path.open("w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved metrics to {output_path}")


if __name__ == "__main__":
    main()
