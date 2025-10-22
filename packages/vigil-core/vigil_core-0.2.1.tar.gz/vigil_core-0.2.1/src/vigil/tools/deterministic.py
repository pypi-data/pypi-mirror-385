"""Deterministic time and randomness control for Vigil."""

from __future__ import annotations

import os
import random
import time
from datetime import datetime, UTC
from typing import Any, Dict, Optional


class DeterministicContext:
    """Context manager for deterministic execution."""

    def __init__(self, seed: Optional[int] = None, fixed_time: Optional[datetime] = None):
        """Initialize deterministic context.

        Args:
            seed: Random seed for reproducibility
            fixed_time: Fixed timestamp for deterministic time
        """
        self.seed = seed
        self.fixed_time = fixed_time
        self.original_random_state = None
        self.original_time = None

    def __enter__(self) -> DeterministicContext:
        """Enter deterministic context."""
        # Set random seed
        if self.seed is not None:
            self.original_random_state = random.getstate()
            random.seed(self.seed)

        # Set fixed time
        if self.fixed_time is not None:
            self.original_time = time.time
            time.time = lambda: self.fixed_time.timestamp()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit deterministic context."""
        # Restore random state
        if self.original_random_state is not None:
            random.setstate(self.original_random_state)

        # Restore time function
        if self.original_time is not None:
            time.time = self.original_time


def set_deterministic_environment(seed: Optional[int] = None,
                                 fixed_time: Optional[datetime] = None) -> None:
    """Set deterministic environment variables.

    Args:
        seed: Random seed
        fixed_time: Fixed timestamp
    """
    if seed is not None:
        os.environ["PYTHONHASHSEED"] = str(seed)
        os.environ["VIGIL_DETERMINISTIC_SEED"] = str(seed)

    if fixed_time is not None:
        os.environ["VIGIL_DETERMINISTIC_TIME"] = fixed_time.isoformat()


def get_deterministic_seed() -> Optional[int]:
    """Get deterministic seed from environment.

    Returns:
        Seed value or None
    """
    seed_str = os.environ.get("VIGIL_DETERMINISTIC_SEED")
    if seed_str:
        try:
            return int(seed_str)
        except ValueError:
            pass
    return None


def get_deterministic_time() -> Optional[datetime]:
    """Get deterministic time from environment.

    Returns:
        Fixed timestamp or None
    """
    time_str = os.environ.get("VIGIL_DETERMINISTIC_TIME")
    if time_str:
        try:
            return datetime.fromisoformat(time_str)
        except ValueError:
            pass
    return None


def canonical_json_serialize(obj: Any) -> str:
    """Serialize object to canonical JSON format.

    Args:
        obj: Object to serialize

    Returns:
        Canonical JSON string
    """
    import json

    def canonicalize(obj: Any) -> Any:
        """Recursively canonicalize object."""
        if isinstance(obj, dict):
            # Sort keys for deterministic output
            return {k: canonicalize(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [canonicalize(item) for item in obj]
        elif isinstance(obj, float):
            # Normalize floats to avoid precision issues
            if obj == 0.0:
                return 0.0
            elif obj == float('inf'):
                return float('inf')
            elif obj == float('-inf'):
                return float('-inf')
            elif obj != obj:  # NaN check
                return float('nan')
            else:
                # Round to reasonable precision
                return round(obj, 10)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    canonical_obj = canonicalize(obj)
    return json.dumps(canonical_obj, separators=(',', ':'), ensure_ascii=True, sort_keys=True)


def compute_deterministic_hash(obj: Any, algorithm: str = "sha256") -> str:
    """Compute deterministic hash of object.

    Args:
        obj: Object to hash
        algorithm: Hash algorithm

    Returns:
        Hash string
    """
    import hashlib

    canonical_json = canonical_json_serialize(obj)
    hash_func = getattr(hashlib, algorithm)()
    hash_func.update(canonical_json.encode('utf-8'))
    return f"{algorithm}:{hash_func.hexdigest()}"


def cli() -> None:
    """CLI entry point for deterministic control."""
    import argparse

    parser = argparse.ArgumentParser(description="Control deterministic execution")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Set command
    set_parser = subparsers.add_parser("set", help="Set deterministic environment")
    set_parser.add_argument("--seed", type=int, help="Random seed")
    set_parser.add_argument("--time", help="Fixed timestamp (ISO format)")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get current deterministic settings")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test deterministic behavior")
    test_parser.add_argument("--iterations", type=int, default=5, help="Number of test iterations")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "set":
        fixed_time = None
        if args.time:
            try:
                fixed_time = datetime.fromisoformat(args.time)
            except ValueError:
                print(f"Invalid time format: {args.time}")
                return

        set_deterministic_environment(args.seed, fixed_time)

        if args.seed:
            print(f"Set deterministic seed: {args.seed}")
        if fixed_time:
            print(f"Set deterministic time: {fixed_time}")

    elif args.command == "get":
        seed = get_deterministic_seed()
        fixed_time = get_deterministic_time()

        print("Deterministic settings:")
        print(f"  Seed: {seed}")
        print(f"  Fixed time: {fixed_time}")

    elif args.command == "test":
        seed = get_deterministic_seed()
        fixed_time = get_deterministic_time()

        print(f"Testing deterministic behavior ({args.iterations} iterations):")

        # Test random number generation
        if seed is not None:
            print("Random numbers:")
            for i in range(args.iterations):
                with DeterministicContext(seed=seed):
                    numbers = [random.random() for _ in range(3)]
                    print(f"  Iteration {i+1}: {numbers}")

        # Test time generation
        if fixed_time is not None:
            print("Timestamps:")
            for i in range(args.iterations):
                with DeterministicContext(fixed_time=fixed_time):
                    timestamp = datetime.now(UTC)
                    print(f"  Iteration {i+1}: {timestamp}")


if __name__ == "__main__":
    cli()
