import pytest
from fastapi.testclient import TestClient
from fastmcp.client import Client as MCPClient
from fastmcp.client.transports import FastMCPTransport

from {{app_module_name}}.app import app


@pytest.fixture
def client():
    """Inject a FastAPI test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mcp_client():
    """Inject a FastAPI test client."""
    assert app.mcp_server is not None
    return MCPClient(transport=FastMCPTransport(app.mcp_server))
