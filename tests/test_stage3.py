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

class TestStage3Maintenance(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.env = {
            "GETRON_ROOT": os.path.join(self.test_dir, "tetron_root"),
            "GETRON_MOCK_DOWNLOAD": "1"
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_doctor_output_formatting(self):
        run_cmd(f"sh {GETRON_BIN} install 1.0.0", env=self.env)
        rc, out, err = run_cmd(f"sh {GETRON_BIN} doctor", env=self.env)
        self.assertEqual(rc, 0)
        self.assertIn("Getron Diagnostic Report", out)
        self.assertIn("Active Version:", out)
        self.assertIn("1.0.0", out)

    def test_repair_missing_symlink(self):
        run_cmd(f"sh {GETRON_BIN} install 1.0.0", env=self.env)
        root_dir = self.env["GETRON_ROOT"]
        active_link = os.path.join(root_dir, "active")
        
        # Break active link manually
        os.remove(active_link)
        self.assertFalse(os.path.exists(active_link))

        # Run repair
        rc, out, err = run_cmd(f"sh {GETRON_BIN} repair", env=self.env)
        self.assertEqual(rc, 0, f"Repair failed: {err}")
        self.assertIn("Repaired active symlink", out)
        self.assertTrue(os.path.exists(active_link))
        self.assertEqual(os.path.realpath(active_link), os.path.realpath(os.path.join(root_dir, "versions", "1.0.0")))

    def test_garbage_collection_preserves_active_and_rollback(self):
        # Install 1.0.0, 1.1.0, 1.2.0, 1.3.0
        run_cmd(f"sh {GETRON_BIN} install 1.0.0", env=self.env)
        run_cmd(f"sh {GETRON_BIN} install 1.1.0", env=self.env)
        run_cmd(f"sh {GETRON_BIN} install 1.2.0", env=self.env)
        run_cmd(f"sh {GETRON_BIN} install 1.3.0", env=self.env)

        root_dir = self.env["GETRON_ROOT"]
        versions_dir = os.path.join(root_dir, "versions")
        
        # Currently 1.3.0 is active, 1.2.0 is rollback
        # 1.0.0 and 1.1.0 are unused
        rc, out, err = run_cmd(f"sh {GETRON_BIN} gc", env=self.env)
        self.assertEqual(rc, 0, f"GC failed: {err}")

        installed = os.listdir(versions_dir)
        self.assertIn("1.3.0", installed)  # active
        self.assertIn("1.2.0", installed)  # rollback
        self.assertNotIn("1.0.0", installed)
        self.assertNotIn("1.1.0", installed)

    def test_uninstall_refuses_active_version(self):
        run_cmd(f"sh {GETRON_BIN} install 1.0.0", env=self.env)
        rc, out, err = run_cmd(f"sh {GETRON_BIN} uninstall 1.0.0", env=self.env)
        self.assertNotEqual(rc, 0)
        self.assertIn("Cannot uninstall active version", err)

if __name__ == "__main__":
    unittest.main()
