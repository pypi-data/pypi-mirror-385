import pytest
from fastapi.testclient import TestClient
from fastmcp.client import Client as MCPClient
from fastmcp.client.transports import FastMCPTransport


@pytest.fixture(autouse=True)
def in_memory_db(monkeypatch):
    monkeypatch.setenv("DB_URL", "sqlite+aiosqlite:///:memory:")


@pytest.fixture
def client():
    """Inject a FastAPI test client."""
    from {{app_module_name}}.app import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def mcp_client():
    """Inject a FastAPI test client."""
    from {{app_module_name}}.app import app

    assert app.mcp_server is not None
    return MCPClient(transport=FastMCPTransport(app.mcp_server))
