import os
import shutil
import tempfile
import unittest
import subprocess

GETRON_BIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "getron"))

def run_cmd(cmd, cwd=None, env=None):
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, env=merged_env)
    return res.returncode, res.stdout, res.stderr

class TestStage2Installation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.env = {
            "GETRON_ROOT": os.path.join(self.test_dir, "tetron_root"),
            "GETRON_MOCK_DOWNLOAD": "1"
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_directory_layout_creation(self):
        rc, out, err = run_cmd(f"sh {GETRON_BIN} doctor", env=self.env)
        self.assertEqual(rc, 0, f"Doctor failed: {err}")
        root_dir = self.env["GETRON_ROOT"]
        self.assertTrue(os.path.exists(os.path.join(root_dir, "versions")))
        self.assertTrue(os.path.exists(os.path.join(root_dir, "staging")))

    def test_install_and_atomic_activation(self):
        rc, out, err = run_cmd(f"sh {GETRON_BIN} install 1.0.0", env=self.env)
        self.assertEqual(rc, 0, f"Install failed: {err}")
        
        root_dir = self.env["GETRON_ROOT"]
        ver_dir = os.path.join(root_dir, "versions", "1.0.0")
        self.assertTrue(os.path.exists(ver_dir))
        self.assertTrue(os.path.exists(os.path.join(ver_dir, "tetron")))
        self.assertTrue(os.path.exists(os.path.join(ver_dir, "manifest.toml")))

        # Check active symlink
        active_link = os.path.join(root_dir, "active")
        self.assertTrue(os.path.islink(active_link))
        self.assertEqual(os.path.realpath(active_link), os.path.realpath(ver_dir))

    def test_version_switching_and_rollback_pointer(self):
        # Install 1.0.0 first
        rc1, _, err1 = run_cmd(f"sh {GETRON_BIN} install 1.0.0", env=self.env)
        self.assertEqual(rc1, 0, f"Install 1.0.0 failed: {err1}")
        # Install 1.1.0 second
        rc, out, err = run_cmd(f"sh {GETRON_BIN} install 1.1.0", env=self.env)
        self.assertEqual(rc, 0, f"Install 1.1.0 failed: {err}")


        root_dir = self.env["GETRON_ROOT"]
        active_link = os.path.join(root_dir, "active")
        rollback_link = os.path.join(root_dir, "rollback")

        self.assertEqual(os.path.realpath(active_link), os.path.realpath(os.path.join(root_dir, "versions", "1.1.0")))
        self.assertEqual(os.path.realpath(rollback_link), os.path.realpath(os.path.join(root_dir, "versions", "1.0.0")))

        # Use rollback command
        rc, out, err = run_cmd(f"sh {GETRON_BIN} rollback", env=self.env)
        self.assertEqual(rc, 0, f"Rollback failed: {err}")
        self.assertEqual(os.path.realpath(active_link), os.path.realpath(os.path.join(root_dir, "versions", "1.0.0")))

    def test_use_command(self):
        run_cmd(f"sh {GETRON_BIN} install 1.0.0", env=self.env)
        run_cmd(f"sh {GETRON_BIN} install 1.1.0", env=self.env)

        rc, out, err = run_cmd(f"sh {GETRON_BIN} use 1.0.0", env=self.env)
        self.assertEqual(rc, 0, f"Use command failed: {err}")
        root_dir = self.env["GETRON_ROOT"]
        active_link = os.path.join(root_dir, "active")
        self.assertEqual(os.path.realpath(active_link), os.path.realpath(os.path.join(root_dir, "versions", "1.0.0")))

    def test_health_check_failure_triggers_automatic_rollback(self):
        run_cmd(f"sh {GETRON_BIN} install 1.0.0", env=self.env)
        
        # Attempt installing broken version 2.0.0 with simulated health check failure
        env_broken = self.env.copy()
        env_broken["GETRON_MOCK_HEALTH_FAIL"] = "1"
        rc, out, err = run_cmd(f"sh {GETRON_BIN} install 2.0.0", env=env_broken)
        self.assertNotEqual(rc, 0)
        self.assertIn("health check failed", err.lower())

        # Verify active link rolled back to 1.0.0
        root_dir = self.env["GETRON_ROOT"]
        active_link = os.path.join(root_dir, "active")
        self.assertEqual(os.path.realpath(active_link), os.path.realpath(os.path.join(root_dir, "versions", "1.0.0")))

if __name__ == "__main__":
    unittest.main()
