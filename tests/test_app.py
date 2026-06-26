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

    def test_bootstrap_endpoint_returns_blank_app_metadata(self):
        app = self.make_app("/demo-app")
        client = app.test_client()

        response = client.get("/demo-app/api/bootstrap")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["app"]["shell"], "graphical")
        self.assertNotIn("urlPrefix", payload["app"])
        self.assertNotIn("capabilitySummary", payload)
        self.assertNotIn("sampleNodes", payload)
        self.assertNotIn("database", payload["health"])

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

    def test_capabilities_include_optional_ml_and_mapping_without_global_location_default(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.get("/api/capabilities")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        slugs = {capability["slug"] for capability in payload["capabilities"]}
        self.assertIn("machine-learning", slugs)
        self.assertIn("mapping", slugs)
        self.assertNotIn("mapping", payload)
        self.assertNotIn("defaultLocation", payload)

    def test_search_endpoint_queries_persistent_records(self):
        app = self.make_app("")
        client = app.test_client()

        client.post(
            "/api/sample-nodes",
            json={
                "slug": "compass",
                "label": "Compass",
                "description": "Inserted by the test suite.",
                "accent_color": "#72d1c2",
                "x": 0.25,
                "y": 0.4,
                "radius": 0.1,
            },
        )

        response = client.get("/api/search?q=compass")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["source"], "sqlite")
        self.assertEqual(payload["results"][0]["slug"], "compass")

    def test_sample_node_api_starts_empty(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.get("/api/sample-nodes")
        payload = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["sampleNodes"], [])

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
        self.assertIn("Blank graphical workspace", html)
        self.assertIn("template-chrome", html)
        self.assertNotIn("app-topbar", html)
        self.assertNotIn("brand-mark", html)
        self.assertIn("base.css", html)
        self.assertNotIn("UBC Vancouver", html)
        self.assertNotIn("Map", html)
        self.assertNotIn("DB", html)

    def test_text_index_renders_without_prefix(self):
        app = self.make_app("", shell_variant="text")
        client = app.test_client()

        response = client.get("/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Text workspace", html)
        self.assertIn("template-chrome", html)
        self.assertNotIn("app-topbar", html)
        self.assertNotIn("brand-mark", html)
        self.assertIn("base.css", html)
        self.assertNotIn("UBC Vancouver", html)
        self.assertNotIn("Database", html)
        self.assertNotIn("Location", html)

    def test_admin_keeps_header_and_diagnostics(self):
        app = self.make_app("")
        client = app.test_client()

        response = client.get("/admin/")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("app-topbar", html)
        self.assertIn("brand-mark", html)
        self.assertIn("Database", html)


if __name__ == "__main__":
    unittest.main()
