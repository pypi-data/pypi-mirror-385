"""Cryptographic signing core API."""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class Signer:
    """Cryptographic signer for receipts and artifacts."""

    def __init__(self, private_key: ed25519.Ed25519PrivateKey | None = None):
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("cryptography library is required for signing")

        if private_key is None:
            private_key = ed25519.Ed25519PrivateKey.generate()

        self.private_key = private_key
        self.public_key = private_key.public_key()

    @classmethod
    def from_file(cls, key_path: Path | str) -> Signer:
        """Load signer from private key file."""
        if not CRYPTOGRAPHY_AVAILABLE:
            raise ImportError("cryptography library is required for signing")

        key_path = Path(key_path)
        if not key_path.exists():
            raise FileNotFoundError(f"Private key file not found: {key_path}")

        key_data = key_path.read_bytes()
        private_key = serialization.load_pem_private_key(
            key_data,
            password=None
        )

        if not isinstance(private_key, ed25519.Ed25519PrivateKey):
            raise ValueError("Key must be Ed25519 private key")

        return cls(private_key)

    def save_key(self, key_path: Path | str) -> None:
        """Save private key to file."""
        key_path = Path(key_path)
        key_path.parent.mkdir(parents=True, exist_ok=True)

        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        key_path.write_bytes(private_pem)

    def get_public_key_pem(self) -> str:
        """Get public key in PEM format."""
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_pem.decode("utf-8")

    def sign_data(self, data: bytes) -> str:
        """Sign data and return base64-encoded signature."""
        signature = self.private_key.sign(data)
        return base64.b64encode(signature).decode("utf-8")

    def sign_receipt(self, receipt: dict[str, Any]) -> str:
        """Sign a receipt and return the signature."""
        # Create canonical JSON representation
        canonical_json = json.dumps(receipt, sort_keys=True, separators=(',', ':'))
        return self.sign_data(canonical_json.encode("utf-8"))

    def sign_file(self, file_path: Path | str) -> str:
        """Sign a file and return the signature."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_data = file_path.read_bytes()
        return self.sign_data(file_data)


def verify_signature(
    data: bytes,
    signature: str,
    public_key_pem: str
) -> bool:
    """Verify a signature against data and public key."""
    if not CRYPTOGRAPHY_AVAILABLE:
        raise ImportError("cryptography library is required for signature verification")

    try:
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode("utf-8")
        )

        if not isinstance(public_key, ed25519.Ed25519PublicKey):
            return False

        # Decode signature
        signature_bytes = base64.b64decode(signature)

        # Verify signature
        public_key.verify(signature_bytes, data)
        return True

    except Exception:
        return False


def verify_receipt_signature(
    receipt: dict[str, Any],
    signature: str,
    public_key_pem: str
) -> bool:
    """Verify a receipt signature."""
    canonical_json = json.dumps(receipt, sort_keys=True, separators=(',', ':'))
    return verify_signature(
        canonical_json.encode("utf-8"),
        signature,
        public_key_pem
    )


def verify_file_signature(
    file_path: Path | str,
    signature: str,
    public_key_pem: str
) -> bool:
    """Verify a file signature."""
    file_path = Path(file_path)
    if not file_path.exists():
        return False

    file_data = file_path.read_bytes()
    return verify_signature(file_data, signature, public_key_pem)
