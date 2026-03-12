from __future__ import annotations

DEFAULT_SHELL = "graphical"

SHELL_DEFINITIONS = {
    "graphical": {
        "slug": "graphical",
        "label": "Graphical",
        "description": "Touch-first graphical shell with a canvas scene ready for sprites, animation, or future 3D.",
        "template": "index.html",
        "asset_subpath": "app/",
        "theme_color": "#132033",
        "background_color": "#132033",
    },
    "text": {
        "slug": "text",
        "label": "Text",
        "description": "Standard text-first shell with dashboard panels, lists, and forms ready for application flows.",
        "template": "index_text.html",
        "asset_subpath": "app/text/",
        "theme_color": "#15443f",
        "background_color": "#f4efe4",
    },
}


def get_shell_definition(shell_variant: str | None) -> dict:
    variant = (shell_variant or DEFAULT_SHELL).strip().lower()
    return SHELL_DEFINITIONS.get(variant, SHELL_DEFINITIONS[DEFAULT_SHELL]).copy()


def shell_settings(shell_variant: str | None) -> dict:
    definition = get_shell_definition(shell_variant)
    return {
        "APP_SHELL": definition["slug"],
        "APP_SHELL_LABEL": definition["label"],
        "APP_SHELL_DESCRIPTION": definition["description"],
        "APP_SHELL_TEMPLATE": definition["template"],
        "APP_SHELL_ASSET_SUBPATH": definition["asset_subpath"],
        "THEME_COLOR": definition["theme_color"],
        "BACKGROUND_COLOR": definition["background_color"],
    }


def available_shells() -> list[dict]:
    return [
        {
            "slug": definition["slug"],
            "label": definition["label"],
            "description": definition["description"],
        }
        for definition in SHELL_DEFINITIONS.values()
    ]
