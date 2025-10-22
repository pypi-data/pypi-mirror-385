import importlib
import importlib.util
import sys
from enum import Enum
from pathlib import Path
from types import ModuleType
from typing import List

import yaml
from pydantic import BaseModel

from ..core.conf import DefaultSettings


class Category(str, Enum):
    BILLING = "billing"
    CONTROLLING = "controlling"
    FORECAST = "forecast"
    MARKET_INTELLIGENCE = "market_intelligence"
    METERING = "metering"
    OPTIMIZATION = "optimization"
    SCHEDULING = "scheduling"
    SETTLEMENT = "settlement"
    STRUCTURING = "structuring"
    TRADING = "trading"


class Market(str, Enum):
    ALL = "*"
    DE = "de"
    NL = "nl"
    SE = "se"


class Flavor(str, Enum):
    EXTERNAL_API = "external-api"


class Trait(str, Enum):
    STORAGE = "storage"


class Extensions(BaseModel):
    markets: List[Market]


class PluginMetadata(BaseModel):
    display_name: str
    service_name: str
    url_prefix: str
    fav_icon: str
    image: str
    port: str
    flavors: List[Flavor]
    traits: List[Trait]


class Manifest(BaseModel):
    name: str
    author: str
    description: str
    product_category: Category
    extensions: Extensions
    plugin_metadata: PluginMetadata


def load_manifest(path: str) -> Manifest:
    """Load and parse manifest file."""
    with Path(path).open() as file:
        data = yaml.safe_load(file)
        return Manifest(**data)


def find_plugin_root() -> Path:
    """Find and return plugin root directory."""
    path = Path.cwd()
    for parent in [path] + list(path.parents):
        if (parent / "plugin_manifest.yaml").exists():
            return parent
    raise FileNotFoundError("Not inside an Engrate plugin directory.")


def find_settings() -> tuple[DefaultSettings, ModuleType]:
    """Search recursively under ./src for a conf.py file containing a
    `settings` object. Import it dynamically and return (settings, module).

    """
    root = find_plugin_root()
    src = root / "src"

    if not src.exists():
        raise FileNotFoundError(
            "No src/ directory found in current plugin directory or its children."
        )

    conf_files = list(src.rglob("conf.py"))
    if not conf_files:
        raise FileNotFoundError("No conf.py found under src/")

    for conf_file in conf_files:
        spec = importlib.util.spec_from_file_location("user_conf", conf_file)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules["user_conf"] = module
        spec.loader.exec_module(module)

        if hasattr(module, "settings"):
            settings = getattr(module, "settings")
            if isinstance(settings, DefaultSettings):
                return settings, module

    raise ImportError("No settings object found in any conf.py file.")
