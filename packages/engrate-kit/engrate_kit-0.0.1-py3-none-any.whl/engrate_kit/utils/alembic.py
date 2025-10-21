import importlib.util
import sys
from pathlib import Path

from alembic import context
from alembic.config import Config
from sqlalchemy.engine.url import make_url
from sqlmodel import SQLModel

from .plugin import find_plugin_root, find_settings


def get_alembic_config() -> Config:
    """Load Alembic config from plugin root, inject DB_URL, and import models."""
    root = find_plugin_root()

    ini_path = root / "alembic.ini"
    migrations_dir = root / "migrations"

    if not ini_path.exists():
        raise FileNotFoundError(f"No alembic.ini found in {root}")

    settings, module = find_settings()

    cfg = Config(str(ini_path))
    cfg.set_main_option("sqlalchemy.url", to_sync_url(settings.DB_URL))
    cfg.set_main_option("script_location", str(migrations_dir))
    cfg.config_file_name = str(ini_path)

    # Dynamically import project models to populate SQLModel.metadata. This
    # may not be strictly necessary if we add the import to the env file. My
    # initial goal was to be able to run everything with vanilla generated
    # alembic files.

    assert module.__file__ is not None
    conf_path = Path(module.__file__).resolve()
    src_dir = next(p for p in conf_path.parents if p.name == "src")
    package_name = conf_path.parent.name

    # Ensure src/ is importable
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    models_module_name = f"{package_name}.models"

    try:
        importlib.import_module(models_module_name)
        print(f"Imported {models_module_name}")
    except ModuleNotFoundError as e:
        print(f"Warning: could not import {models_module_name}: {e}")

    setattr(context, "target_metadata", SQLModel.metadata)

    return cfg


def to_sync_url(url: str) -> str:
    """We're using the default synchronous alembic env to make templating
    easier for now."""
    u = make_url(url)
    replacements = {
        "sqlite+aiosqlite": "sqlite",
        "postgresql+asyncpg": "postgresql+psycopg",
    }
    for k, v in replacements.items():
        if u.drivername.startswith(k):
            u = u.set(drivername=v)
            break
    return str(u)
