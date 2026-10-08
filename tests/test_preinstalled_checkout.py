from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PreinstalledCheckoutTests(unittest.TestCase):
    def run_installer(self, *, preinstalled, readonly=True):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            checkout = root / "checkout"
            scripts = checkout / "scripts"
            scripts.mkdir(parents=True)
            for name in ("install_checkout.sh", "envfile.py", "require_explicit_approval.sh"):
                shutil.copyfile(ROOT / "scripts" / name, scripts / name)
            (checkout / ".env.example").write_text("GIZMOAPP_SHELL=text\n")
            runtime = root / "runtime"
            binary = runtime / "bin" / "python"
            binary.parent.mkdir(parents=True)
            binary.write_text("#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$DEPENDENCY_TEST_LOG\"\n")
            binary.chmod(0o555)
            runtime.chmod(0o555 if readonly else 0o755)
            (checkout / ".venv").symlink_to(runtime)
            log = root / "calls"
            environment = {**os.environ, "ALLOW_NETWORK_INSTALL": "1",
                           "CODINGWORKSPACE_PREINSTALLED_DEPENDENCIES": str(preinstalled),
                           "DEPENDENCY_TEST_LOG": str(log)}
            result = subprocess.run(["bash", str(scripts / "install_checkout.sh")],
                                    env=environment, text=True, capture_output=True)
            calls = log.read_text() if log.exists() else ""
            runtime.chmod(0o755)
            return result, calls

    def test_shared_dependencies_skip_pip_but_initialize_project(self):
        result, calls = self.run_installer(preinstalled=1)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("pip install", calls)
        self.assertIn("init-db", calls)
        self.assertIn("describe --shell text", calls)

    def test_preinstalled_flag_refuses_writable_environment(self):
        result, calls = self.run_installer(preinstalled=1, readonly=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("read-only managed virtualenv", result.stderr)
        self.assertEqual(calls, "")

    def test_ordinary_checkout_still_installs_requirements(self):
        result, calls = self.run_installer(preinstalled=0, readonly=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("-m pip install -r", calls)
        self.assertIn("init-db", calls)
