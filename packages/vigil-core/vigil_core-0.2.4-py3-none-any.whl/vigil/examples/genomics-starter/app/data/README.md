# Genomics Data Documentation

## Overview

This directory contains data handles and sample datasets for the genomics analysis pipeline.

## Directory Structure

```
app/data/
├── handles/                    # Data handle descriptors (.dhandle.json)
│   └── variants.dhandle.json   # Variant data handle with remote URI
└── samples/                    # Offline fallback data
    └── variants.csv            # Sample variant data (synthetic)
```

## Data Handles

Data handles provide typed references to datasets with support for both remote storage and offline fallbacks.

### Variants Data Handle

**File**: `handles/variants.dhandle.json`

- **Remote URI**: `s3://genomics-bucket/cohort-2024/variants/variants.vcf.gz`
- **Format**: VCF (Variant Call Format)
- **Offline Fallback**: `samples/variants.csv` (40 synthetic variants)
- **Schema**: Chromosome, position, ref/alt alleles, quality, depth, frequency, genotype, gene
- **Metadata**: Illumina NovaSeq, GRCh38 genome build, GATK HaplotypeCaller

The pipeline automatically uses the offline fallback when the remote URI is unavailable.

## Large File Handling Strategies

Genomics workflows often involve large files (BAM, CRAM, VCF.gz). This template demonstrates several strategies:

### 1. Remote Storage with Offline Samples

Store large files remotely (S3, GCS) and use small sample datasets for local development:

```json
{
  "uri": "s3://bucket/large-file.vcf.gz",
  "offline_fallback": "app/data/samples/small-sample.csv"
}
```

**Benefits**:
- Full dataset available in production
- Small sample for offline development
- No large files in git repository

### 2. Parquet Format for Efficiency

Convert large text files to Parquet for columnar storage and compression:

```python
import pandas as pd

# Read VCF-like data
df = pd.read_csv("variants.csv")

# Write to Parquet (5-10x smaller than CSV)
df.to_parquet("variants.parquet", compression="snappy")
```

**Benefits**:
- 5-10x size reduction vs CSV
- Faster read/write operations
- Column-level compression
- Schema enforcement

### 3. Indexed Access for BAM/CRAM

For alignment files, use indexed formats with region-specific queries:

```json
{
  "uri": "s3://bucket/sample.cram",
  "index_uri": "s3://bucket/sample.cram.crai",
  "reference_uri": "s3://bucket/GRCh38.fa",
  "offline_fallback": "app/data/samples/coverage_summary.json"
}
```

Extract only the data you need:

```bash
# Extract specific region
samtools view -b sample.cram chr17:41196312-41277500 > brca1_region.bam

# Compute coverage for specific region
samtools depth -r chr17:41196312-41277500 sample.cram > coverage.txt
```

**Benefits**:
- Access specific regions without downloading entire file
- Significantly faster for targeted analysis
- CRAM format is 30-50% smaller than BAM

### 4. Checksum Manifests

For large multi-file datasets, use manifest files with checksums:

```json
{
  "manifest_uri": "s3://bucket/cohort-manifest.json",
  "format": "manifest",
  "total_size_gb": 2500,
  "file_count": 1000,
  "offline_fallback": "app/data/samples/subset-manifest.json"
}
```

Manifest format:

```json
{
  "files": [
    {
      "path": "patient_001.cram",
      "size_bytes": 2500000000,
      "checksum": "sha256:abc123...",
      "uri": "s3://bucket/patient_001.cram"
    }
  ]
}
```

**Benefits**:
- Verify file integrity without downloading
- Track large datasets efficiently
- Enable selective download

### 5. Streaming Processing

Process large files without loading entirely into memory:

```python
import pandas as pd

# Read VCF in chunks
for chunk in pd.read_csv("large_variants.csv", chunksize=10000):
    # Process chunk
    filtered = chunk[chunk["quality_score"] >= 30]
    # Write to output
    filtered.to_parquet("output.parquet", mode="append")
```

**Benefits**:
- Constant memory usage regardless of file size
- Process files larger than available RAM
- Enable parallel processing

## Data Ethics & Compliance

### Synthetic Data

The sample data in `samples/variants.csv` is **entirely synthetic** and contains no real patient information.

- **PII**: None (synthetic patient IDs only)
- **Sensitive Data**: None (synthetic genetic variants)
- **Consent**: Not applicable (synthetic data)
- **IRB Review**: Not required (synthetic data)

### Real Data Requirements

When using this template with real genomics data, ensure:

#### 1. Institutional Approval
- IRB/Ethics committee approval for genetic research
- Protocol number documented in data handles
- Regular protocol renewals

#### 2. Informed Consent
- Explicit consent for genetic data collection
- Consent for specific research uses
- Consent for data sharing (if applicable)
- Right to withdraw consent

#### 3. De-identification
- Remove or hash patient identifiers
- Remove dates (except year if needed)
- Remove locations (zip codes, addresses)
- Remove demographic information that could re-identify

#### 4. Secure Storage
- Encrypted storage (at rest and in transit)
- Access controls and audit logs
- Secure credential management
- Regular security audits

#### 5. Regulatory Compliance
- **HIPAA** (USA): Health information privacy
- **GDPR** (EU): General data protection
- **GINA** (USA): Genetic information nondiscrimination
- **21 CFR Part 11** (USA FDA): Electronic records for clinical trials

#### 6. Data Sharing Considerations
- dbGaP controlled access (for NIH-funded research)
- Repository-specific consent requirements
- Publication embargo periods
- Acknowledgment requirements

## File Format Guidelines

### VCF (Variant Call Format)
- Standard format for variant data
- Use `.vcf.gz` with tabix index for efficiency
- Include header lines with metadata
- Document genome build version

### BAM/CRAM (Alignment Format)
- CRAM preferred (30-50% smaller than BAM)
- Always include index file (.bai or .crai)
- Document reference genome used
- Consider region-specific extraction for analysis

### BED (Regions Format)
- Tab-separated, 0-based coordinates
- Use for gene lists, target regions, ROIs
- Document coordinate system (0-based vs 1-based)

### Parquet (Efficient Storage)
- Use for intermediate results
- Columnar format with compression
- Schema enforcement
- Fast query performance

## Data Validation

Before running the pipeline, validate your data:

### Check Data Handle Syntax
```bash
vigil doctor
```

### Verify Checksums
```bash
vigil verify app/code/receipts/receipt_*.json
```

### Validate Data Format
```python
import pandas as pd

# Check required columns
df = pd.read_csv("app/data/samples/variants.csv")
required_cols = ["chromosome", "position", "ref_allele", "alt_allele", "quality_score"]
assert all(col in df.columns for col in required_cols)
```

### Check Data Quality
```python
# Check for missing values
assert df["quality_score"].notna().all()

# Check value ranges
assert (df["quality_score"] >= 0).all()
assert (df["depth"] > 0).all()
assert (df["allele_frequency"].between(0, 1)).all()
```

## References

- **VCF Specification**: https://samtools.github.io/hts-specs/
- **BAM/CRAM Specification**: https://samtools.github.io/hts-specs/
- **dbGaP**: https://www.ncbi.nlm.nih.gov/gap/
- **HIPAA Guidance**: https://www.hhs.gov/hipaa/
- **GDPR**: https://gdpr.eu/

## Contact

For data-related questions or to report data quality issues, contact:

- **Data Steward**: [Your Name]
- **Email**: [Your Email]
- **IRB Protocol**: [Protocol Number]
