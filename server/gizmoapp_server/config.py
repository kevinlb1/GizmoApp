from __future__ import annotations

import os
import re
import shlex
from pathlib import Path

from .shells import DEFAULT_SHELL, available_shells, shell_settings

ASSIGNMENT_RE = re.compile(
    r"^\s*(?:export\s+)?(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<raw>.*)$"
)


def parse_env_assignment(line: str, line_number: int) -> tuple[str, str] | None:
    match = ASSIGNMENT_RE.match(line)
    if match is None:
        return None

    raw_value = match.group("raw").strip()
    if raw_value == "":
        return match.group("key"), ""

    try:
        parts = shlex.split(raw_value, posix=True)
    except ValueError as exc:
        raise RuntimeError(f"Invalid env syntax on line {line_number}: {exc}") from exc

    if len(parts) != 1:
        raise RuntimeError(
            f"Invalid env syntax on line {line_number}: expected one value token."
        )

    return match.group("key"), parts[0]


def load_local_env(env_path: Path, environ: dict[str, str] | None = None) -> None:
    if not env_path.exists():
        return

    target = environ if environ is not None else os.environ
    for index, line in enumerate(env_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        assignment = parse_env_assignment(line, index)
        if assignment is None:
            continue

        key, value = assignment
        target.setdefault(key, value)


def normalize_url_prefix(value: str | None) -> str:
    if value is None:
        return ""

    trimmed = value.strip()
    if trimmed in {"", "/"}:
        return ""

    if not trimmed.startswith("/"):
        trimmed = f"/{trimmed}"

    return trimmed.rstrip("/")


def load_settings(shell_variant: str | None = None, repo_root: Path | None = None) -> dict:
    repo_root = repo_root or Path(__file__).resolve().parents[2]
    load_local_env(repo_root / "deploy" / "app.env")
    load_local_env(repo_root / ".env")
    data_dir = repo_root / "var" / "data"
    log_dir = repo_root / "var" / "log"
    static_dir = Path(__file__).resolve().parent / "static"
    url_prefix = normalize_url_prefix(os.getenv("GIZMOAPP_URL_PREFIX", ""))
    db_path = Path(os.getenv("GIZMOAPP_DB_PATH", data_dir / "gizmoapp.sqlite3")).expanduser()

    data_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    settings = {
        "APP_NAME": os.getenv("GIZMOAPP_APP_NAME", "GizmoApp"),
        "APP_TAGLINE": "Blank webapp template",
        "URL_PREFIX": url_prefix,
        "DB_PATH": db_path,
        "REPO_ROOT": repo_root,
        "STATIC_ROOT": static_dir,
        "SECRET_KEY": os.getenv("GIZMOAPP_SECRET_KEY", "dev-only-secret"),
        "AVAILABLE_SHELLS": available_shells(),
        "PWA_SHORT_NAME": "GizmoApp",
        "ADMIN_NOTES": [
            "Anonymous/public access only in the initial scaffold.",
            "Frontend is build-free by design to keep deploys easy.",
            "Touch-first layout takes priority over desktop polish.",
            "The project ships with both graphical and text-first frontend shells.",
            "Select the active shell through GIZMOAPP_SHELL or an explicit WSGI entry point.",
        ],
    }
    settings.update(shell_settings(shell_variant or os.getenv("GIZMOAPP_SHELL", DEFAULT_SHELL)))
    return settings


def scoped_path(url_prefix: str, path: str = "") -> str:
    cleaned = path.lstrip("/")
    base = f"{url_prefix}/" if url_prefix else "/"
    return f"{base}{cleaned}" if cleaned else base
