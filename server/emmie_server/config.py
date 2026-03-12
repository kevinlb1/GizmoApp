from __future__ import annotations

import os
from pathlib import Path


def normalize_url_prefix(value: str | None) -> str:
    if value is None:
        return ""

    trimmed = value.strip()
    if trimmed in {"", "/"}:
        return ""

    if not trimmed.startswith("/"):
        trimmed = f"/{trimmed}"

    return trimmed.rstrip("/")


def load_settings() -> dict:
    repo_root = Path(__file__).resolve().parents[2]
    data_dir = repo_root / "var" / "data"
    log_dir = repo_root / "var" / "log"
    static_dir = Path(__file__).resolve().parent / "static"
    url_prefix = normalize_url_prefix(os.getenv("EMMIE_URL_PREFIX", ""))
    db_path = Path(os.getenv("EMMIE_DB_PATH", data_dir / "emmie.sqlite3")).expanduser()

    data_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    return {
        "APP_NAME": os.getenv("EMMIE_APP_NAME", "Emmie"),
        "APP_TAGLINE": "Blank graphical webapp template",
        "URL_PREFIX": url_prefix,
        "DB_PATH": db_path,
        "REPO_ROOT": repo_root,
        "STATIC_ROOT": static_dir,
        "SECRET_KEY": os.getenv("EMMIE_SECRET_KEY", "dev-only-secret"),
        "THEME_COLOR": "#132033",
        "BACKGROUND_COLOR": "#132033",
        "PWA_SHORT_NAME": "Emmie",
        "ADMIN_NOTES": [
            "Anonymous/public access only in the initial scaffold.",
            "Frontend is build-free by design to keep deploys easy.",
            "Touch-first layout takes priority over desktop polish.",
        ],
    }


def scoped_path(url_prefix: str, path: str = "") -> str:
    cleaned = path.lstrip("/")
    base = f"{url_prefix}/" if url_prefix else "/"
    return f"{base}{cleaned}" if cleaned else base

