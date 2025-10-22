from __future__ import annotations

import asyncio

import pytest

from vigil.mcp import server


def _call_tool(name: str, arguments: dict[str, object]) -> server.CallToolResult:
    return asyncio.run(server.call_tool(name, arguments))


def _result_text(result: server.CallToolResult) -> str:
    assert result.content, "call_tool should always return content"
    block = result.content[0]
    assert block.type == "text"
    return block.text


def test_run_target_rejects_path_traversal(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_run(cmd: object) -> None:  # pragma: no cover - should not run
        raise AssertionError("run_command should not be invoked for rejected targets")

    monkeypatch.setattr(server, "run_command", fail_run)

    result = _call_tool("run_target", {"targets": ["../evil"], "confirm": True})
    message = _result_text(result)
    assert "Invalid targets" in message
    assert ".." in message


def test_promote_rejects_outside_directories(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_run(cmd: object) -> None:  # pragma: no cover - should not run
        raise AssertionError("run_command should not be invoked for unsafe promotion paths")

    monkeypatch.setattr(server, "run_command", fail_run)

    result = _call_tool(
        "promote",
        {
            "confirm": True,
            "input_dir": "../../outside",
            "output_dir": "app/code/receipts",
        },
    )
    message = _result_text(result)
    assert "unsafe" in message
    assert "input dir" in message


def test_preview_data_requires_handle_suffix(monkeypatch: pytest.MonkeyPatch) -> None:
    result = _call_tool("preview_data", {"handle_path": "app/data/handles/data.csv"})
    message = _result_text(result)
    assert "Invalid handle path" in message
    assert "dhandle.json" in message
