# Engrate Kit

A lightweight framework for building and running Engrate plugins.

It includes the following primary tools:

- uv
- FastAPI
- FastMCP
- SQLModel
- SQLAlchemy
- Alembic
- Pytest

There's also a CLI that helps users with project initialization and common
operations.

## Quick start

Initialize a new plugin:

```bash
uvx run engrate-kit init
uv sync
uv run engrate-kit dev
```

## Other commands

### Settings

View the currently loaded settings:

```bash
uv run engrate-kit show-settings
```

### Migrations

Migrations are handled through Alembic, wrapped in the Engrate Kit CLI.

Run these from your project root:

```bash
uv run engrate-kit makemigrations "message"
```

Autogenerate a new database migration based on your SQLModel definitions.

```bash
uv run engrate-kit migrate
```

Apply all migrations (upgrade to the latest revision).

```bash
uv run engrate-kit downgrade -1
```

Downgrade the database to a previous revision (e.g. `-1` or a specific revision ID).

```bash
uv run engrate-kit history
```

Show migration histoy.

### Development goodies

```bash
uv run devdb
```

Spawns a PostgreSQL instance via Docker using configuration from the
application settings object.
