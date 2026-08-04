import os
import shutil
import tempfile
import unittest
import subprocess

GETRON_BIN = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "getron"))
INSTALL_SH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "install.sh"))

def run_cmd(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout, res.stderr

class TestStage1Bootstrap(unittest.TestCase):
    def test_posix_sh_syntax(self):
        rc, _, err = run_cmd(f"sh -n {GETRON_BIN}")
        self.assertEqual(rc, 0, f"getron syntax error: {err}")

        rc, _, err = run_cmd(f"sh -n {INSTALL_SH}")
        self.assertEqual(rc, 0, f"install.sh syntax error: {err}")

    def test_help_command(self):
        rc, out, _ = run_cmd(f"sh {GETRON_BIN} help")
        self.assertEqual(rc, 0)
        self.assertIn("Getron: Tetron Installation and Version Management", out)
        self.assertIn("Usage: getron <command>", out)

    def test_flag_help_command(self):
        rc, out, _ = run_cmd(f"sh {GETRON_BIN} --help")
        self.assertEqual(rc, 0)
        self.assertIn("Getron: Tetron Installation and Version Management", out)

    def test_unknown_subcommand(self):
        rc, out, err = run_cmd(f"sh {GETRON_BIN} invalid_cmd")
        self.assertEqual(rc, 1)
        self.assertIn("Error: unknown command 'invalid_cmd'", err)
        self.assertIn("Run 'getron --help' for usage", err)

    def test_subcommand_stubs(self):
        for cmd in ["install", "update", "versions", "use 1.0.0", "rollback", "doctor", "repair", "gc", "uninstall 1.0.0"]:
            rc, out, err = run_cmd(f"sh {GETRON_BIN} {cmd}")
            self.assertEqual(rc, 0, f"Command '{cmd}' failed with code {rc}: {err}")
            base_cmd = cmd.split()[0]
            self.assertTrue(f"Executing {base_cmd}" in out or f"Command '{base_cmd}'" in out)


    def test_install_script_bootstrap_dry_run(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            env_prefix = f"GETRON_INSTALL_DIR={tmp_dir}"
            rc, out, err = run_cmd(f"{env_prefix} sh {INSTALL_SH}")
            self.assertEqual(rc, 0, f"install.sh failed: {err}")
            installed_path = os.path.join(tmp_dir, "getron")
            self.assertTrue(os.path.exists(installed_path))
            self.assertTrue(os.access(installed_path, os.X_OK))
        finally:
            shutil.rmtree(tmp_dir)

if __name__ == "__main__":
    unittest.main()

