"""Verification utilities for receipts and attestations."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from vigil.tools import signing


def compute_sha256(path: Path) -> str:
    """Compute SHA256 hash of a file with sha256: prefix."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def verify_receipt(receipt_path: Path, verbose: bool = False) -> bool:
    """
    Verify a receipt's integrity.

    Args:
        receipt_path: Path to receipt JSON file
        verbose: Print detailed verification information

    Returns:
        True if receipt is valid, False otherwise
    """
    if not receipt_path.exists():
        print(f"Error: Receipt not found: {receipt_path}", file=sys.stderr)
        return False

    try:
        receipt: dict[str, Any] = json.loads(receipt_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in receipt: {e}", file=sys.stderr)
        return False

    # Verify required fields
    required_fields = ["issuer", "runletId", "vigilUrl", "gitRef", "outputs"]
    missing_fields = [field for field in required_fields if field not in receipt]
    if missing_fields:
        print(f"Error: Missing required fields: {', '.join(missing_fields)}", file=sys.stderr)
        return False

    # Verify output checksums
    all_valid = True

    for output in receipt.get("outputs", []):
        uri = output.get("uri")
        expected_checksum = output.get("checksum")

        if not uri or not expected_checksum:
            print(f"Warning: Output missing uri or checksum: {output}", file=sys.stderr)
            continue

        # Try to resolve the output path
        output_path = Path(uri)
        if not output_path.is_absolute():
            # First try relative to current working directory (project root)
            if not output_path.exists():
                # Fall back to relative to receipt's parent directory
                base_dir = receipt_path.parent
                output_path = base_dir / uri

        if not output_path.exists():
            print(f"Error: Output file not found: {uri}", file=sys.stderr)
            all_valid = False
            continue

        # Compute actual checksum
        actual_checksum = compute_sha256(output_path)

        # Compare checksums
        if actual_checksum != expected_checksum:
            print(
                f"Error: Checksum mismatch for {uri}\n"
                f"  Expected: {expected_checksum}\n"
                f"  Actual:   {actual_checksum}",
                file=sys.stderr,
            )
            all_valid = False
        elif verbose:
            print(f"✓ {uri}: checksum valid")

    return all_valid


def verify_attestation(
    attestation_path: Path, signature_path: Path | None = None, verbose: bool = False
) -> bool:
    """
    Verify an attestation's structure and signature (if present).

    Args:
        attestation_path: Path to attestation JSON file
        signature_path: Path to signature file (optional, defaults to attestation_path.sig)
        verbose: Print detailed verification information

    Returns:
        True if attestation is valid, False otherwise
    """
    if not attestation_path.exists():
        print(f"Error: Attestation not found: {attestation_path}", file=sys.stderr)
        return False

    try:
        attestation: dict[str, Any] = json.loads(attestation_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in attestation: {e}", file=sys.stderr)
        return False

    # Verify in-toto statement structure
    if attestation.get("_type") != "https://in-toto.io/Statement/v1":
        print("Error: Invalid in-toto statement type", file=sys.stderr)
        return False

    if attestation.get("predicateType") != "https://slsa.dev/provenance/v1":
        print("Error: Invalid SLSA provenance type", file=sys.stderr)
        return False

    # Verify required fields
    if "subject" not in attestation or not isinstance(attestation["subject"], list):
        print("Error: Missing or invalid subject field", file=sys.stderr)
        return False

    if "predicate" not in attestation:
        print("Error: Missing predicate field", file=sys.stderr)
        return False

    predicate = attestation["predicate"]
    if "buildDefinition" not in predicate:
        print("Error: Missing buildDefinition in predicate", file=sys.stderr)
        return False

    if "runDetails" not in predicate:
        print("Error: Missing runDetails in predicate", file=sys.stderr)
        return False

    if verbose:
        print("✓ Attestation structure is valid")
        print(f"  Subject: {attestation['subject'][0].get('name', 'unknown')}")
        build_def = predicate.get("buildDefinition", {})
        print(f"  Build type: {build_def.get('buildType', 'unknown')}")
        run_details = predicate.get("runDetails", {})
        metadata = run_details.get("metadata", {})
        print(f"  Invocation ID: {metadata.get('invocationId', 'unknown')}")

    # Verify signature if present
    if signature_path is None:
        signature_path = attestation_path.with_suffix(attestation_path.suffix + ".sig")

    if signature_path.exists():
        try:
            is_valid = signing.verify_signature(attestation_path, signature_path)
            if is_valid:
                if verbose:
                    print("✓ Signature is valid")
                return True
            else:
                print("Error: Invalid signature", file=sys.stderr)
                return False
        except ImportError:
            print("Warning: cryptography library not available, skipping signature verification")
            return True  # Structure is valid even if we can't verify signature
        except Exception as e:
            print(f"Error verifying signature: {e}", file=sys.stderr)
            return False
    elif verbose:
        print("  No signature file found (unsigned)")

    return True


def verify_receipt_with_attestation(receipt_path: Path, verbose: bool = False) -> bool:
    """
    Verify a receipt and its associated attestation (if present).

    Args:
        receipt_path: Path to receipt JSON file
        verbose: Print detailed verification information

    Returns:
        True if both receipt and attestation (if present) are valid, False otherwise
    """
    if verbose:
        print(f"Verifying receipt: {receipt_path}")

    # Verify receipt
    receipt_valid = verify_receipt(receipt_path, verbose=verbose)

    if not receipt_valid:
        return False

    # Look for associated attestation
    # Replace "receipt_" with "attestation_" in filename
    attestation_path = receipt_path.parent / receipt_path.name.replace("receipt_", "attestation_")

    if attestation_path.exists():
        if verbose:
            print(f"\nVerifying attestation: {attestation_path}")
        attestation_valid = verify_attestation(attestation_path, verbose=verbose)
        return attestation_valid
    elif verbose:
        print("  No associated attestation found")

    return True


def cli() -> None:
    """CLI entrypoint for verify command."""
    ap = argparse.ArgumentParser(description="Verify Vigil receipts and attestations")
    ap.add_argument("receipt", help="Path to receipt JSON file")
    ap.add_argument(
        "-v", "--verbose", action="store_true", help="Print detailed verification information"
    )
    ap.add_argument(
        "--attestation",
        dest="attestation",
        default=None,
        help="Path to attestation file (auto-detected if not specified)",
    )
    ap.add_argument(
        "--signature",
        dest="signature",
        default=None,
        help="Path to signature file (auto-detected if not specified)",
    )

    args = ap.parse_args()

    receipt_path = Path(args.receipt)

    if args.attestation:
        # Verify only attestation
        attestation_path = Path(args.attestation)
        signature_path = Path(args.signature) if args.signature else None
        valid = verify_attestation(attestation_path, signature_path, verbose=args.verbose)
    else:
        # Verify receipt and associated attestation
        valid = verify_receipt_with_attestation(receipt_path, verbose=args.verbose)

    if valid:
        if args.verbose:
            print("\n✅ Verification successful")
        sys.exit(0)
    else:
        if args.verbose:
            print("\n❌ Verification failed")
        sys.exit(1)


if __name__ == "__main__":
    cli()
