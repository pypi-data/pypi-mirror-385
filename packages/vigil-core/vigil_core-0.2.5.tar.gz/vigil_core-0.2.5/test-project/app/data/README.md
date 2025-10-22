---
title: Minimal Starter Dataset
description: Simple threshold-based data for testing Vigil pipelines
license: __LICENSE__
size: 100 KB
splits: [sample]
format: CSV
consent: not_applicable
pii: false
tags: [sample, minimal, threshold]
---

# Minimal Starter Dataset

## Description

This dataset contains sample data for the minimal-starter Vigil template. It demonstrates the basic workflow of loading data, applying a threshold filter, and producing artifacts.

The data is synthetic and designed for testing purposes only.

## Schema

### data.csv

| Column | Type | Description |
|--------|------|-------------|
| id | integer | Unique identifier |
| value | float | Numeric value for threshold filtering |
| category | string | Sample category label |

## Splits

- **sample**: 1000 rows of synthetic data in `samples/data.csv`

## Ethics & Privacy

**Consent**: Not applicable (synthetic data)
**PII**: No personally identifiable information
**Sensitive**: No sensitive information
**IRB**: Not required (synthetic data)

## Usage

### Loading Data

The pipeline uses data handles to load data:

```python
import polars as pl

# Via data handle
df = pl.read_csv("app/data/samples/data.csv")
```

### Filtering Example

```python
# Apply threshold filter
threshold = 0.5
filtered = df.filter(pl.col("value") >= threshold)
```

### Expected Output

The processed data should contain only rows where `value >= threshold`.

## Data Handle

See `app/data/handles/data.parquet.dhandle.json` for the canonical data handle descriptor.

## License

This dataset is licensed under __LICENSE__.
