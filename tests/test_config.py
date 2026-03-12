from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from server.gizmoapp_server.config import load_settings


class ConfigTestCase(unittest.TestCase):
    def test_load_settings_reads_git_tracked_deploy_env(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            deploy_dir = repo_root / "deploy"
            deploy_dir.mkdir()
            (deploy_dir / "app.env").write_text(
                "GIZMOAPP_SHELL=text\n",
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("GIZMOAPP_SHELL", None)
                settings = load_settings(repo_root=repo_root)

            self.assertEqual(settings["APP_SHELL"], "text")

    def test_load_settings_reads_repo_root_dotenv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / ".env").write_text(
                "\n".join(
                    [
                        'GIZMOAPP_APP_NAME="Derived Demo"',
                        "GIZMOAPP_URL_PREFIX=/demo-app",
                        "GIZMOAPP_SHELL=text",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop("GIZMOAPP_APP_NAME", None)
                os.environ.pop("GIZMOAPP_URL_PREFIX", None)
                os.environ.pop("GIZMOAPP_SHELL", None)
                settings = load_settings(repo_root=repo_root)

            self.assertEqual(settings["APP_NAME"], "Derived Demo")
            self.assertEqual(settings["URL_PREFIX"], "/demo-app")
            self.assertEqual(settings["APP_SHELL"], "text")

    def test_process_env_overrides_repo_root_dotenv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            deploy_dir = repo_root / "deploy"
            deploy_dir.mkdir()
            (deploy_dir / "app.env").write_text(
                "GIZMOAPP_SHELL=text\n",
                encoding="utf-8",
            )
            (repo_root / ".env").write_text(
                "GIZMOAPP_URL_PREFIX=/from-dotenv\n",
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {"GIZMOAPP_URL_PREFIX": "/from-environ", "GIZMOAPP_SHELL": "graphical"},
                clear=False,
            ):
                settings = load_settings(repo_root=repo_root)

            self.assertEqual(settings["URL_PREFIX"], "/from-environ")
            self.assertEqual(settings["APP_SHELL"], "graphical")


if __name__ == "__main__":
    unittest.main()
