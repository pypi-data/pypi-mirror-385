"""Tests for cryptographic signing and verification."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    from vigil.tools import signing

    SIGNING_AVAILABLE = True
except ImportError:
    SIGNING_AVAILABLE = False


pytestmark = pytest.mark.skipif(not SIGNING_AVAILABLE, reason="cryptography not installed")


@pytest.fixture
def sample_attestation(tmp_path: Path) -> Path:
    """Create a sample attestation file for testing."""
    attestation_data = {
        "_type": "https://in-toto.io/Statement/v1",
        "subject": [{"name": "receipt.json", "digest": {"sha256": "abc123"}}],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {"buildDefinition": {}, "runDetails": {}},
    }
    attestation_path = tmp_path / "attestation.json"
    attestation_path.write_text(json.dumps(attestation_data, indent=2), encoding="utf-8")
    return attestation_path


@pytest.fixture
def keypair(tmp_path: Path) -> tuple[Path, Path]:
    """Generate a test keypair."""
    private_key_path = tmp_path / "private.pem"
    public_key_path = tmp_path / "public.pem"
    signing.generate_keypair(private_key_path, public_key_path)
    return private_key_path, public_key_path


def test_generate_keypair(tmp_path: Path) -> None:
    """Test Ed25519 keypair generation."""
    private_key_path = tmp_path / "private.pem"
    public_key_path = tmp_path / "public.pem"

    signing.generate_keypair(private_key_path, public_key_path)

    # Verify files exist
    assert private_key_path.exists()
    assert public_key_path.exists()

    # Verify private key permissions
    assert oct(private_key_path.stat().st_mode)[-3:] == "600"

    # Verify PEM format
    private_pem = private_key_path.read_text()
    assert "-----BEGIN PRIVATE KEY-----" in private_pem
    assert "-----END PRIVATE KEY-----" in private_pem

    public_pem = public_key_path.read_text()
    assert "-----BEGIN PUBLIC KEY-----" in public_pem
    assert "-----END PUBLIC KEY-----" in public_pem


def test_sign_attestation(sample_attestation: Path, keypair: tuple[Path, Path]) -> None:
    """Test attestation signing."""
    private_key_path, public_key_path = keypair

    signature_envelope = signing.sign_attestation(
        attestation_path=sample_attestation,
        private_key_path=private_key_path,
    )

    # Verify signature envelope structure
    assert signature_envelope["algorithm"] == "Ed25519"
    assert "-----BEGIN PUBLIC KEY-----" in signature_envelope["publicKey"]
    assert len(signature_envelope["signature"]) > 0

    # Verify signature file was created
    signature_path = sample_attestation.with_suffix(sample_attestation.suffix + ".sig")
    assert signature_path.exists()

    # Verify signature file content
    loaded_envelope = json.loads(signature_path.read_text())
    assert loaded_envelope == signature_envelope


def test_verify_signature_valid(sample_attestation: Path, keypair: tuple[Path, Path]) -> None:
    """Test signature verification with valid signature."""
    private_key_path, public_key_path = keypair

    # Sign attestation
    signing.sign_attestation(
        attestation_path=sample_attestation,
        private_key_path=private_key_path,
    )

    # Verify signature
    is_valid = signing.verify_signature(sample_attestation)
    assert is_valid


def test_verify_signature_with_explicit_public_key(
    sample_attestation: Path, keypair: tuple[Path, Path]
) -> None:
    """Test signature verification with explicit public key."""
    private_key_path, public_key_path = keypair

    # Sign attestation
    signing.sign_attestation(
        attestation_path=sample_attestation,
        private_key_path=private_key_path,
    )

    # Verify with explicit public key
    is_valid = signing.verify_signature(sample_attestation, public_key_path=public_key_path)
    assert is_valid


def test_verify_signature_invalid(sample_attestation: Path, keypair: tuple[Path, Path]) -> None:
    """Test signature verification with tampered content."""
    private_key_path, public_key_path = keypair

    # Sign attestation
    signing.sign_attestation(
        attestation_path=sample_attestation,
        private_key_path=private_key_path,
    )

    # Tamper with attestation
    tampered_data = json.loads(sample_attestation.read_text())
    tampered_data["subject"][0]["digest"]["sha256"] = "tampered"
    sample_attestation.write_text(json.dumps(tampered_data, indent=2))

    # Verify signature fails
    is_valid = signing.verify_signature(sample_attestation)
    assert not is_valid


def test_sign_with_env_var(
    sample_attestation: Path, keypair: tuple[Path, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test signing with VIGIL_SIGNING_KEY environment variable."""
    private_key_path, public_key_path = keypair

    # Set environment variable
    monkeypatch.setenv("VIGIL_SIGNING_KEY", str(private_key_path))

    # Sign without explicit key path
    signature_envelope = signing.sign_attestation(attestation_path=sample_attestation)

    # Verify signature was created
    assert signature_envelope["algorithm"] == "Ed25519"


def test_sign_without_key_raises_error(sample_attestation: Path) -> None:
    """Test that signing without a key raises an error."""
    with pytest.raises(ValueError, match="No signing key specified"):
        signing.sign_attestation(attestation_path=sample_attestation)


def test_verify_missing_signature_raises_error(sample_attestation: Path) -> None:
    """Test that verifying without a signature file raises an error."""
    with pytest.raises(FileNotFoundError, match="Signature file not found"):
        signing.verify_signature(sample_attestation)
