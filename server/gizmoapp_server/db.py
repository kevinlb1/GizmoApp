from __future__ import annotations

import sqlite3
from typing import Any

from flask import current_app, g

SCHEMA_MIGRATIONS = {
    1: """
CREATE TABLE IF NOT EXISTS sample_nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    description TEXT NOT NULL,
    accent_color TEXT NOT NULL,
    x REAL NOT NULL,
    y REAL NOT NULL,
    radius REAL NOT NULL DEFAULT 0.11,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
""",
    2: """
CREATE TABLE IF NOT EXISTS app_state (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT '',
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
""",
}

SEED_ROWS = [
    ("compass", "Compass", "Sample navigation node for future interactions.", "#72d1c2", 0.24, 0.38, 0.11),
    ("harbor", "Harbor", "Sample content node anchored to the blank scene.", "#f59a62", 0.57, 0.63, 0.13),
    ("signal", "Signal", "Sample status node seeded from SQLite.", "#f0cf87", 0.77, 0.31, 0.1),
]


def _connect(db_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _ensure_migration_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def _applied_migrations(connection: sqlite3.Connection) -> set[int]:
    rows = connection.execute("SELECT version FROM schema_migrations").fetchall()
    return {int(row["version"]) for row in rows}


def _apply_migrations(connection: sqlite3.Connection) -> None:
    _ensure_migration_table(connection)
    applied = _applied_migrations(connection)

    for version, sql in sorted(SCHEMA_MIGRATIONS.items()):
        if version in applied:
            continue
        connection.executescript(sql)
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
            (version,),
        )


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = _connect(str(current_app.config["DB_PATH"]))
    return g.db


def close_db(_: BaseException | None = None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def initialize_database(config: dict) -> None:
    connection = _connect(str(config["DB_PATH"]))
    try:
        _apply_migrations(connection)
        existing = connection.execute("SELECT COUNT(*) FROM sample_nodes").fetchone()[0]
        if existing == 0:
            connection.executemany(
                """
                INSERT INTO sample_nodes (slug, label, description, accent_color, x, y, radius)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                SEED_ROWS,
            )
        connection.commit()
    finally:
        connection.close()


def fetch_sample_nodes(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT id, slug, label, description, accent_color, x, y, radius, created_at
        FROM sample_nodes
        ORDER BY id
        """
    ).fetchall()
    return [dict(row) for row in rows]


def search_sample_nodes(connection: sqlite3.Connection, query: str, limit: int = 8) -> list[dict[str, Any]]:
    term = query.strip().lower()
    if not term:
        return []

    rows = connection.execute(
        """
        SELECT id, slug, label, description, accent_color, x, y, radius, created_at
        FROM sample_nodes
        WHERE lower(slug) LIKE ?
           OR lower(label) LIKE ?
           OR lower(description) LIKE ?
        ORDER BY id
        LIMIT ?
        """,
        (f"%{term}%", f"%{term}%", f"%{term}%", limit),
    ).fetchall()
    return [dict(row) for row in rows]


def insert_sample_node(connection: sqlite3.Connection, payload: dict[str, Any]) -> dict[str, Any]:
    cursor = connection.execute(
        """
        INSERT INTO sample_nodes (slug, label, description, accent_color, x, y, radius)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["slug"],
            payload["label"],
            payload["description"],
            payload["accent_color"],
            payload["x"],
            payload["y"],
            payload["radius"],
        ),
    )
    connection.commit()

    row = connection.execute(
        """
        SELECT id, slug, label, description, accent_color, x, y, radius, created_at
        FROM sample_nodes
        WHERE id = ?
        """,
        (cursor.lastrowid,),
    ).fetchone()
    return dict(row)


def database_summary(config: dict) -> dict[str, Any]:
    connection = _connect(str(config["DB_PATH"]))
    try:
        count = connection.execute("SELECT COUNT(*) FROM sample_nodes").fetchone()[0]
        state_count = connection.execute("SELECT COUNT(*) FROM app_state").fetchone()[0]
        event_count = connection.execute("SELECT COUNT(*) FROM app_events").fetchone()[0]
        schema_version = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()[0]
    finally:
        connection.close()

    return {
        "database_path": str(config["DB_PATH"]),
        "sample_node_count": count,
        "app_state_count": state_count,
        "app_event_count": event_count,
        "schema_version": schema_version,
    }
