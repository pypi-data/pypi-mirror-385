# {{name}}

{{description}}

## Usage

Start the development server:

```bash
uv run engrate-kit dev
```

Start the production server:

```bash
uv run engrate-kit run
```

## Migrations

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

## Docker

You can build and run the included Docker image:

```bash
docker build -t engrate-plugin .
docker run -p 8000:8000 engrate-plugin
```
