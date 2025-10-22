---
title: Imaging Starter Dataset
description: Sample microscopy data with segmentation ground truth
license: __LICENSE__
size: 500 KB
splits: [sample, validation]
format: Parquet
consent: not_applicable
pii: false
tags: [microscopy, imaging, segmentation, sample]
domain: microscopy
---

# Imaging Starter Dataset

## Description

This dataset contains sample microscopy data for the imaging-starter Vigil template. It includes:

- Simulated cell imaging data
- Ground truth segmentation labels
- Metadata for image acquisition parameters

The data is synthetic and designed for testing microscopy analysis pipelines.

## Schema

### data.parquet

| Column | Type | Description |
|--------|------|-------------|
| id | integer | Unique sample identifier |
| intensity | float | Cell intensity measurement |
| area | float | Cell area (pixels²) |
| predicted | boolean | Predicted segmentation label |
| actual | boolean | Ground truth label |
| image_id | string | Source image identifier |

## Splits

- **sample**: 10,000 rows of synthetic microscopy data in `samples/data.csv`
- **validation**: Subset used for ground truth comparison in metrics step

## Ethics & Privacy

**Consent**: Not applicable (synthetic data)
**PII**: No personally identifiable information
**Sensitive**: No sensitive information
**IRB**: Not required (synthetic data)
**De-identification**: Not applicable (data never contained real subjects)

## Usage

### Loading Data

The pipeline uses data handles to load data:

```python
import polars as pl

# Via data handle (preferred)
from vigil.data import load_data_handle
df = load_data_handle("app/data/handles/data.parquet.dhandle.json")

# Or directly from samples
df = pl.read_csv("app/data/samples/data.csv")
```

### Segmentation Workflow

```python
# Apply threshold-based segmentation
threshold = 0.5
predictions = df.with_columns(
    pl.when(pl.col("intensity") >= threshold)
    .then(True)
    .otherwise(False)
    .alias("predicted")
)

# Compare to ground truth
from app.code.lib.steps.metrics import compute_metrics
metrics = compute_metrics(predictions, "predicted", "actual")
```

### Expected Metrics

With default threshold (0.5), you should see:

- **Accuracy**: ~0.85
- **Precision**: ~0.80
- **Recall**: ~0.75
- **F1**: ~0.77

## Data Handle

See `app/data/handles/data.parquet.dhandle.json` for the canonical data handle descriptor with schema and offline fallback configuration.

## Extending

To use your own microscopy data:

1. Update the data handle URI to point to your data source
2. Add offline samples that match your schema
3. Adjust the threshold and processing steps in `app/code/lib/steps/segment.py`
4. Update ground truth validation in `app/code/lib/steps/metrics.py`

## License

This dataset is licensed under __LICENSE__.
