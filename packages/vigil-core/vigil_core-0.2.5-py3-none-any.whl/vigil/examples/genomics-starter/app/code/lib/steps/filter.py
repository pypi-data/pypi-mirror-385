"""Filter genomic variants based on quality metrics."""

import json
import sys
from pathlib import Path

import pandas as pd


def main():
    """Filter variants by quality score, depth, and allele frequency."""
    if len(sys.argv) < 4:
        print("Usage: filter.py <input_csv> <output_parquet> <params_json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}

    # Read variant data
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} raw variants")

    # Get filter parameters with genomics-standard defaults
    min_quality = params.get("min_quality_score", 30.0)  # PHRED >= 30
    min_depth = params.get("min_depth", 20)              # Coverage >= 20x
    min_allele_freq = params.get("min_allele_frequency", 0.01)  # AF >= 1%
    allowed_types = params.get("variant_types", ["SNV", "INDEL"])

    print(f"Filter parameters:")
    print(f"  Min quality score: {min_quality}")
    print(f"  Min depth: {min_depth}x")
    print(f"  Min allele frequency: {min_allele_freq}")
    print(f"  Allowed variant types: {allowed_types}")

    # Apply quality filters
    filtered_df = df[
        (df["quality_score"] >= min_quality)
        & (df["depth"] >= min_depth)
        & (df["allele_frequency"] >= min_allele_freq)
        & (df["variant_type"].isin(allowed_types))
    ].copy()

    print(f"Filtered to {len(filtered_df)} variants ({len(filtered_df)/len(df)*100:.1f}% pass rate)")

    # Add quality tier classification
    filtered_df["quality_tier"] = pd.cut(
        filtered_df["quality_score"],
        bins=[0, 30, 60, 100],
        labels=["moderate", "high", "excellent"],
    )

    # Add depth tier classification
    filtered_df["depth_tier"] = pd.cut(
        filtered_df["depth"],
        bins=[0, 30, 50, 1000],
        labels=["adequate", "good", "excellent"],
    )

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save to Parquet format for efficient storage
    filtered_df.to_parquet(output_path, index=False, compression="snappy")

    print(f"Saved filtered variants to {output_path}")
    print(f"  SNVs: {len(filtered_df[filtered_df['variant_type'] == 'SNV'])}")
    print(f"  INDELs: {len(filtered_df[filtered_df['variant_type'] == 'INDEL'])}")
    print(f"  Mean quality: {filtered_df['quality_score'].mean():.1f}")
    print(f"  Mean depth: {filtered_df['depth'].mean():.1f}x")


if __name__ == "__main__":
    main()
