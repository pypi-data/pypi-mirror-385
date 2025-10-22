"""Reproducibility caching for Vigil pipelines."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import yaml


class CacheEntry:
    """Represents a cached pipeline execution."""

    def __init__(self, cache_id: str, inputs_hash: str, outputs: List[Dict[str, Any]],
                 receipt_id: str, created_at: datetime, metadata: Dict[str, Any]):
        self.cache_id = cache_id
        self.inputs_hash = inputs_hash
        self.outputs = outputs
        self.receipt_id = receipt_id
        self.created_at = created_at
        self.metadata = metadata


class ReproducibilityCache:
    """Local cache for reproducible pipeline executions."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize reproducibility cache.

        Args:
            cache_dir: Directory for cache storage
        """
        self.cache_dir = cache_dir or Path(".vigil/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load cache metadata."""
        if self.metadata_file.exists():
            with self.metadata_file.open("r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"entries": {}, "stats": {"hits": 0, "misses": 0}}

    def _save_metadata(self) -> None:
        """Save cache metadata."""
        with self.metadata_file.open("w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2, default=str)

    def _compute_inputs_hash(self, inputs: List[Dict[str, Any]],
                           environment: Dict[str, Any]) -> str:
        """Compute deterministic hash of inputs and environment."""
        # Normalize inputs for consistent hashing
        normalized_inputs = []
        for inp in inputs:
            normalized = {
                "uri": inp.get("uri", ""),
                "checksum": inp.get("checksum", ""),
                "size_bytes": inp.get("size_bytes", 0)
            }
            normalized_inputs.append(normalized)

        # Normalize environment
        normalized_env = {
            "python_version": environment.get("python", {}).get("version", ""),
            "system": environment.get("system", {}).get("system", ""),
            "docker_image": environment.get("docker", {}).get("image", ""),
            "git_ref": environment.get("git", {}).get("ref", "")
        }

        # Create deterministic hash
        cache_key = {
            "inputs": sorted(normalized_inputs, key=lambda x: x["uri"]),
            "environment": normalized_env
        }

        cache_json = json.dumps(cache_key, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(cache_json.encode("utf-8")).hexdigest()

    def get_cache_entry(self, inputs: List[Dict[str, Any]],
                       environment: Dict[str, Any]) -> Optional[CacheEntry]:
        """Get cached entry for given inputs and environment.

        Args:
            inputs: Pipeline inputs
            environment: Environment metadata

        Returns:
            Cache entry if found, None otherwise
        """
        inputs_hash = self._compute_inputs_hash(inputs, environment)

        if inputs_hash in self.metadata["entries"]:
            entry_data = self.metadata["entries"][inputs_hash]
            self.metadata["stats"]["hits"] += 1
            self._save_metadata()

            return CacheEntry(
                cache_id=entry_data["cache_id"],
                inputs_hash=inputs_hash,
                outputs=entry_data["outputs"],
                receipt_id=entry_data["receipt_id"],
                created_at=datetime.fromisoformat(entry_data["created_at"]),
                metadata=entry_data["metadata"]
            )

        self.metadata["stats"]["misses"] += 1
        self._save_metadata()
        return None

    def store_cache_entry(self, inputs: List[Dict[str, Any]],
                         environment: Dict[str, Any], outputs: List[Dict[str, Any]],
                         receipt_id: str, metadata: Dict[str, Any]) -> str:
        """Store cache entry for pipeline execution.

        Args:
            inputs: Pipeline inputs
            environment: Environment metadata
            outputs: Pipeline outputs
            receipt_id: Receipt ID
            metadata: Additional metadata

        Returns:
            Cache ID
        """
        inputs_hash = self._compute_inputs_hash(inputs, environment)
        cache_id = str(uuid4())

        # Store outputs in cache directory
        outputs_dir = self.cache_dir / cache_id
        outputs_dir.mkdir(exist_ok=True)

        for output in outputs:
            if "uri" in output and "checksum" in output:
                # Create symbolic link or copy file
                source_path = Path(output["uri"])
                if source_path.exists():
                    cache_path = outputs_dir / source_path.name
                    if not cache_path.exists():
                        if source_path.is_file():
                            shutil.copy2(source_path, cache_path)
                        else:
                            shutil.copytree(source_path, cache_path)

        # Store metadata
        entry_data = {
            "cache_id": cache_id,
            "inputs_hash": inputs_hash,
            "outputs": outputs,
            "receipt_id": receipt_id,
            "created_at": datetime.now(UTC).isoformat(),
            "metadata": metadata
        }

        self.metadata["entries"][inputs_hash] = entry_data
        self._save_metadata()

        return cache_id

    def restore_from_cache(self, cache_entry: CacheEntry, output_dir: Path) -> None:
        """Restore outputs from cache entry.

        Args:
            cache_entry: Cache entry to restore
            output_dir: Directory to restore outputs to
        """
        cache_dir = self.cache_dir / cache_entry.cache_id

        if not cache_dir.exists():
            raise FileNotFoundError(f"Cache directory not found: {cache_dir}")

        # Restore outputs
        for output in cache_entry.outputs:
            if "uri" in output:
                source_path = cache_dir / Path(output["uri"]).name
                if source_path.exists():
                    target_path = output_dir / source_path.name
                    if source_path.is_file():
                        shutil.copy2(source_path, target_path)
                    else:
                        shutil.copytree(source_path, target_path)

    def list_cache_entries(self, limit: int = 100) -> List[CacheEntry]:
        """List cache entries.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of cache entries
        """
        entries = []
        for entry_data in list(self.metadata["entries"].values())[:limit]:
            entry = CacheEntry(
                cache_id=entry_data["cache_id"],
                inputs_hash=entry_data["inputs_hash"],
                outputs=entry_data["outputs"],
                receipt_id=entry_data["receipt_id"],
                created_at=datetime.fromisoformat(entry_data["created_at"]),
                metadata=entry_data["metadata"]
            )
            entries.append(entry)

        return entries

    def clear_cache(self, older_than_days: Optional[int] = None) -> int:
        """Clear cache entries.

        Args:
            older_than_days: Clear entries older than this many days

        Returns:
            Number of entries cleared
        """
        if older_than_days is None:
            # Clear all entries
            cleared_count = len(self.metadata["entries"])
            self.metadata["entries"] = {}
            self.metadata["stats"] = {"hits": 0, "misses": 0}
            self._save_metadata()

            # Remove cache directories
            for entry in self.metadata["entries"].values():
                cache_dir = self.cache_dir / entry["cache_id"]
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)

            return cleared_count

        # Clear old entries
        cutoff_date = datetime.now(UTC).timestamp() - (older_than_days * 24 * 60 * 60)
        cleared_count = 0

        entries_to_remove = []
        for inputs_hash, entry_data in self.metadata["entries"].items():
            entry_date = datetime.fromisoformat(entry_data["created_at"]).timestamp()
            if entry_date < cutoff_date:
                entries_to_remove.append(inputs_hash)
                cache_dir = self.cache_dir / entry_data["cache_id"]
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
                cleared_count += 1

        for inputs_hash in entries_to_remove:
            del self.metadata["entries"][inputs_hash]

        self._save_metadata()
        return cleared_count

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics
        """
        stats = self.metadata["stats"].copy()
        stats["total_entries"] = len(self.metadata["entries"])
        stats["cache_size_mb"] = self._get_cache_size_mb()
        return stats

    def _get_cache_size_mb(self) -> float:
        """Get cache size in MB."""
        total_size = 0
        for item in self.cache_dir.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size / (1024 * 1024)


def cli() -> None:
    """CLI entry point for cache management."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage Vigil reproducibility cache")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List cache entries")
    list_parser.add_argument("--limit", type=int, default=100, help="Maximum entries to show")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show cache statistics")

    # Clear command
    clear_parser = subparsers.add_parser("clear", help="Clear cache entries")
    clear_parser.add_argument("--older-than", type=int, help="Clear entries older than N days")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cache = ReproducibilityCache()

    if args.command == "list":
        entries = cache.list_cache_entries(args.limit)
        print(f"Cache entries ({len(entries)}):")
        for entry in entries:
            print(f"  {entry.cache_id}: {entry.receipt_id}")
            print(f"    Created: {entry.created_at}")
            print(f"    Outputs: {len(entry.outputs)}")
            print()

    elif args.command == "stats":
        stats = cache.get_cache_stats()
        print("Cache Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Cache hits: {stats['hits']}")
        print(f"  Cache misses: {stats['misses']}")
        print(f"  Hit rate: {stats['hits'] / (stats['hits'] + stats['misses']) * 100:.1f}%")
        print(f"  Cache size: {stats['cache_size_mb']:.1f} MB")

    elif args.command == "clear":
        cleared = cache.clear_cache(args.older_than)
        print(f"Cleared {cleared} cache entries")


if __name__ == "__main__":
    cli()
