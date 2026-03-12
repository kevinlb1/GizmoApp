from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from server.emmie_server import create_app


class EmmieAppTestCase(unittest.TestCase):
    def make_app(self, url_prefix: str = "", shell_variant: str = "graphical"):
        self.temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(self.temp_dir.name) / "test.sqlite3"
        app = create_app(
            {
                "TESTING": True,
                "DB_PATH": db_path,
                "URL_PREFIX": url_prefix,
                "SECRET_KEY": "test-secret",
            },
            shell_variant=shell_variant,
        )
        return app

    def tearDown(self):
        temp_dir = getattr(self, "temp_dir", None)
        if temp_dir is not None:
            temp_dir.cleanup()

    def test_bootstrap_endpoint_returns_seed_data(self):
        app = self.make_app("/AI100")
        client = app.test_client()

        response = client.get("/AI100/api/bootstrap")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["app"]["urlPrefix"], "/AI100")
        self.assertEqual(payload["app"]["shell"], "graphical")
        self.assertGreaterEqual(len(payload["sampleNodes"]), 3)

    def test_manifest_uses_configured_prefix(self):
        app = self.make_app("/AI100")
        client = app.test_client()

        response = client.get("/AI100/manifest.webmanifest")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["scope"], "/AI100/")
        self.assertEqual(payload["start_url"], "/AI100/")

    def test_can_insert_sample_node(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.post(
            "/api/sample-nodes",
            json={
                "slug": "new-node",
                "label": "New Node",
                "description": "Created by the test suite.",
                "accent_color": "#72d1c2",
                "x": 0.6,
                "y": 0.4,
                "radius": 0.12,
            },
        )

        payload = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(payload["sampleNode"]["slug"], "new-node")

    def test_graphical_index_renders_without_prefix(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.get("/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Interactive graphical scene", html)

    def test_text_index_renders_without_prefix(self):
        app = self.make_app("", shell_variant="text")
        client = app.test_client()

        response = client.get("/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Standard app layout, no product logic yet", html)


if __name__ == "__main__":
    unittest.main()
