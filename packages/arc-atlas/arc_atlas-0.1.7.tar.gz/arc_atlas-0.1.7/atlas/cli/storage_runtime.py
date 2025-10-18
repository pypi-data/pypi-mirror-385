"""Helpers for provisioning PostgreSQL storage through the Atlas CLI."""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

try:
    from importlib import resources as importlib_resources
except ImportError:  
    import importlib_resources  

COMPOSE_TEMPLATE = """version: "3.9"

services:
  postgres:
    image: postgres:15
    container_name: atlas-postgres
    environment:
      POSTGRES_USER: atlas
      POSTGRES_PASSWORD: atlas
      POSTGRES_DB: atlas
    ports:
      - "5433:5432"
    volumes:
      - atlas_pg_data:/var/lib/postgresql/data

volumes:
  atlas_pg_data:
"""

CONTAINER_NAME = "atlas-postgres"
DEFAULT_CONNECTION_URL = "postgresql://atlas:atlas@localhost:5433/atlas"


@dataclass
class InitOptions:
    compose_file: Path
    force: bool = False
    no_start: bool = False
    auto_install: bool = True


@dataclass
class QuitOptions:
    compose_file: Path
    purge: bool = False


def init_storage(options: InitOptions) -> int:
    """Provision Dockerized storage, ensuring Docker, database, and schema are ready."""

    compose_path = options.compose_file.expanduser().resolve()
    compose_path.parent.mkdir(parents=True, exist_ok=True)

    if compose_path.exists() and not options.force:
        print(f"{compose_path} already exists; pass --force to overwrite.", file=sys.stderr)
        return 1

    compose_path.write_text(COMPOSE_TEMPLATE, encoding="utf-8")
    print(f"Wrote Docker Compose file to {compose_path}")

    if options.no_start:
        _print_connection_help(compose_path)
        return 0

    docker_bin = _ensure_docker_installed(auto_install=options.auto_install)
    _ensure_docker_running(docker_bin)
    compose_cmd = _compose_command(docker_bin)

    _handle_port_conflicts()
    _start_postgres(compose_cmd, compose_path)
    _wait_for_postgres_ready(docker_bin)
    _ensure_database_exists(docker_bin)
    _apply_schema(docker_bin)

    print("Atlas storage is ready.")
    _print_connection_help(compose_path)
    return 0


def quit_storage(options: QuitOptions) -> int:
    """Tear down Dockerized storage, optionally removing volumes."""

    compose_path = options.compose_file.expanduser().resolve()
    if not compose_path.exists():
        print(f"{compose_path} does not exist; nothing to tear down.")
        return 0
    docker_bin = shutil.which("docker")
    if docker_bin is None:
        print(
            "Docker is not on PATH. If the container is still running, stop it manually.",
            file=sys.stderr,
        )
        return 1
    compose_cmd = _compose_command(docker_bin)

    down_cmd = compose_cmd + ["-f", str(compose_path), "down"]
    if options.purge:
        down_cmd.append("--volumes")
    try:
        subprocess.run(down_cmd, check=True)
        print("Stopped Atlas storage services.")
    except subprocess.CalledProcessError as exc:  # pragma: no cover - defensive
        print(f"Failed to stop containers: {exc}", file=sys.stderr)
        return 1

    return 0


def _ensure_docker_installed(auto_install: bool = True) -> str:
    docker_bin = shutil.which("docker")
    if docker_bin:
        return docker_bin
    if not auto_install:
        raise SystemExit("Docker is required. Install Docker Desktop or Engine and re-run `atlas init`.")

    print("Docker not found. Attempting to install Docker automatically...")
    system = platform.system()
    installers: list[Sequence[str]] = []

    if system == "Darwin":
        brew = shutil.which("brew")
        if brew:
            installers.append([brew, "install", "--cask", "docker"])
    elif system == "Linux":
        curl = shutil.which("curl")
        if curl:
            installers.append([curl, "-fsSL", "https://get.docker.com", "-o", "/tmp/get-docker.sh"])
        installers.append(["sh", "/tmp/get-docker.sh"])
    elif system == "Windows":
        print("Automatic Docker installation is not supported on Windows. Please install Docker Desktop manually.", file=sys.stderr)
        raise SystemExit(1)

    for cmd in installers:
        try:
            subprocess.run(cmd, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError, PermissionError) as exc:
            print(f"Failed to run {' '.join(cmd)}: {exc}", file=sys.stderr)
            continue

    docker_bin = shutil.which("docker")
    if docker_bin:
        return docker_bin

    raise SystemExit("Unable to install Docker automatically. Install it manually and re-run `atlas init`.")


def _ensure_docker_running(docker_bin: str) -> None:
    if _docker_info(docker_bin):
        return

    system = platform.system()
    attempted_commands: list[Sequence[str]] = []

    if system == "Darwin":
        if shutil.which("open"):
            attempted_commands.append(["open", "-a", "Docker"])
    elif system == "Linux":
        if shutil.which("systemctl"):
            attempted_commands.append(["sudo", "systemctl", "start", "docker"])
        if shutil.which("service"):
            attempted_commands.append(["sudo", "service", "docker", "start"])

    for cmd in attempted_commands:
        try:
            subprocess.run(cmd, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError, PermissionError) as exc:
            print(f"Failed to start Docker using {' '.join(cmd)}: {exc}", file=sys.stderr)

    for _ in range(30):
        if _docker_info(docker_bin):
            return
        time.sleep(2)

    raise SystemExit("Docker daemon is not running. Start Docker Desktop or Engine and retry.")


def _docker_info(docker_bin: str) -> bool:
    try:
        subprocess.run(
            [docker_bin, "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=5,
        )
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _compose_command(docker_bin: str) -> list[str]:
    if shutil.which("docker") == docker_bin or docker_bin == "docker":
        return [docker_bin, "compose"]
    docker_compose = shutil.which("docker-compose")
    if docker_compose:
        return [docker_compose]
    return [docker_bin, "compose"]


def _handle_port_conflicts() -> None:
    try:
        proc = subprocess.run(
            ["lsof", "-i", ":5433"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return

    if proc.returncode == 0 and proc.stdout.strip():
        print(
            "Port 5433 is already in use. Stop the service bound to this port or run atlas init "
            "with a custom compose file that maps a different port.",
            file=sys.stderr,
        )
        raise SystemExit(1)


def _start_postgres(compose_cmd: Sequence[str], compose_path: Path) -> None:
    cmd = list(compose_cmd) + ["-f", str(compose_path), "up", "-d", "postgres"]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Failed to start Postgres via Docker Compose: {exc}") from exc


def _wait_for_postgres_ready(docker_bin: str, timeout: float = 60.0) -> None:
    start = time.monotonic()
    while time.monotonic() - start < timeout:
        try:
            subprocess.run(
                [
                    docker_bin,
                    "exec",
                    CONTAINER_NAME,
                    "pg_isready",
                    "-U",
                    "atlas",
                    "-d",
                    "postgres",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return
        except subprocess.CalledProcessError:
            time.sleep(2)
        except FileNotFoundError as exc:  # pragma: no cover - defensive
            raise SystemExit(f"Failed to check PostgreSQL readiness: {exc}") from exc

    raise SystemExit("PostgreSQL failed to become ready. Check Docker logs with `docker logs atlas-postgres`.")


def _ensure_database_exists(docker_bin: str) -> None:
    check_sql = "SELECT 1 FROM pg_database WHERE datname='atlas';"
    try:
        result = subprocess.run(
            [
                docker_bin,
                "exec",
                CONTAINER_NAME,
                "psql",
                "-U",
                "atlas",
                "-d",
                "postgres",
                "-tAc",
                check_sql,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Failed to verify atlas database existence: {exc}") from exc

    if "1" in result.stdout:
        return

    try:
        subprocess.run(
            [
                docker_bin,
                "exec",
                CONTAINER_NAME,
                "psql",
                "-U",
                "atlas",
                "-d",
                "postgres",
                "-c",
                "CREATE DATABASE atlas;",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Failed to create atlas database: {exc}") from exc


def _apply_schema(docker_bin: str) -> None:
    try:
        schema_resource = importlib_resources.files("atlas.runtime.storage").joinpath("schema.sql")
        schema_sql = schema_resource.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError) as exc:
        raise SystemExit(f"Unable to load schema.sql: {exc}") from exc

    try:
        subprocess.run(
            [
                docker_bin,
                "exec",
                "-i",
                CONTAINER_NAME,
                "psql",
                "-U",
                "atlas",
                "-d",
                "atlas",
                "-v",
                "ON_ERROR_STOP=1",
            ],
            input=schema_sql.encode("utf-8"),
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"Failed to apply schema: {exc}") from exc


def _print_connection_help(compose_path: Path) -> None:
    print()
    print("Configure the Atlas SDK to use storage with:")
    print(f"  export STORAGE__DATABASE_URL={DEFAULT_CONNECTION_URL}")
    print("or set the same value in your Atlas config under storage.database_url.")
    print()
    print("To stop the storage services later, run:")
    print(f"  atlas quit --compose-file {compose_path}")
