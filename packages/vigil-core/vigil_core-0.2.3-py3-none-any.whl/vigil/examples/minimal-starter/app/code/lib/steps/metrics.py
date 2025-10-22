"""Compute metrics from processed data."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def compute_metrics(processed_path: Path, output_path: Path) -> None:
    """Compute basic metrics from processed data.

    Args:
        processed_path: Path to processed Parquet file
        output_path: Path to output metrics JSON file
    """
    # Load processed data
    df = pd.read_parquet(processed_path)

    # Compute simple metrics
    metrics = {
        "n": len(df),
        "mean_value": float(df["value"].mean()) if len(df) > 0 else 0.0,
        "median_value": float(df["value"].median()) if len(df) > 0 else 0.0,
        "std_value": float(df["value"].std()) if len(df) > 0 else 0.0,
    }

    # Save metrics
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Computed metrics: n={metrics['n']}, mean={metrics['mean_value']:.3f}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python metrics.py <processed_parquet> <output_json>")
        sys.exit(1)

    processed_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    compute_metrics(processed_path, output_path)
