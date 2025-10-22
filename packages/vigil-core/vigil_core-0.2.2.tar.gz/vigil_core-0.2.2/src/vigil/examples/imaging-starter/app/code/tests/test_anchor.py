from __future__ import annotations

import json
from pathlib import Path

import pytest
from vigil.tools import anchor, receipt_index


@pytest.fixture()
def repo_layout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    monkeypatch.chdir(tmp_path)
    receipts_dir = tmp_path / "app/code/receipts"
    receipts_dir.mkdir(parents=True)
    anchors_dir = tmp_path / "app/code/anchors"
    anchors_dir.mkdir(parents=True)
    state_path = anchors_dir / "state.json"
    bundle_dir = anchors_dir / "proofs"
    manifest_path = anchors_dir / "latest.json"
    index_path = receipts_dir / "index.json"
    return {
        "receipts": receipts_dir,
        "state": state_path,
        "bundle_dir": bundle_dir,
        "manifest": manifest_path,
        "index": index_path,
    }


def test_anchor_creates_merkle_bundle(repo_layout: dict[str, Path]) -> None:
    receipt_a = repo_layout["receipts"] / "receipt_a.json"
    receipt_b = repo_layout["receipts"] / "receipt_b.json"
    receipt_a.write_text("alpha", encoding="utf-8")
    receipt_b.write_text("bravo", encoding="utf-8")

    repo_root = Path.cwd()
    index = receipt_index.load_index(repo_layout["index"])
    for receipt_path in (receipt_a, receipt_b):
        entry: receipt_index.ReceiptEntry = {
            "path": receipt_path.relative_to(repo_root).as_posix(),
            "hash": "sha256:placeholder",
            "issuer": "Vigil",
            "vigilUrl": "vigil://example/run",
            "gitRef": "abcdef123456",
            "capsuleDigest": "unknown",
            "runletId": "rl_test",
            "startedAt": "2024-01-01T00:00:00Z",
            "finishedAt": "2024-01-01T00:05:00Z",
            "outputs": [],
            "metrics": {},
            "glyphs": ["RECEIPT"],
            "anchor": None,
        }
        receipt_index.upsert_receipt(index, entry)
    receipt_index.write_index(repo_layout["index"], index)

    result = anchor.anchor_receipts(
        repo_layout["receipts"],
        repo_layout["state"],
        repo_layout["bundle_dir"],
        repo_layout["manifest"],
        repo_layout["index"],
    )

    assert result.root is not None
    assert result.bundle_path is not None
    assert result.bundle_path.exists()
    assert anchor.verify_receipt(result.bundle_path, receipt_a)
    assert anchor.verify_receipt(result.bundle_path, receipt_b)

    state_data = json.loads(repo_layout["state"].read_text(encoding="utf-8"))
    assert len(state_data["processed"]) == 2
    manifest_data = json.loads(repo_layout["manifest"].read_text(encoding="utf-8"))
    assert manifest_data["root"] == result.root
    index_after = receipt_index.load_index(repo_layout["index"])
    anchors = [entry.get("anchor") for entry in index_after.get("receipts", [])]
    assert any(anchor_info and anchor_info.get("root") == result.root for anchor_info in anchors)

    proof_url = "https://proofs.example/anchor/bundle"
    anchor.record_proof(
        result.bundle_path,
        proof_url,
        repo_layout["state"],
        repo_layout["manifest"],
        repo_layout["index"],
    )
    index_with_proof = receipt_index.load_index(repo_layout["index"])
    proof_links = [entry["anchor"]["proofUrl"] for entry in index_with_proof.get("receipts", []) if entry.get("anchor")]
    assert proof_url in proof_links
    updated_manifest = json.loads(repo_layout["manifest"].read_text(encoding="utf-8"))
    assert updated_manifest["proof_url"] == proof_url


def test_anchor_skips_when_no_new_receipts(repo_layout: dict[str, Path]) -> None:
    receipt = repo_layout["receipts"] / "receipt.json"
    receipt.write_text("charlie", encoding="utf-8")

    first = anchor.anchor_receipts(
        repo_layout["receipts"],
        repo_layout["state"],
        repo_layout["bundle_dir"],
        repo_layout["manifest"],
        repo_layout["index"],
    )
    assert first.root is not None

    second = anchor.anchor_receipts(
        repo_layout["receipts"],
        repo_layout["state"],
        repo_layout["bundle_dir"],
        repo_layout["manifest"],
        repo_layout["index"],
    )
    assert second.root is None
    manifest_data = json.loads(repo_layout["manifest"].read_text(encoding="utf-8"))
    assert manifest_data["root"] is None
    assert manifest_data["new_receipts"] == []
