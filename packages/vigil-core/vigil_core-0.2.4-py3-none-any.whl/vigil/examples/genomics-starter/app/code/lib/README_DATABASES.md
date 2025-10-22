# Genomics Database Integration Guide

This guide explains how to integrate common genomics annotation databases into your Vigil workflows.

## Quick Start

```python
from app.code.lib.genomics_databases import (
    EnsemblClient,
    ClinVarClient,
    GnomADClient,
    annotate_variants_with_databases,
)

# Annotate variants with all databases
annotated_df = annotate_variants_with_databases(
    variants_df,
    use_ensembl=True,
    use_clinvar=True,
    use_gnomad=True,
    cache_dir="~/.vigil/annotation_cache",
)
```

## Supported Databases

### 1. Ensembl

**Purpose**: Gene annotation, transcript information, variant consequences

**Data provided**:
- Gene IDs, symbols, descriptions
- Transcript information
- Variant effects (missense, nonsense, splice site)
- SIFT and PolyPhen predictions

**Example**:

```python
from app.code.lib.genomics_databases import EnsemblClient

client = EnsemblClient(cache_dir="~/.vigil/cache")

# Lookup gene by symbol
gene = client.get_gene_by_symbol("BRCA1", species="human")
print(f"Gene ID: {gene['id']}")
print(f"Location: {gene['seq_region_name']}:{gene['start']}-{gene['end']}")
print(f"Description: {gene['description']}")

# Get variant consequences
consequences = client.get_variant_consequences(
    chromosome="17",
    position=41245466,
    alleles="G/A",
    species="human",
)
print(f"Most severe consequence: {consequences[0]['most_severe_consequence']}")
```

**API Documentation**: https://rest.ensembl.org/

**Rate limits**: 15 requests/second

### 2. ClinVar

**Purpose**: Clinical significance of genetic variants

**Data provided**:
- Clinical significance (Pathogenic, Likely pathogenic, VUS, Benign, etc.)
- Review status (expert reviewed, criteria provided, no assertion)
- Associated conditions/diseases
- Submission history

**Example**:

```python
from app.code.lib.genomics_databases import ClinVarClient

client = ClinVarClient(
    cache_dir="~/.vigil/cache",
    email="your.email@example.com",  # Recommended for NCBI APIs
)

# Search for variant
result = client.search_variant(
    chromosome="17",
    position=41245466,
    ref="G",
    alt="A",
)

print(f"Clinical significance: {result['clinical_significance']}")
print(f"Review status: {result['review_status']}")
```

**API Documentation**: https://www.ncbi.nlm.nih.gov/clinvar/docs/help/

**Rate limits**: 3 requests/second without API key, 10 requests/second with key

### 3. gnomAD

**Purpose**: Population allele frequencies

**Data provided**:
- Allele frequency (overall and by population)
- Allele count and allele number
- Homozygote count
- Quality metrics (depth, quality score)

**Example**:

```python
from app.code.lib.genomics_databases import GnomADClient

client = GnomADClient(cache_dir="~/.vigil/cache")

# Get allele frequency
freq = client.get_allele_frequency(
    chromosome="17",
    position=41245466,
    ref="G",
    alt="A",
)

print(f"Allele frequency: {freq['allele_freq']:.6f}")
print(f"Allele count: {freq['allele_count']}/{freq['allele_number']}")
```

**API Documentation**: https://gnomad.broadinstitute.org/api/

**Rate limits**: No official limit, but be respectful (1-2 requests/second)

### 4. dbSNP

**Purpose**: Known variant IDs and frequencies

**Data provided**:
- rsID (reference SNP ID)
- Minor allele frequency (MAF)
- Validation status
- Clinical significance

**Example**:

```python
# dbSNP queries typically use rsID
import requests

def get_dbsnp_info(rsid: str) -> dict:
    """Query dbSNP for variant information."""
    url = f"https://api.ncbi.nlm.nih.gov/variation/v0/beta/refsnp/{rsid}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()

# Example
info = get_dbsnp_info("rs80357906")  # BRCA1 pathogenic variant
print(f"rsID: {info['refsnp_id']}")
print(f"Alleles: {info['primary_snapshot_data']['allele_annotations']}")
```

**API Documentation**: https://api.ncbi.nlm.nih.gov/variation/v0/

## Caching for Offline Work

All database clients cache results locally to enable:
- Faster subsequent queries
- Offline development and testing
- Reduced API load

**Cache location**: `~/.vigil/annotation_cache/`

**Cache format**: JSON files with MD5 hash keys

**Clear cache**:

```bash
rm -rf ~/.vigil/annotation_cache/
```

**Check cache size**:

```bash
du -sh ~/.vigil/annotation_cache/
```

## Integration with Pipeline

### Option 1: Annotate During Pipeline

Modify `app/code/lib/steps/annotate.py`:

```python
from app.code.lib.genomics_databases import annotate_variants_with_databases

def main():
    # Read filtered variants
    df = pd.read_parquet(input_path)

    # Annotate with databases
    annotated_df = annotate_variants_with_databases(
        df,
        use_ensembl=True,
        use_clinvar=True,
        use_gnomad=True,
    )

    # Save annotated variants
    annotated_df.to_parquet(output_path)
```

### Option 2: Pre-download Annotations

For large datasets, pre-download annotations:

```python
# scripts/predownload_annotations.py
from app.code.lib.genomics_databases import EnsemblClient, ClinVarClient, GnomADClient
import pandas as pd

# Load variants
variants = pd.read_csv("variants.csv")

# Initialize clients
ensembl = EnsemblClient()
clinvar = ClinVarClient()
gnomad = GnomADClient()

# Query all variants (results are cached)
for _, variant in variants.iterrows():
    clinvar.search_variant(variant["chromosome"], variant["position"], ...)
    gnomad.get_allele_frequency(variant["chromosome"], variant["position"], ...)

print("Annotations cached for offline use")
```

Then run pipeline offline:

```bash
# Predownload annotations (with internet)
python scripts/predownload_annotations.py

# Run pipeline (offline)
vigil run --cores 4
```

## Best Practices

### 1. Respect Rate Limits

```python
import time

def query_with_rate_limit(client, variants, rate_limit=1.0):
    """Query database with rate limiting."""
    results = []
    for variant in variants:
        result = client.query(variant)
        results.append(result)
        time.sleep(1.0 / rate_limit)  # Wait between requests
    return results
```

### 2. Batch Queries When Possible

Some APIs support batch queries:

```python
# Ensembl VEP supports batch mode
variants = ["17:41245466:G:A", "17:41246481:C:T", "13:32890598:T:C"]
response = requests.post(
    "https://rest.ensembl.org/vep/human/region",
    headers={"Content-Type": "application/json"},
    json={"variants": variants},
)
```

### 3. Handle API Errors Gracefully

```python
import requests
from requests.exceptions import RequestException

def safe_query(client, *args, max_retries=3):
    """Query with automatic retries."""
    for attempt in range(max_retries):
        try:
            return client.query(*args)
        except RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            # Log error and return placeholder
            print(f"Query failed after {max_retries} attempts: {e}")
            return {"error": str(e)}
```

### 4. Validate Input Data

```python
def validate_variant(chromosome: str, position: int, ref: str, alt: str) -> bool:
    """Validate variant format before querying."""
    # Check chromosome format
    if not chromosome.startswith("chr"):
        chromosome = f"chr{chromosome}"

    # Check position is positive
    if position <= 0:
        return False

    # Check alleles are valid nucleotides
    valid_bases = set("ACGT")
    if not (set(ref) <= valid_bases and set(alt) <= valid_bases):
        return False

    return True
```

### 5. Monitor API Usage

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoredClient:
    def __init__(self):
        self.query_count = 0
        self.cache_hits = 0

    def query(self, *args):
        self.query_count += 1
        result = self.cache.get(key)
        if result:
            self.cache_hits += 1
            logger.info(f"Cache hit ({self.cache_hits}/{self.query_count})")
        else:
            logger.info(f"API query ({self.query_count})")
        return result

    def stats(self):
        cache_rate = self.cache_hits / self.query_count if self.query_count > 0 else 0
        return f"Queries: {self.query_count}, Cache rate: {cache_rate:.1%}"
```

## Common Issues

### Issue 1: API Rate Limit Exceeded

**Error**: `HTTP 429 Too Many Requests`

**Solution**: Add rate limiting:

```python
import time
from functools import wraps

def rate_limit(calls_per_second=1.0):
    """Decorator to rate-limit function calls."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=1.0)
def query_clinvar(variant):
    ...
```

### Issue 2: Timeout Errors

**Error**: `requests.exceptions.Timeout`

**Solution**: Increase timeout and add retries:

```python
def query_with_timeout(url, timeout=30, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            return response.json()
        except requests.Timeout:
            if attempt < retries - 1:
                time.sleep(5)
                continue
            raise
```

### Issue 3: Version Mismatches

Different databases use different genome builds (GRCh37/hg19 vs GRCh38/hg38).

**Solution**: Liftover coordinates when needed:

```python
from pyliftover import LiftOver

def liftover_variant(chromosome, position, build_from="hg19", build_to="hg38"):
    """Convert coordinates between genome builds."""
    lo = LiftOver(build_from, build_to)
    result = lo.convert_coordinate(chromosome, position)

    if result:
        return result[0]  # (new_chrom, new_pos, strand)
    return None
```

## Performance Tips

### 1. Parallel Queries

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_annotate(variants, client, max_workers=10):
    """Annotate variants in parallel."""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(client.query, variant)
            for variant in variants
        ]
        results = [future.result() for future in futures]
    return results
```

### 2. Use GraphQL for Batch Queries

gnomAD and some other databases support GraphQL:

```python
import requests

query = """
{
  variant(variantId: "17-41245466-G-A", dataset: gnomad_r3) {
    pos
    ref
    alt
    genome {
      ac
      an
      af
    }
  }
}
"""

response = requests.post(
    "https://gnomad.broadinstitute.org/api",
    json={"query": query},
)
```

### 3. Cache Aggressively

```python
# Cache for 30 days
from datetime import datetime, timedelta

class TimedCache(DatabaseCache):
    def is_expired(self, cache_file, max_age_days=30):
        if not cache_file.exists():
            return True
        age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        return age > timedelta(days=max_age_days)

    def get(self, query):
        key = self._cache_key(query)
        cache_file = self.cache_dir / f"{key}.json"

        if self.is_expired(cache_file):
            return None

        return super().get(query)
```

## References

- [Ensembl REST API](https://rest.ensembl.org/)
- [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar/)
- [gnomAD](https://gnomad.broadinstitute.org/)
- [dbSNP](https://www.ncbi.nlm.nih.gov/snp/)
- [Variant Effect Predictor (VEP)](https://www.ensembl.org/info/docs/tools/vep/index.html)

## License

Apache-2.0
