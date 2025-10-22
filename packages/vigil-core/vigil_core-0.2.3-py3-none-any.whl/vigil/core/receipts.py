"""Receipt generation and verification core API."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypedDict

import yaml


class Artifact(TypedDict):
    """Artifact metadata."""

    uri: str
    checksum: str
    kind: str


class ReceiptMetrics(TypedDict, total=False):
    """Receipt metrics structure."""

    n: int
    tp: int
    tn: int
    fp: int
    fn: int
    accuracy: float
    precision: float
    recall: float
    f1: float


def sha256(path: Path | str) -> str:
    """Return the Vigil-prefixed SHA256 digest for ``path``."""
    file_path = Path(path)
    with file_path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256")
    return f"vigil:sha256:{digest.hexdigest()}"


def get_git_user_info() -> tuple[str, str]:
    """Get git user name and email."""
    owner = "unknown"
    email = "unknown"

    try:
        result = subprocess.run(["git", "config", "user.name"], capture_output=True, text=True)
        if result.returncode == 0:
            owner = f"@{result.stdout.strip()}"
    except Exception:
        pass

    try:
        result = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
        if result.returncode == 0:
            email = result.stdout.strip()
    except Exception:
        pass

    return owner, email


def get_git_info() -> dict[str, Any]:
    """Get git repository information."""
    git_info: dict[str, Any] = {
        "repository": "unknown",
        "commit": "unknown",
        "branch": "unknown",
        "status": "unknown"
    }

    try:
        # Get repository URL
        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True)
        if result.returncode == 0:
            git_info["repository"] = result.stdout.strip()
    except Exception:
        pass

    try:
        # Get current commit
        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        if result.returncode == 0:
            git_info["commit"] = result.stdout.strip()
    except Exception:
        pass

    try:
        # Get current branch
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
        if result.returncode == 0:
            git_info["branch"] = result.stdout.strip()
    except Exception:
        pass

    try:
        # Get git status
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode == 0:
            git_info["status"] = "clean" if not result.stdout.strip() else "dirty"
    except Exception:
        pass

    return git_info


def get_environment_info() -> dict[str, Any]:
    """Get environment information."""
    return {
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        "platform": os.sys.platform,
        "hostname": os.uname().nodename if hasattr(os, "uname") else "unknown",
        "user": os.getenv("USER", "unknown"),
        "path": os.getenv("PATH", ""),
        "timestamp": datetime.now(UTC).isoformat()
    }


def generate_receipt(
    artifacts: list[Artifact],
    pipeline_cmd: str | None = None,
    started_at: datetime | None = None,
    finished_at: datetime | None = None,
    metrics: ReceiptMetrics | None = None,
    receipt_id: str | None = None
) -> dict[str, Any]:
    """Generate a receipt from artifacts and metadata."""

    if started_at is None:
        started_at = datetime.now(UTC)
    if finished_at is None:
        finished_at = datetime.now(UTC)

    if pipeline_cmd is None:
        pipeline_cmd = os.environ.get("VIGIL_PIPELINE_CMD", "unknown")

    if receipt_id is None:
        receipt_id = f"receipt_{int(time.time())}"

    owner, email = get_git_user_info()
    git_info = get_git_info()
    environment_info = get_environment_info()

    # Generate runlet ID
    runlet_id = f"runlet_{int(time.time())}"

    # Generate vigil URL
    vigil_url = f"vigil://receipt/{receipt_id}"

    # Get git ref
    try:
        git_ref = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        git_ref = "unknown"

    receipt: dict[str, Any] = {
        "$schema": "https://vigil.dev/schema/receipt/v1",
        "id": receipt_id,
        "issuer": owner,
        "runletId": runlet_id,
        "vigilUrl": vigil_url,
        "gitRef": git_ref,
        "owner": owner,
        "pipeline": pipeline_cmd,
        "inputs": [],
        "outputs": artifacts,
        "environment": environment_info,
        "git": git_info,
        "policies": ["reproducibility/v1"],
        "startedAt": started_at.isoformat(),
        "finishedAt": finished_at.isoformat(),
        "signature": "UNSIGNED-DEV"
    }

    if metrics:
        receipt["metrics"] = metrics

    return receipt


def verify_receipt(receipt: dict[str, Any]) -> bool:
    """Verify a receipt's integrity."""
    try:
        # Check required fields
        required_fields = ["id", "owner", "pipeline", "outputs", "environment", "git"]
        for field in required_fields:
            if field not in receipt:
                return False

        # Verify artifact checksums
        for artifact in receipt.get("outputs", []):
            if "checksum" not in artifact or "uri" not in artifact:
                return False

            # Verify checksum if file exists
            artifact_path = Path(artifact["uri"])
            if artifact_path.exists():
                expected_checksum = sha256(artifact_path)
                if artifact["checksum"] != expected_checksum:
                    return False

        return True
    except Exception:
        return False


class ReceiptManager:
    """Manager for receipt operations."""

    def __init__(self, receipts_dir: Path | str = ".vigil/receipts"):
        self.receipts_dir = Path(receipts_dir)
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

    def save_receipt(self, receipt: dict[str, Any]) -> Path:
        """Save a receipt to disk."""
        receipt_file = self.receipts_dir / f"{receipt['id']}.json"
        receipt_file.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return receipt_file

    def load_receipt(self, receipt_id: str) -> dict[str, Any] | None:
        """Load a receipt from disk."""
        receipt_file = self.receipts_dir / f"{receipt_id}.json"
        if not receipt_file.exists():
            return None

        try:
            return json.loads(receipt_file.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_receipts(self) -> list[dict[str, Any]]:
        """List all receipts."""
        receipts = []
        for receipt_file in self.receipts_dir.glob("*.json"):
            try:
                receipt = json.loads(receipt_file.read_text(encoding="utf-8"))
                receipts.append(receipt)
            except Exception:
                continue
        return receipts
