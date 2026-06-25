from __future__ import annotations

import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SCENE_JS = ROOT_DIR / "server" / "gizmoapp_server" / "static" / "app" / "scene.js"


class GraphicsDefaultsTests(unittest.TestCase):
    def test_scene_renderer_defaults_to_bitmap_sprites(self) -> None:
        source = SCENE_JS.read_text(encoding="utf-8")

        self.assertIn("function createSpriteTexture", source)
        self.assertIn("this.nodeSprites", source)
        self.assertIn("this.context.drawImage", source)
        self.assertIn("createNodeSprite", source)


if __name__ == "__main__":
    unittest.main()
