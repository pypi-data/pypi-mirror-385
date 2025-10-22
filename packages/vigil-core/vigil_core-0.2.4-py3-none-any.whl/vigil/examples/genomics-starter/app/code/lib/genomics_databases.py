"""Genomics database connection patterns and utilities.

This module demonstrates how to connect to common genomics annotation
databases for variant annotation workflows.

Supported databases:
- Ensembl: Gene annotation and transcript information
- dbSNP: Known variant IDs and population frequencies
- ClinVar: Clinical significance of variants
- gnomAD: Population allele frequencies

All database access includes caching for offline work.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd
import requests


class DatabaseCache:
    """Local cache for database queries to enable offline work."""

    def __init__(self, cache_dir: str | Path = "~/.vigil/annotation_cache"):
        """Initialize cache directory."""
        self.cache_dir = Path(cache_dir).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.md5(query.encode()).hexdigest()

    def get(self, query: str) -> dict[str, Any] | None:
        """Retrieve cached result."""
        key = self._cache_key(query)
        cache_file = self.cache_dir / f"{key}.json"

        if cache_file.exists():
            with cache_file.open("r") as f:
                return json.load(f)  # type: ignore[no-any-return]
        return None

    def set(self, query: str, result: dict[str, Any]) -> None:
        """Store result in cache."""
        key = self._cache_key(query)
        cache_file = self.cache_dir / f"{key}.json"

        with cache_file.open("w") as f:
            json.dump(result, f, indent=2)


class EnsemblClient:
    """Client for Ensembl REST API.

    Provides gene annotation, transcript information, and variant effects.

    Example:
        >>> client = EnsemblClient(cache_dir="~/.vigil/cache")
        >>> gene = client.get_gene_by_symbol("BRCA1", species="human")
        >>> print(gene["id"], gene["description"])
    """

    BASE_URL = "https://rest.ensembl.org"

    def __init__(self, cache_dir: str | Path = "~/.vigil/annotation_cache"):
        """Initialize Ensembl client with caching."""
        self.cache = DatabaseCache(cache_dir)
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _request(self, endpoint: str) -> dict[str, Any]:
        """Make API request with caching."""
        url = f"{self.BASE_URL}{endpoint}"

        # Check cache first
        cached = self.cache.get(url)
        if cached is not None:
            return cached

        # Make request
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        result: dict[str, Any] = response.json()

        # Cache result
        self.cache.set(url, result)

        return result

    def get_gene_by_symbol(self, symbol: str, species: str = "human") -> dict[str, Any]:
        """Get gene information by symbol.

        Args:
            symbol: Gene symbol (e.g., "BRCA1")
            species: Species name (default: "human")

        Returns:
            Gene information including ID, description, location
        """
        endpoint = f"/lookup/symbol/{species}/{symbol}?expand=1"
        return self._request(endpoint)

    def get_variant_consequences(
        self, chromosome: str, position: int, alleles: str, species: str = "human"
    ) -> dict[str, Any]:
        """Get variant consequences and predicted effects.

        Args:
            chromosome: Chromosome name (e.g., "17")
            position: Genomic position
            alleles: Ref/alt alleles (e.g., "G/A")
            species: Species name (default: "human")

        Returns:
            Variant consequences including transcript effects, SIFT, PolyPhen
        """
        endpoint = f"/vep/{species}/region/{chromosome}:{position}:{position}/{alleles}?"
        return self._request(endpoint)


class ClinVarClient:
    """Client for ClinVar database.

    Provides clinical significance of genetic variants.

    Example:
        >>> client = ClinVarClient(cache_dir="~/.vigil/cache")
        >>> result = client.search_variant("17", 41245466, "G", "A")
        >>> print(result["clinical_significance"])
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self, cache_dir: str | Path = "~/.vigil/annotation_cache", email: str | None = None):
        """Initialize ClinVar client.

        Args:
            cache_dir: Directory for caching results
            email: Email for NCBI API (recommended for higher rate limits)
        """
        self.cache = DatabaseCache(cache_dir)
        self.session = requests.Session()
        self.email = email

    def search_variant(
        self, chromosome: str, position: int, ref: str, alt: str
    ) -> dict[str, Any]:
        """Search for variant in ClinVar.

        Args:
            chromosome: Chromosome (e.g., "17")
            position: Position
            ref: Reference allele
            alt: Alternate allele

        Returns:
            Clinical significance and review status
        """
        # Build query
        query = f"chr{chromosome}:{position}[chrpos] AND {ref}>{alt}[variant]"
        cache_key = f"clinvar_{chromosome}_{position}_{ref}_{alt}"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        # Search ClinVar (simplified - real implementation would use E-utilities)
        # This is a placeholder showing the pattern
        result: dict[str, Any] = {
            "chromosome": chromosome,
            "position": position,
            "ref": ref,
            "alt": alt,
            "clinical_significance": "Uncertain significance",
            "review_status": "no assertion criteria provided",
            "note": "Placeholder result - integrate with real ClinVar API",
        }

        # Cache result
        self.cache.set(cache_key, result)

        return result


class GnomADClient:
    """Client for gnomAD (Genome Aggregation Database).

    Provides population allele frequencies.

    Example:
        >>> client = GnomADClient(cache_dir="~/.vigil/cache")
        >>> freq = client.get_allele_frequency("17", 41245466, "G", "A")
        >>> print(f"gnomAD AF: {freq['allele_freq']}")
    """

    def __init__(self, cache_dir: str | Path = "~/.vigil/annotation_cache"):
        """Initialize gnomAD client with caching."""
        self.cache = DatabaseCache(cache_dir)

    def get_allele_frequency(
        self, chromosome: str, position: int, ref: str, alt: str
    ) -> dict[str, Any]:
        """Get population allele frequency.

        Args:
            chromosome: Chromosome (e.g., "17")
            position: Position
            ref: Reference allele
            alt: Alternate allele

        Returns:
            Allele frequencies by population
        """
        cache_key = f"gnomad_{chromosome}_{position}_{ref}_{alt}"

        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        # Query gnomAD (placeholder - real implementation would use GraphQL API)
        result: dict[str, Any] = {
            "chromosome": chromosome,
            "position": position,
            "ref": ref,
            "alt": alt,
            "allele_freq": 0.0001,
            "allele_count": 12,
            "allele_number": 120000,
            "homozygote_count": 0,
            "note": "Placeholder result - integrate with real gnomAD API",
        }

        # Cache result
        self.cache.set(cache_key, result)

        return result


def annotate_variants_with_databases(
    variants: pd.DataFrame,
    use_ensembl: bool = True,
    use_clinvar: bool = True,
    use_gnomad: bool = True,
    cache_dir: str | Path = "~/.vigil/annotation_cache",
) -> pd.DataFrame:
    """Annotate variants with multiple databases.

    Args:
        variants: DataFrame with columns: chromosome, position, ref_allele, alt_allele
        use_ensembl: Query Ensembl for gene info
        use_clinvar: Query ClinVar for clinical significance
        use_gnomad: Query gnomAD for population frequencies
        cache_dir: Cache directory for offline work

    Returns:
        Annotated DataFrame with additional columns
    """
    result = variants.copy()

    # Initialize clients
    if use_ensembl:
        ensembl = EnsemblClient(cache_dir)

    if use_clinvar:
        clinvar = ClinVarClient(cache_dir)

    if use_gnomad:
        gnomad = GnomADClient(cache_dir)

    # Annotate each variant
    annotations = []

    for _, variant in variants.iterrows():
        annotation: dict[str, Any] = {}

        # ClinVar annotation
        if use_clinvar:
            clinvar_result = clinvar.search_variant(
                variant["chromosome"],
                variant["position"],
                variant["ref_allele"],
                variant["alt_allele"],
            )
            annotation["clinvar_significance"] = clinvar_result.get(
                "clinical_significance", "Unknown"
            )

        # gnomAD annotation
        if use_gnomad:
            gnomad_result = gnomad.get_allele_frequency(
                variant["chromosome"],
                variant["position"],
                variant["ref_allele"],
                variant["alt_allele"],
            )
            annotation["gnomad_af"] = gnomad_result.get("allele_freq", 0.0)
            annotation["gnomad_ac"] = gnomad_result.get("allele_count", 0)

        annotations.append(annotation)

    # Add annotations to DataFrame
    annotations_df = pd.DataFrame(annotations)
    result = pd.concat([result, annotations_df], axis=1)

    return result


# Example usage
if __name__ == "__main__":
    # Example 1: Query Ensembl
    print("Example 1: Ensembl gene lookup")
    ensembl = EnsemblClient()
    gene = ensembl.get_gene_by_symbol("BRCA1")
    print(f"Gene: {gene.get('id')}, Description: {gene.get('description', '')[:50]}...")

    # Example 2: Annotate variants
    print("\nExample 2: Annotate variants")
    variants = pd.DataFrame(
        {
            "chromosome": ["chr17", "chr17"],
            "position": [41245466, 41246481],
            "ref_allele": ["G", "C"],
            "alt_allele": ["A", "T"],
            "gene": ["BRCA1", "BRCA1"],
        }
    )

    annotated = annotate_variants_with_databases(
        variants, use_ensembl=False, use_clinvar=True, use_gnomad=True
    )

    print(annotated)
