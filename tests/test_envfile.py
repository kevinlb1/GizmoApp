from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
ENVFILE = ROOT_DIR / "scripts" / "envfile.py"


class EnvfileTestCase(unittest.TestCase):
    def test_set_and_get_round_trip_with_spaces(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("GIZMOAPP_PORT=8100\n", encoding="utf-8")

            subprocess.run(
                [sys.executable, str(ENVFILE), "set", str(env_path), "GIZMOAPP_APP_NAME", "Demo App"],
                check=True,
            )

            stored_text = env_path.read_text(encoding="utf-8")
            self.assertIn('GIZMOAPP_APP_NAME="Demo App"', stored_text)

            result = subprocess.run(
                [sys.executable, str(ENVFILE), "get", str(env_path), "GIZMOAPP_APP_NAME"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.stdout, "Demo App")

    def test_load_outputs_nul_delimited_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                '\n'.join(
                    [
                        '# comment',
                        'GIZMOAPP_APP_NAME="Demo App"',
                        'GIZMOAPP_PORT=8100',
                    ]
                )
                + '\n',
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(ENVFILE), "load", str(env_path)],
                check=True,
                capture_output=True,
            )

            self.assertEqual(
                result.stdout.split(b"\0"),
                [b"GIZMOAPP_APP_NAME=Demo App", b"GIZMOAPP_PORT=8100", b""],
            )


if __name__ == "__main__":
    unittest.main()
