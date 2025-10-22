from __future__ import annotations

import json
from collections.abc import Callable, Mapping  # noqa: TCH003
from datetime import UTC, datetime, timedelta
from pathlib import Path  # noqa: TCH003
from typing import Any

import pytest
import yaml
from vigil.tools import vigilurl

from app.code.lib.paths import PROJECT_ROOT
from app.code.lib.vigil_resolver import (
    HmacSigner,
    ResolverApp,
    ResolverError,
    VigilResolver,
)


def _write_manifest(path: Path, data: Mapping[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(data, fh, sort_keys=False)


def _build_environ(path: str, query: str, method: str = "GET") -> Mapping[str, Any]:
    return {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query,
        "wsgi.input": b"",
    }


def _call_app(app: Callable, environ: Mapping[str, Any]) -> tuple[str, dict[str, str], bytes]:
    status_holder: dict[str, Any] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_holder["status"] = status
        status_holder["headers"] = dict(headers)

    body_iter = app(environ, start_response)
    body = b"".join(body_iter)
    return status_holder["status"], status_holder["headers"], body


def _base_manifest(image_digest: str) -> dict[str, Any]:
    return {
        "version": 1,
        "resolverHost": "labs.example",
        "org": "acme-lab",
        "project": "imaging-starter",
        "capsule": {
            "image": f"ghcr.io/acme-lab/capsule@{image_digest}",
            "extensions": [],
        },
        "inputs": ["s3://demo-bucket/microscopy/"],
        "policies": {"requireReceipts": True},
    }


@pytest.fixture()
def signer() -> HmacSigner:
    return HmacSigner("super-secret-key", "acme-signing-key")


def test_resolver_contract_round_trip(signer: HmacSigner, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = PROJECT_ROOT
    monkeypatch.chdir(repo_root)

    manifest, _ = vigilurl.load_manifest()
    url = vigilurl.build_vigil_url(manifest)

    resolver = VigilResolver(base_path=repo_root, signer=signer)
    spec, _ = resolver.resolve(url)

    expected_spec_path = repo_root / ".vigil" / "workspace.spec.json"
    expected_spec = json.loads(expected_spec_path.read_text(encoding="utf-8"))

    expected_capsule_digest = expected_spec["capsule"]["image"].split("@", 1)[1]
    assert spec.capsuleDigest == expected_capsule_digest
    assert spec.inputs == expected_spec["inputs"]
    assert spec.scopes == expected_spec["scopes"]
    assert spec.policies == expected_spec["policies"]


def test_resolver_returns_signed_spec(tmp_path: Path, signer: HmacSigner) -> None:
    digest = "sha256:deadbeef"
    _write_manifest(tmp_path / "vigil.yaml", _base_manifest(digest))

    def clock() -> datetime:
        return datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
    resolver = VigilResolver(base_path=tmp_path, signer=signer, clock=clock, ttl=timedelta(minutes=45))
    app = ResolverApp(resolver)

    url = f"vigil://labs.example/acme-lab/imaging-starter@refs/heads/main?img={digest}"
    environ = _build_environ("/.well-known/vigil/resolve", f"url={url}")
    status, headers, body = _call_app(app, environ)

    assert status == "200 OK"
    assert headers["Content-Type"] == "application/json"

    payload = json.loads(body)
    spec = payload["spec"]
    signature = payload["signature"]

    assert spec == {
        "ref": "refs/heads/main",
        "capsuleDigest": digest,
        "inputs": ["s3://demo-bucket/microscopy/"],
        "scopes": ["preview_data", "run_target", "promote"],
        "policies": {"requireReceipts": True},
        "issuedAt": "2024-01-01T00:00:00Z",
        "expiresAt": "2024-01-01T00:45:00Z",
    }

    bundle = signer.sign(spec)
    assert signature == {
        "algorithm": bundle.algorithm,
        "keyId": bundle.key_id,
        "value": bundle.value,
    }


def test_resolver_falls_back_to_bench_manifest(tmp_path: Path, signer: HmacSigner) -> None:
    digest = "sha256:feedface"
    _write_manifest(tmp_path / "bench.yaml", _base_manifest(digest))

    resolver = VigilResolver(base_path=tmp_path, signer=signer)
    spec, _ = resolver.resolve(
        f"vigil://labs.example/acme-lab/imaging-starter@refs/heads/main?img={digest}"
    )

    assert spec.capsuleDigest == digest


def test_resolver_rejects_mismatched_host(tmp_path: Path, signer: HmacSigner) -> None:
    digest = "sha256:badcafe"
    _write_manifest(tmp_path / "vigil.yaml", _base_manifest(digest))

    resolver = VigilResolver(base_path=tmp_path, signer=signer)
    with pytest.raises(ResolverError):
        resolver.resolve(
            f"vigil://other.example/acme-lab/imaging-starter@refs/heads/main?img={digest}"
        )


def test_resolver_blocks_pat_scopes(tmp_path: Path, signer: HmacSigner) -> None:
    digest = "sha256:abc123"
    manifest = _base_manifest(digest)
    manifest["scopes"] = ["personalAccessToken"]
    _write_manifest(tmp_path / "vigil.yaml", manifest)

    resolver = VigilResolver(base_path=tmp_path, signer=signer)
    url = f"vigil://labs.example/acme-lab/imaging-starter@refs/heads/main?img={digest}"
    with pytest.raises(ResolverError):
        resolver.resolve(url)


def test_http_app_handles_bad_method(tmp_path: Path, signer: HmacSigner) -> None:
    digest = "sha256:012345"
    _write_manifest(tmp_path / "vigil.yaml", _base_manifest(digest))
    resolver = VigilResolver(base_path=tmp_path, signer=signer)
    app = ResolverApp(resolver)

    environ = _build_environ("/.well-known/vigil/resolve", "", method="POST")
    status, _, body = _call_app(app, environ)

    assert status == "405 Method Not Allowed"
    assert json.loads(body) == {"error": "method not allowed"}


def test_http_app_surfaces_resolver_errors(tmp_path: Path, signer: HmacSigner) -> None:
    digest = "sha256:cafefeed"
    _write_manifest(tmp_path / "vigil.yaml", _base_manifest(digest))
    resolver = VigilResolver(base_path=tmp_path, signer=signer)
    app = ResolverApp(resolver)

    bad_url = f"vigil://labs.example/acme-lab/other-project@refs/heads/main?img={digest}"
    environ = _build_environ("/.well-known/vigil/resolve", f"url={bad_url}")
    status, _, body = _call_app(app, environ)

    assert status == "400 Bad Request"
    payload = json.loads(body)
    assert payload["error"] == "url project does not match manifest"
