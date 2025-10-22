from __future__ import annotations

import asyncio
import json
import sys

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from app.code.ai.mcp import server


def test_preview_data_rate_limit() -> None:
    server._preview_rate_limiter.reset()  # type: ignore[attr-defined]
    responses: list[str] = []
    for _ in range(server.PREVIEW_RATE_LIMIT):  # type: ignore[attr-defined]
        result = asyncio.run(server.call_tool("preview_data", {"limit": 5}))
        text = result.content[0].text  # type: ignore[index]
        responses.append(text)
    data = json.loads(responses[-1])
    assert data["effective_limit"] == 5

    limited = asyncio.run(server.call_tool("preview_data", {"limit": 5}))
    limited_text = limited.content[0].text  # type: ignore[index]
    assert "rate limit" in limited_text.lower()


def test_preview_data_enforces_max_rows() -> None:
    server._preview_rate_limiter.reset()  # type: ignore[attr-defined]
    result = asyncio.run(server.call_tool("preview_data", {"limit": 10_000}))
    text = result.content[0].text  # type: ignore[index]
    payload = json.loads(text)
    assert payload["requested_limit"] == 10_000
    assert payload["max_rows"] == server.PREVIEW_MAX_ROWS  # type: ignore[attr-defined]
    assert payload["limit"] == server.PREVIEW_MAX_ROWS  # type: ignore[attr-defined]
    assert payload["effective_limit"] == server.PREVIEW_MAX_ROWS  # type: ignore[attr-defined]


def test_preview_data_requires_offline_fallback(tmp_path) -> None:
    server._preview_rate_limiter.reset()  # type: ignore[attr-defined]
    handle_path = tmp_path / "missing_offline.dhandle.json"
    handle = {"uri": "s3://example-bucket/dataset.parquet", "format": "parquet"}
    handle_path.write_text(json.dumps(handle), encoding="utf-8")

    result = asyncio.run(
        server.call_tool(
            "preview_data",
            {"handle_path": str(handle_path), "limit": server.PREVIEW_MAX_ROWS + 100},
        )
    )
    text = result.content[0].text  # type: ignore[index]
    assert "offline_fallback" in text
    assert "app/data/samples" in text


def test_mcp_server_process_smoke() -> None:
    async def _exercise() -> list[str]:
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "app.code.ai.mcp.server"],
        )
        async with stdio_client(params) as (read_stream, write_stream), ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            listed = await session.list_tools()
            tool_names = {tool.name for tool in listed.tools}
            assert "preview_data" in tool_names

            outputs: list[str] = []
            for _ in range(2):
                result = await session.call_tool("preview_data", {"limit": 5})
                assert not result.isError
                text = "\n".join(
                    content.text
                    for content in result.content
                    if getattr(content, "type", None) == "text"
                )
                outputs.append(text)
            return outputs

    previews = asyncio.run(_exercise())
    assert len(previews) == 2

    payload = json.loads(previews[-1])
    assert payload["requested_limit"] == 5
    assert payload["limit"] <= server.PREVIEW_MAX_ROWS  # type: ignore[attr-defined]
