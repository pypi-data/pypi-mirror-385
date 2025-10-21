import json

import pytest


@pytest.mark.asyncio
async def test_health_is_registered(mcp_client):
    """Ensure the health tool is registered."""
    async with mcp_client:
        tools = await mcp_client.list_tools()
    assert any(tool.name == "get_health" for tool in tools)


@pytest.mark.asyncio
async def test_health_tool(mcp_client):
    """Test that the health tool returns correctly."""
    async with mcp_client:
        result = await mcp_client.call_tool("get_health", {})
        result = json.loads(result.content[0].text)
        assert result["status"] == "ok"
