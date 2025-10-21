from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]


class DefaultSettings(BaseSettings):
    """Default Engrate plugin settings."""

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_OPENAPI_ENABLED: bool = True
    BASE_URL: str = "http://localhost:8000/"
    API_PREFIX: str = "/api"

    # Database
    DB_URL: str = "sqlite+aiosqlite:///default.db"
    DB_ECHO_SQL: bool = False

    # MCP
    MCP_PATH: str = "/mcp/"

    # Internal
    DEBUG: bool = False

    # Logging
    LOG_LEVEL: LogLevel = "INFO"
    LOG_JSON_FORMAT: bool = False

    # Plugin
    PLUGIN_REGISTER_ON_APP_START: bool = False
    PLUGIN_REGISTRAR_URL: str = "https://api.engrate.io/plugins"

    # CORS
    CORS_ENABLED: bool = True
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOWED_ORIGINS: list[str] = ["*"]
    CORS_ALLOWED_METHODS: list[str] = ["*"]
    CORS_ALLOWED_HEADERS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
