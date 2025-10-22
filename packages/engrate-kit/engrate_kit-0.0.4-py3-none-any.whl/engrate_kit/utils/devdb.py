import os
from urllib.parse import urlparse

POSTGRES_VERSION = "16"


def start_postgres_container(db_url: str, data_dir: str):
    import docker

    client = docker.from_env()
    container_name = "engrate-postgres-local"

    parsed = urlparse(db_url)

    if parsed.scheme not in ("postgres", "postgresql"):
        print(
            f"DB_URL uses scheme '{parsed.scheme}', not postgres/postgresql. Skipping."
        )
        return

    user = parsed.username or "postgres"
    password = parsed.password or "postgres"
    db = parsed.path.lstrip("/") or "testdb"
    port = parsed.port or 5432

    # remove old container
    try:
        old = client.containers.get(container_name)
        old.remove(force=True)
    except docker.errors.NotFound:
        pass

    print("Starting container...")
    container = client.containers.run(
        f"postgres:{POSTGRES_VERSION}",
        ports={"5432/tcp": port},
        name=container_name,
        environment={
            "POSTGRES_USER": user,
            "POSTGRES_PASSWORD": password,
            "POSTGRES_DB": db,
        },
        volumes={
            os.path.expanduser(data_dir): {
                "bind": "/var/lib/postgresql/data",
                "mode": "rw",
            }
        },
        detach=True,
    )

    print("Container started. Streaming logs (Ctrl-C to stop)...")

    try:
        for line in container.logs(stream=True, follow=True):
            print(line.decode().rstrip())
    except KeyboardInterrupt:
        print("\nStopping container...")
        container.stop()
        container.remove()
        print("Container removed.")
