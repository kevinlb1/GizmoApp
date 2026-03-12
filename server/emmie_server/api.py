from __future__ import annotations

import re
import sqlite3
from datetime import UTC, datetime

from flask import Flask, current_app, jsonify, request

from .config import scoped_path
from .db import fetch_sample_nodes, get_db, insert_sample_node

HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
SLUG_RE = re.compile(r"^[a-z0-9-]{3,40}$")


def _health_payload() -> dict:
    return {
        "status": "ok",
        "database": "ok",
        "serverTime": datetime.now(UTC).isoformat(),
    }


def _bootstrap_payload() -> dict:
    connection = get_db()
    return {
        "app": {
            "name": current_app.config["APP_NAME"],
            "tagline": current_app.config["APP_TAGLINE"],
            "urlPrefix": current_app.config["URL_PREFIX"],
            "mode": "public",
        },
        "health": _health_payload(),
        "sampleNodes": fetch_sample_nodes(connection),
    }


def _normalize_payload(payload: dict) -> tuple[dict, list[str]]:
    errors: list[str] = []
    cleaned = {
        "slug": str(payload.get("slug", "")).strip(),
        "label": str(payload.get("label", "")).strip(),
        "description": str(payload.get("description", "")).strip() or "Created through the sample API.",
        "accent_color": str(payload.get("accent_color", "#72d1c2")).strip(),
    }

    if not SLUG_RE.match(cleaned["slug"]):
        errors.append("slug must be 3-40 characters of lowercase letters, digits, or hyphens")

    if len(cleaned["label"]) < 2:
        errors.append("label must be at least 2 characters")

    if not HEX_COLOR_RE.match(cleaned["accent_color"]):
        errors.append("accent_color must be a 6-digit hex color like #72d1c2")

    try:
        cleaned["x"] = min(0.92, max(0.08, float(payload.get("x", 0.5))))
        cleaned["y"] = min(0.92, max(0.08, float(payload.get("y", 0.5))))
        cleaned["radius"] = min(0.2, max(0.06, float(payload.get("radius", 0.11))))
    except (TypeError, ValueError):
        errors.append("x, y, and radius must be numeric")

    return cleaned, errors


def register_api_routes(app: Flask) -> None:
    prefix = app.config["URL_PREFIX"]

    @app.get(scoped_path(prefix, "healthz"))
    def healthz():
        return jsonify(_health_payload())

    @app.get(scoped_path(prefix, "api/bootstrap"))
    def bootstrap():
        return jsonify(_bootstrap_payload())

    @app.route(scoped_path(prefix, "api/sample-nodes"), methods=["GET", "POST"])
    def sample_nodes():
        connection = get_db()

        if request.method == "GET":
            return jsonify({"sampleNodes": fetch_sample_nodes(connection)})

        payload = request.get_json(silent=True) or {}
        cleaned, errors = _normalize_payload(payload)
        if errors:
            return jsonify({"errors": errors}), 400

        try:
            record = insert_sample_node(connection, cleaned)
        except sqlite3.IntegrityError:
            return jsonify({"errors": ["slug already exists"]}), 409

        return jsonify({"sampleNode": record}), 201
