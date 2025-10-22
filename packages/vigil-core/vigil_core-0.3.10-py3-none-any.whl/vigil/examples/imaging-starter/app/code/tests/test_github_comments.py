from __future__ import annotations

import textwrap

from vigil.tools import vigilurl

from app.code.tools import github_comments


def test_render_vigil_link_comment_uses_manifest_url(tmp_path, monkeypatch):
    manifest = textwrap.dedent(
        """
        resolverHost: resolver.example
        org: acme
        project: demo
        capsule:
          image: repo@sha256:abc123
        """
    )
    (tmp_path / "vigil.yaml").write_text(manifest, encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    cfg, _ = vigilurl.load_manifest()
    base_url = vigilurl.build_vigil_url(cfg)

    comment = github_comments.render_vigil_link_comment("deadbeef")

    assert github_comments.OPEN_LINK_MARKER in comment
    assert f"{base_url}&ref=deadbeef" in comment


def test_render_metrics_comment_includes_marker() -> None:
    table = "| Metric | Value |\n| score | 0.5 |"
    comment = github_comments.render_metrics_comment(
        table,
        receipt_url="https://example.com/receipt",  # ensures link rendering
        receipt_name="receipt.json",
    )

    assert github_comments.METRICS_MARKER in comment
    assert "[Download receipt.json](https://example.com/receipt)" in comment
