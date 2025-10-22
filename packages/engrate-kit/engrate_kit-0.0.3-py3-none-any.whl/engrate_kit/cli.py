import importlib.metadata as md
from pathlib import Path

import typer
from alembic import command
from fastapi_cli.cli import dev as fastapi_dev
from fastapi_cli.cli import run as fastapi_run

from .utils.alembic import get_alembic_config
from .utils.devdb import start_postgres_container
from .utils.plugin import Category, find_plugin_root, find_settings
from .utils.templating import copy_templates, to_canonical

TEMPLATE_DIR = Path(__file__).parent / "templates"

app = typer.Typer()

# Nice things for devs


@app.command()
def devdb(
    data_dir: str = typer.Option(
        "pgdata",
        "--data-dir",
        help="Path to the data directory for postgers. Defaults to './pgdata'.",
    ),
):
    try:
        settings, _ = find_settings()
        start_postgres_container(settings.DB_URL, data_dir)
    except Exception as e:
        typer.echo(f"Error: {e}")


# Plugin and metadata commands


@app.command()
def init(
    name: str = typer.Option(
        None,
        "--name",
        "-n",
        prompt="Project name",
        help="The name of your new project.",
    ),
    description: str = typer.Option(
        None,
        "--description",
        "-d",
        prompt="Project description",
        help="Description of your project.",
    ),
    author: str = typer.Option(
        None,
        "--author",
        prompt="Author name",
        help="The name of the author of the plugin.",
    ),
    # NOTE: We can make this more interactive with InquirerPy or questionary.
    product_category: Category = typer.Option(
        None,
        "--product-category",
        prompt=True,
        help="Product category of your plugin.",
    ),
    app_module_name: str = typer.Option(
        "plugin",
        "--app-module-name",
        help="The module name of your app.",
    ),
):
    canonical = to_canonical(name)
    target_dir = Path.cwd()

    # Get our own version
    version = md.version("engrate_kit")

    replacements = {
        "project_name": name,
        "canonical_name": canonical,
        "app_module_name": app_module_name,
        "author": author,
        "product_category": product_category,
        "description": description,
        "kit_version": version,
    }

    copy_templates(TEMPLATE_DIR, target_dir, replacements)
    typer.echo(f"Created project '{name}' in {target_dir.resolve()}")


@app.command()
def show_settings():
    """Locate and print discovered settings object."""
    try:
        settings, module = find_settings()
        typer.echo(f"Found settings in: {module.__file__}")
        for name, value in settings.model_dump().items():
            typer.echo(f"{name} = {value}")
    except Exception as e:
        typer.echo(f"Error: {e}")


# FastAPI commands

app.command("dev")(fastapi_dev)

app.command("run")(fastapi_run)

# Alembic wrappers


@app.command()
def initmigrations():
    """Initialize Alembic migrations directory next to src/ in the plugin
    root.

    """
    root = find_plugin_root()
    migrations_dir = root / "migrations"

    if migrations_dir.exists():
        typer.echo(f"Migrations directory already exists at {migrations_dir}")
        return

    typer.echo(f"Creating migrations directory at {migrations_dir}...")

    ini_path = root / "alembic.ini"
    if not ini_path.exists():
        typer.echo(f"No alembic.init exists at {migrations_dir}")
        return

    cfg = get_alembic_config()

    command.init(cfg, str(migrations_dir), "generic")

    typer.echo("Alembic migrations initialized.")


@app.command()
def makemigrations(message: str = typer.Argument("auto", help="Revision message")):
    """Autogenerate a new Alembic revision."""
    cfg = get_alembic_config()
    command.revision(cfg, message=message, autogenerate=True)
    typer.echo("Revision created.")


@app.command()
def migrate():
    """Apply all database migrations (upgrade to latest)."""
    cfg = get_alembic_config()
    command.upgrade(cfg, "head")
    typer.echo("Database upgraded to latest revision.")


@app.command()
def downgrade(
    revision: str = typer.Argument(
        "-1", help="Target revision (e.g., base, -1, abc123)"
    ),
):
    """Downgrade the database to a previous revision."""
    cfg = get_alembic_config()
    command.downgrade(cfg, revision)
    typer.echo(f"Database downgraded to {revision}.")


@app.command()
def history():
    """Show migration history."""
    cfg = get_alembic_config()
    command.history(cfg)


if __name__ == "__main__":
    app()
