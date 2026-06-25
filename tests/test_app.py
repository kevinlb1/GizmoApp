from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from server.gizmoapp_server import create_app


class GizmoAppTestCase(unittest.TestCase):
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
        app = self.make_app("/demo-app")
        client = app.test_client()

        response = client.get("/demo-app/api/bootstrap")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["app"]["urlPrefix"], "/demo-app")
        self.assertEqual(payload["app"]["shell"], "graphical")
        self.assertEqual(payload["capabilitySummary"]["defaultLocation"]["label"], "UBC Vancouver")
        self.assertGreaterEqual(len(payload["sampleNodes"]), 3)

    def test_manifest_uses_configured_prefix(self):
        app = self.make_app("/demo-app")
        client = app.test_client()

        response = client.get("/demo-app/manifest.webmanifest")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["scope"], "/demo-app/")
        self.assertEqual(payload["start_url"], "/demo-app/")

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

    def test_capabilities_include_optional_ml_and_openstreetmap_defaults(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.get("/api/capabilities")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        slugs = {capability["slug"] for capability in payload["capabilities"]}
        self.assertIn("machine-learning", slugs)
        self.assertIn("mapping", slugs)
        self.assertEqual(payload["mapping"]["provider"], "openstreetmap")
        self.assertEqual(payload["defaultLocation"]["label"], "UBC Vancouver")

    def test_search_endpoint_queries_persistent_records(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.get("/api/search?q=compass")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["source"], "sqlite")
        self.assertEqual(payload["results"][0]["slug"], "compass")

    def test_audio_analysis_endpoint_summarizes_samples(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.post(
            "/api/audio/analyze",
            json={"samples": [0, 0.5, -0.5, 0], "sampleRate": 4},
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["sampleCount"], 4)
        self.assertAlmostEqual(payload["durationSeconds"], 1.0)

    def test_optimization_endpoint_orders_route(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.post(
            "/api/optimize/route",
            json={"points": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 1, "y": 0}]},
        )
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["orderedIds"], ["a", "b"])

    def test_map_default_endpoint_uses_ubc_vancouver(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.get("/api/map/default")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["provider"], "openstreetmap")
        self.assertEqual(payload["defaultLocation"]["label"], "UBC Vancouver")

    def test_ml_status_reports_optional_dependency(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.get("/api/ml/status")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["package"], "scikit-learn")
        self.assertIn("available", payload)

    def test_graphical_index_renders_without_prefix(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.get("/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Graphical canvas", html)
        self.assertIn("base.css", html)

    def test_text_index_renders_without_prefix(self):
        app = self.make_app("", shell_variant="text")
        client = app.test_client()

        response = client.get("/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Text workspace", html)
        self.assertIn("base.css", html)


if __name__ == "__main__":
    unittest.main()
