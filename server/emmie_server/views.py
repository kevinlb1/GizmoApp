from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from flask import Flask, Response, abort, current_app, render_template, send_from_directory

from .config import scoped_path
from .db import database_summary, fetch_sample_nodes, get_db


def _root_path() -> str:
    return scoped_path(current_app.config["URL_PREFIX"])


def _client_config() -> dict:
    prefix = current_app.config["URL_PREFIX"]
    return {
        "appName": current_app.config["APP_NAME"],
        "tagline": current_app.config["APP_TAGLINE"],
        "rootPath": scoped_path(prefix),
        "apiBase": scoped_path(prefix, "api"),
        "adminUrl": scoped_path(prefix, "admin/"),
        "healthUrl": scoped_path(prefix, "healthz"),
        "serviceWorkerUrl": scoped_path(prefix, "sw.js"),
        "manifestUrl": scoped_path(prefix, "manifest.webmanifest"),
        "urlPrefix": prefix,
    }


def _manifest_payload() -> dict:
    root_path = _root_path()
    return {
        "name": current_app.config["APP_NAME"],
        "short_name": current_app.config["PWA_SHORT_NAME"],
        "description": current_app.config["APP_TAGLINE"],
        "start_url": root_path,
        "scope": root_path,
        "display": "standalone",
        "background_color": current_app.config["BACKGROUND_COLOR"],
        "theme_color": current_app.config["THEME_COLOR"],
        "orientation": "any",
        "icons": [
            {
                "src": scoped_path(current_app.config["URL_PREFIX"], "icons/icon-192.png"),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": scoped_path(current_app.config["URL_PREFIX"], "icons/icon-512.png"),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ],
    }


def _static_file_response(folder: str, asset_path: str):
    root = Path(current_app.config["STATIC_ROOT"]) / folder
    return send_from_directory(root, asset_path)


def register_page_routes(app: Flask) -> None:
    prefix = app.config["URL_PREFIX"]
    root_path = scoped_path(prefix)
    reserved_top_level = {"api", "app", "icons", "admin", "healthz", "manifest.webmanifest", "sw.js", "favicon.ico"}

    @app.get(scoped_path(prefix, "app/<path:asset_path>"))
    def app_assets(asset_path: str):
        return _static_file_response("app", asset_path)

    @app.get(scoped_path(prefix, "icons/<path:asset_path>"))
    def icon_assets(asset_path: str):
        return _static_file_response("icons", asset_path)

    @app.get(scoped_path(prefix, "sw.js"))
    def service_worker():
        response = _static_file_response("app", "sw.js")
        response.headers["Content-Type"] = "application/javascript; charset=utf-8"
        response.headers["Cache-Control"] = "no-cache"
        return response

    @app.get(scoped_path(prefix, "favicon.ico"))
    def favicon():
        return _static_file_response("icons", "icon-192.png")

    @app.get(scoped_path(prefix, "manifest.webmanifest"))
    def manifest():
        return Response(
            json.dumps(_manifest_payload(), separators=(",", ":")),
            mimetype="application/manifest+json",
        )

    @app.get(scoped_path(prefix, "admin/"))
    def admin_page():
        summary = database_summary(current_app.config)
        sample_nodes = fetch_sample_nodes(get_db())
        return render_template(
            "admin.html",
            app_name=current_app.config["APP_NAME"],
            root_path=root_path,
            now=datetime.now(UTC).isoformat(),
            summary=summary,
            sample_nodes=sample_nodes,
            notes=current_app.config["ADMIN_NOTES"],
        )

    @app.route(root_path, defaults={"path": ""})
    @app.route(f"{root_path}<path:path>")
    def index(path: str):
        if path and path.split("/", 1)[0] in reserved_top_level:
            abort(404)

        return render_template(
            "index.html",
            app_name=current_app.config["APP_NAME"],
            app_tagline=current_app.config["APP_TAGLINE"],
            base_href=root_path,
            asset_base=scoped_path(prefix, "app/"),
            admin_url=scoped_path(prefix, "admin/"),
            manifest_url=scoped_path(prefix, "manifest.webmanifest"),
            icon_url=scoped_path(prefix, "icons/icon-192.png"),
            apple_touch_icon_url=scoped_path(prefix, "icons/apple-touch-icon.png"),
            theme_color=current_app.config["THEME_COLOR"],
            client_config=_client_config(),
        )
