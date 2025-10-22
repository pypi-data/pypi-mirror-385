import asyncio
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from .conf import DefaultSettings
from .db import db_lifespan
from .lifespan import compose_lifespans
from .logging import configure_logging, get_logger
from .mcp import mcp_lifespan

logger = get_logger(__name__)


class App(FastAPI):
    settings = DefaultSettings()
    mcp_server = None

    def __init__(self, title=None, settings=None, lifespan=None, *args, **kwargs):
        title = title if title is not None else "Engrate plugin"

        if settings is not None:
            self.settings = settings

        self.configure_logger()

        lifespan = compose_lifespans(*self.get_lifespans(), lifespan)
        super().__init__(
            lifespan=lifespan,
            title=title,
            description="lol",
            version="0.1.0",
            *args,
            **kwargs,
        )

        self.add_cors_middleware()

    def add_cors_middleware(self):
        self.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.CORS_ALLOWED_ORIGINS,
            allow_credentials=self.settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=self.settings.CORS_ALLOWED_METHODS,
            allow_headers=self.settings.CORS_ALLOWED_HEADERS,
        )

    def get_lifespans(self):
        """Return a list of all core lifespan context managers."""
        return (
            mcp_lifespan,
            db_lifespan,
        )

    def include_mcp_server(self, mcp_server, prefix=None):
        """Import `mcp_server` and expose with `prefix`. If no prefix is given
        the components will be merged into the default server and keep their
        original names. If no core mcp server has been started it will be
        started and mounted.

        """
        if self.mcp_server is None:
            self.mcp_server = FastMCP(name=self.title)
            # We use the path / here as we're mounting the main server at
            # `settings.MCP_PATH` below.
            self.mcp_app = self.mcp_server.http_app(path="/")
            self.mount(self.settings.MCP_PATH, self.mcp_app)
            logger.debug("Mounted MCP core application at %s", self.settings.MCP_PATH)

        async def import_server():
            assert self.mcp_server is not None
            await self.mcp_server.import_server(mcp_server, prefix=prefix)

        loop = asyncio.get_event_loop()
        asyncio.ensure_future(import_server(), loop=loop)

        logger.debug("Registered MCP server.")

    def openapi(self) -> dict[str, Any]:
        """Generate or return cached OpenAPI schema."""
        if getattr(self, "_openapi_schema", None) is not None:
            return self._openapi_schema

        schema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.routes,
            tags=getattr(self, "openapi_tags", None),
            servers=[{"url": self.settings.BASE_URL}],
            contact=getattr(self, "contact", None),
            license_info=getattr(self, "license_info", None),
        )

        schema["x-logo"] = {"url": "https://www.engrate.io/engrate_logo_black.png"}

        self._openapi_schema = schema
        return schema

    def configure_logger(self):
        """Set up logging behavior."""
        configure_logging(
            level=self.settings.LOG_LEVEL,
            json_format=self.settings.LOG_JSON_FORMAT,
        )
