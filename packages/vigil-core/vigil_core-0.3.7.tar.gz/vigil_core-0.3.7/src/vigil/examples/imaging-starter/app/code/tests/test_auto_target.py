from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest
from vigil.tools import promote as promote_tool

from app.code.ai import assistant
from app.code.ai.auto_target import AutoTargetAgent
from app.code.ai.mcp import server as mcp_server
from app.code.lib.steps.metrics import run as metrics_run
from app.code.lib.steps.segment import run as segment_run


class _AssistantRunStub:
    def __call__(self, parts: list[str]) -> assistant._CommandResult:  # type: ignore[attr-defined]
        if "--dag" in parts:
            return assistant._CommandResult(True, "digraph G {}", "")  # type: ignore[attr-defined]
        return assistant._CommandResult(True, "Dry run succeeded", "")  # type: ignore[attr-defined]


class _RunCommandStub:
    def __init__(self, artifacts_dir: Path, receipts_dir: Path) -> None:
        self.artifacts_dir = artifacts_dir
        self.receipts_dir = receipts_dir
        self.commands: list[list[str]] = []

    def __call__(self, parts: list[str]) -> mcp_server.CommandResult:
        self.commands.append(list(parts))
        if "-n" in parts:
            return mcp_server.CommandResult(True, "DRY RUN", "")
        if "snakemake" in parts:
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)
            processed = self.artifacts_dir / "processed.parquet"
            segment_run("app/data/handles/data.parquet.dhandle.json", str(processed))
            metrics_path = self.artifacts_dir / "metrics.json"
            metrics_run(
                str(processed),
                "app/data/handles/data.parquet.dhandle.json",
                str(metrics_path),
            )
            return mcp_server.CommandResult(True, "EXECUTION", "")
        if any(part.endswith("promote.py") for part in parts):
            in_dir = Path(parts[parts.index("--in") + 1])
            out_dir = Path(parts[parts.index("--out") + 1])
            vigil = parts[parts.index("--vigil-url") + 1]
            promote_tool.main(
                str(in_dir),
                str(out_dir),
                vigil,
                profile=None,
                attestation_blob=None,
            )
            assert out_dir.exists(), "promotion did not create receipts directory"
            assert list(out_dir.glob("receipt_*.json")), "promotion did not write receipt"
            return mcp_server.CommandResult(True, "PROMOTED", "")
        return mcp_server.CommandResult(True, "OK", "")


def _read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_auto_target_full_flow(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    artifacts_dir = tmp_path / "artifacts"
    receipts_dir = tmp_path / "receipts"
    suggestion_path = tmp_path / "suggestions" / "cell.py"
    state_path = tmp_path / "state.json"
    report_path = tmp_path / "report.md"
    log_path = tmp_path / "log.json"

    agent = AutoTargetAgent(
        suggestion_path=suggestion_path,
        state_path=state_path,
        report_path=report_path,
        receipt_log_path=log_path,
        artifacts_dir=artifacts_dir,
        receipts_dir=receipts_dir,
    )

    monkeypatch.setattr(assistant, "_run_command", _AssistantRunStub())
    run_stub = _RunCommandStub(artifacts_dir, receipts_dir)
    monkeypatch.setattr(mcp_server, "run_command", run_stub)

    panel_state = {"target": "all", "paramSuggestions": {"process.threshold": 0.6}}
    state = agent.propose(panel_state)
    assert state.dry_run_ok
    assert suggestion_path.exists()

    updated = agent.apply()
    assert updated.run_message is not None
    assert report_path.exists()
    report_text = report_path.read_text(encoding="utf-8")
    assert "Auto-Target Report" in report_text
    assert "Metrics snapshot" in report_text
    assert receipts_dir.exists()
    commands = list(run_stub.commands)
    assert any(any(part.endswith("promote.py") for part in cmd) for cmd in commands)
    receipts = list(receipts_dir.glob("receipt_*.json"))
    assert receipts
    log = _read_json(log_path)
    assert any(event["action"] == "apply" for event in log["events"])  # type: ignore[index]
