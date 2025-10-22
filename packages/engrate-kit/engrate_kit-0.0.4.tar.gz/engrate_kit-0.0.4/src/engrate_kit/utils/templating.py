import re
import shutil
import tomllib
from pathlib import Path

import tomli_w
import typer

VALID_NAME = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9_-]*[A-Za-z0-9])?$")


def to_canonical(name: str) -> str:
    """Turn human-friendly name to canonical name (for use in pyrpoject.toml
    for example).

    """
    clean = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip())
    return clean.strip("-").lower()


def copy_templates(template_dir: Path, target_dir: Path, replacements: dict):
    for src_path in template_dir.rglob("*"):
        if "__pycache__" in src_path.parts:
            continue

        # Compute destination path (replace placeholders in folder names)
        rel_path = str(src_path.relative_to(template_dir))
        for key, val in replacements.items():
            rel_path = rel_path.replace(f"{{{{{key}}}}}", val)
        dst_path = target_dir / rel_path

        if src_path.is_dir():
            dst_path.mkdir(parents=True, exist_ok=True)
            continue

        name = dst_path.name

        # Skip files if present
        if name in ("README.md", "alembic.ini") and dst_path.exists():
            typer.echo(f"Skipping existing {name}")
            continue

        # Update pyproject.toml
        # if name == "pyproject.toml" and dst_path.exists():
        #     overwrite = typer.confirm(f"File '{dst_path}' exists. Overwrite?")
        #     if not overwrite:
        #         typer.echo(f"Skipped {dst_path}")
        #         continue
        # update_pyproject(dst_path, src_path, replacements)
        # continue

        # App module files (ask to overwrite each individual file)
        if dst_path.exists():
            overwrite = typer.confirm(f"File '{dst_path}' exists. Overwrite?")
            if not overwrite:
                typer.echo(f"Skipped {dst_path}")
                continue

        # Write the files that made it here...
        content_ext = src_path.suffix.lower()

        if content_ext == ".mako":
            shutil.copy2(src_path, dst_path)
        else:
            content = src_path.read_text()
            for key, val in replacements.items():
                content = content.replace(f"{{{{{key}}}}}", val)
            dst_path.write_text(content)

        typer.echo(f"Wrote {dst_path}")


def update_pyproject(dst_path: Path, template_path: Path, replacements: dict):
    """Safely update or merge pyproject.toml."""
    # This was an experiment to update only parts of the pyproject.toml. Seems
    # to be working, but maybe not worth the hassle.
    overwrite = typer.confirm(f"'{dst_path.name}' exists. Update project metadata?")
    if not overwrite:
        typer.echo("Keeping existing pyproject.toml")
        return

    data = tomllib.loads(dst_path.read_text())
    template_data = tomllib.loads(template_path.read_text())

    # Update project settings

    project = data.setdefault("project", {})

    project["name"] = replacements["canonical_name"]
    project["description"] = replacements["description"]

    tpl_proj = template_data.get("project", {})

    if "dependencies" in tpl_proj:
        deps = set(project.get("dependencies", [])) | set(tpl_proj["dependencies"])
        project["dependencies"] = sorted(deps)

    # Update build system

    build_system = data.setdefault("build-system", {})
    tpl_build_system = template_data.get("build-system", {})

    if "requires" in tpl_build_system:
        requires = set(build_system.get("requires", [])) | set(
            tpl_build_system["requires"]
        )
        build_system["requires"] = sorted(requires)

    if "build-backend" in tpl_build_system:
        build_system["build-backend"] = tpl_build_system["build-backend"]

    dst_path.write_text(tomli_w.dumps(data))
    typer.echo("Updated pyproject.toml.")
