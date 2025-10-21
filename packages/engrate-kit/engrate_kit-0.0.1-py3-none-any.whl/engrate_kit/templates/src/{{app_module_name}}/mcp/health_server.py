from fastmcp import FastMCP

server = FastMCP(name="HealthMCP")


@server.tool
def get_health() -> dict:
    """Return health information."""
    return {"status": "ok"}
