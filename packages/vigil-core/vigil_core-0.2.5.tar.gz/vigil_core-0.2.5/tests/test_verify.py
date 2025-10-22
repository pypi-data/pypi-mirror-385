"""Tests for receipt and attestation verification."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from vigil.tools import verify


@pytest.fixture
def sample_receipt_with_outputs(tmp_path: Path) -> Path:
    """Create a sample receipt with output files."""
    # Create output files
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()

    output1 = artifacts_dir / "output1.txt"
    output1.write_text("hello", encoding="utf-8")

    output2 = artifacts_dir / "output2.txt"
    output2.write_text("world", encoding="utf-8")

    # Compute checksums
    checksum1 = verify.compute_sha256(output1)
    checksum2 = verify.compute_sha256(output2)

    # Create receipt
    receipt_data = {
        "issuer": "Vigil",
        "runletId": "rl_1234567890",
        "vigilUrl": "vigil://example/test@main",
        "gitRef": "abc123",
        "outputs": [
            {"uri": str(output1), "checksum": checksum1},
            {"uri": str(output2), "checksum": checksum2},
        ],
    }

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    receipt_path = receipts_dir / "receipt_test.json"
    receipt_path.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")

    return receipt_path


@pytest.fixture
def sample_attestation(tmp_path: Path) -> Path:
    """Create a sample attestation file."""
    attestation_data = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "receipt.json", "digest": {"sha256": "abc123"}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://vigil.science/build/v1",
                "externalParameters": {},
                "internalParameters": {},
                "resolvedDependencies": [],
            },
            "runDetails": {
                "builder": {"id": "https://vigil.science/builder/v1"},
                "metadata": {
                    "invocationId": "rl_123",
                    "startedOn": "2025-01-20T12:00:00Z",
                    "finishedOn": "2025-01-20T12:05:00Z",
                },
                "byproducts": [],
            },
        },
    }
    attestation_path = tmp_path / "attestation.json"
    attestation_path.write_text(json.dumps(attestation_data, indent=2), encoding="utf-8")
    return attestation_path


def test_compute_sha256(tmp_path: Path) -> None:
    """Test SHA256 computation with prefix."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world", encoding="utf-8")

    checksum = verify.compute_sha256(test_file)

    # Verify format
    assert checksum.startswith("sha256:")
    assert len(checksum) == 71  # "sha256:" + 64 hex chars


def test_verify_receipt_valid(sample_receipt_with_outputs: Path) -> None:
    """Test verification of a valid receipt."""
    is_valid = verify.verify_receipt(sample_receipt_with_outputs, verbose=False)
    assert is_valid


def test_verify_receipt_missing_file() -> None:
    """Test verification fails for missing receipt file."""
    is_valid = verify.verify_receipt(Path("/nonexistent/receipt.json"), verbose=False)
    assert not is_valid


def test_verify_receipt_invalid_json(tmp_path: Path) -> None:
    """Test verification fails for invalid JSON."""
    receipt_path = tmp_path / "invalid.json"
    receipt_path.write_text("not valid json{", encoding="utf-8")

    is_valid = verify.verify_receipt(receipt_path, verbose=False)
    assert not is_valid


def test_verify_receipt_missing_fields(tmp_path: Path) -> None:
    """Test verification fails when required fields are missing."""
    receipt_data = {"issuer": "Vigil"}  # Missing other required fields
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(receipt_data), encoding="utf-8")

    is_valid = verify.verify_receipt(receipt_path, verbose=False)
    assert not is_valid


def test_verify_receipt_checksum_mismatch(tmp_path: Path) -> None:
    """Test verification fails when output checksum doesn't match."""
    # Create output file
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    output = artifacts_dir / "output.txt"
    output.write_text("hello", encoding="utf-8")

    # Create receipt with wrong checksum
    receipt_data = {
        "issuer": "Vigil",
        "runletId": "rl_123",
        "vigilUrl": "vigil://example/test",
        "gitRef": "abc",
        "outputs": [{"uri": str(output), "checksum": "sha256:wrong"}],
    }

    receipts_dir = tmp_path / "receipts"
    receipts_dir.mkdir()
    receipt_path = receipts_dir / "receipt.json"
    receipt_path.write_text(json.dumps(receipt_data, indent=2), encoding="utf-8")

    is_valid = verify.verify_receipt(receipt_path, verbose=False)
    assert not is_valid


def test_verify_attestation_valid(sample_attestation: Path) -> None:
    """Test verification of a valid attestation."""
    is_valid = verify.verify_attestation(sample_attestation, verbose=False)
    assert is_valid


def test_verify_attestation_invalid_type(tmp_path: Path) -> None:
    """Test verification fails for invalid in-toto type."""
    attestation_data = {
        "_type": "invalid-type",
        "subject": [],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {},
    }
    attestation_path = tmp_path / "attestation.json"
    attestation_path.write_text(json.dumps(attestation_data), encoding="utf-8")

    is_valid = verify.verify_attestation(attestation_path, verbose=False)
    assert not is_valid


def test_verify_attestation_invalid_predicate_type(tmp_path: Path) -> None:
    """Test verification fails for invalid predicate type."""
    attestation_data = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [],
        "predicateType": "invalid-predicate",
        "predicate": {},
    }
    attestation_path = tmp_path / "attestation.json"
    attestation_path.write_text(json.dumps(attestation_data), encoding="utf-8")

    is_valid = verify.verify_attestation(attestation_path, verbose=False)
    assert not is_valid


def test_verify_attestation_missing_subject(tmp_path: Path) -> None:
    """Test verification fails when subject is missing."""
    attestation_data = {
        "_type": "https://in-toto.io/Statement/v1",
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {},
    }
    attestation_path = tmp_path / "attestation.json"
    attestation_path.write_text(json.dumps(attestation_data), encoding="utf-8")

    is_valid = verify.verify_attestation(attestation_path, verbose=False)
    assert not is_valid


def test_verify_attestation_missing_build_definition(tmp_path: Path) -> None:
    """Test verification fails when buildDefinition is missing."""
    attestation_data = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "test", "digest": {"sha256": "abc"}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {"runDetails": {}},
    }
    attestation_path = tmp_path / "attestation.json"
    attestation_path.write_text(json.dumps(attestation_data), encoding="utf-8")

    is_valid = verify.verify_attestation(attestation_path, verbose=False)
    assert not is_valid


def test_verify_receipt_with_attestation(sample_receipt_with_outputs: Path, tmp_path: Path) -> None:
    """Test verification of receipt with associated attestation."""
    # Create matching attestation
    attestation_data = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "receipt_test.json", "digest": {"sha256": "abc123"}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType": "https://vigil.science/build/v1",
                "externalParameters": {},
                "internalParameters": {},
                "resolvedDependencies": [],
            },
            "runDetails": {
                "builder": {"id": "https://vigil.science/builder/v1"},
                "metadata": {
                    "invocationId": "rl_123",
                    "startedOn": "2025-01-20T12:00:00Z",
                    "finishedOn": "2025-01-20T12:05:00Z",
                },
                "byproducts": [],
            },
        },
    }

    receipts_dir = sample_receipt_with_outputs.parent
    attestation_path = receipts_dir / "attestation_test.json"
    attestation_path.write_text(json.dumps(attestation_data, indent=2), encoding="utf-8")

    is_valid = verify.verify_receipt_with_attestation(sample_receipt_with_outputs, verbose=False)
    assert is_valid


def test_verify_receipt_without_attestation(sample_receipt_with_outputs: Path) -> None:
    """Test verification of receipt without attestation (should succeed)."""
    is_valid = verify.verify_receipt_with_attestation(sample_receipt_with_outputs, verbose=False)
    assert is_valid
