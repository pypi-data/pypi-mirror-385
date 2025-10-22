from __future__ import annotations

import json
from pathlib import Path

from vigil.tools import data_handles


def _write_handle(base: Path, name: str, payload: dict[str, object]) -> Path:
    handles_dir = base / "app" / "data" / "handles"
    handles_dir.mkdir(parents=True, exist_ok=True)
    handle_path = handles_dir / name
    handle_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return handle_path


def test_data_handle_lint_success(tmp_path: Path) -> None:
    samples_dir = tmp_path / "app" / "data" / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)
    (samples_dir / "sample.csv").write_text("id,value\n1,2\n", encoding="utf-8")

    payload = {
        "uri": "s3://demo/sample.parquet",
        "format": "csv",
        "offline_fallback": "app/data/samples/sample.csv",
        "schema": {"columns": {"id": "int32", "value": "float32"}},
        "consent": "public",
    }
    handle_path = _write_handle(tmp_path, "sample.dhandle.json", payload)

    reports = data_handles.lint_handles([handle_path], base_path=tmp_path)
    assert len(reports) == 1
    report = reports[0]
    assert report.status is data_handles.LintSeverity.OK
    assert report.issues == []

    aggregated = data_handles.build_report(reports, base_path=tmp_path)
    assert aggregated["summary"]["status"] == "ok"
    assert aggregated["summary"]["handles"] == 1


def test_data_handle_lint_detects_offline_and_schema(tmp_path: Path) -> None:
    payload = {
        "format": "csv",
        "offline_fallback": "../secret.csv",
    }
    handle_path = _write_handle(tmp_path, "invalid.dhandle.json", payload)

    reports = data_handles.lint_handles([handle_path], base_path=tmp_path)
    assert len(reports) == 1
    report = reports[0]
    codes = {issue.code for issue in report.issues}
    assert "schema_missing" in codes
    assert "offline_scope" in codes
    assert report.status is data_handles.LintSeverity.ERROR

    summary = data_handles.build_report(reports, base_path=tmp_path)
    assert summary["summary"]["status"] == "error"
    assert summary["summary"]["errors"] == 1
