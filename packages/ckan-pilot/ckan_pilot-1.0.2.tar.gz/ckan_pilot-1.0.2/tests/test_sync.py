import shutil
import subprocess as sp
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from ckan_pilot.root import cli


class TestSyncCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        Path("/tmp/ckan-pilot/testprj").mkdir(parents=True)
        Path("/tmp/ckan-pilot/testprj/.ckan-pilot").touch()

    def __init_project(self):
        env_runner = CliRunner()
        setup_test_env_options = [
            "init",
            "-n",
            "test",
            "--project-description",
            "Test description",
            "--ckan-version",
            "2.11.3",
            "-p",
            "3.10.16",
            "/tmp/ckan-pilot/testdir",
        ]
        env_runner.invoke(cli, setup_test_env_options)

    def test_sync_success(self):
        self.__init_project()
        shutil.rmtree("/tmp/ckan-pilot/testdir/.venv")

        # Sync the project
        test_sync_options = ["-d", "/tmp/ckan-pilot/testdir", "sync"]
        result = self.runner.invoke(cli, test_sync_options)
        self.assertIn("synchronized", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_sync_on_synced_project(self):
        self.__init_project()

        # Sync the project
        test_sync_options = ["-d", "/tmp/ckan-pilot/testdir", "sync"]
        result = self.runner.invoke(cli, test_sync_options)
        self.assertIn("synchronized", result.output)
        self.assertEqual(result.exit_code, 0)

    def test_sync_is_not_ckan_pilot_project(self):
        test_sync_options = ["-d", "/tmp", "sync"]
        result = self.runner.invoke(cli, test_sync_options)
        self.assertIn("not a valid ckan-pilot project", result.output)
        self.assertEqual(result.exit_code, 1)

    @patch.dict("os.environ", {"PATH": "/some/path"}, clear=True)
    def test_sync_tools_missing(self):
        test_sync_options = ["-d", "/tmp/ckan-pilot/testprj", "sync"]
        result = self.runner.invoke(cli, test_sync_options)
        self.assertIn("not found", result.output)
        self.assertEqual(result.exit_code, 1)

    @patch(
        "ckan_pilot.helpers.subproc.create_virtual_env",
        autospec=True,
        side_effect=sp.CalledProcessError(returncode=2, cmd=["bad"], stderr="Something bad happened".encode()),
    )
    def test_sync_fail_create_virtual_env(self, mock_create_virtual_env):
        test_sync_options = ["-d", "/tmp/ckan-pilot/testprj", "sync"]
        result = self.runner.invoke(cli, test_sync_options)
        self.assertIn("Failed to create a virtual environment", result.output)
        self.assertEqual(result.exit_code, 1)

    @patch(
        "ckan_pilot.helpers.subproc.setup_ckan_src",
        autospec=True,
        side_effect=sp.CalledProcessError(returncode=2, cmd=["bad"], stderr="Something bad happened".encode()),
    )
    def test_sync_fail_setup_ckan_src(self, mock_add_ckan_src):
        test_sync_options = ["-d", "/tmp/ckan-pilot/testprj", "sync"]
        result = self.runner.invoke(cli, test_sync_options)
        self.assertIn("Add CKAN to project failed", result.output)
        self.assertEqual(result.exit_code, 1)

    @patch(
        "ckan_pilot.helpers.subproc.sync_project",
        autospec=True,
        side_effect=sp.CalledProcessError(returncode=2, cmd=["bad"], stderr="Something bad happened".encode()),
    )
    def test_sync_fail_sync_project(self, mock_sync_project):
        self.__init_project()
        shutil.rmtree("/tmp/ckan-pilot/testdir/.venv")

        test_sync_options = ["-d", "/tmp/ckan-pilot/testdir", "sync"]
        result = self.runner.invoke(cli, test_sync_options)
        self.assertIn("Failed to sync project", result.output)
        self.assertEqual(result.exit_code, 1)

    def tearDown(self):
        shutil.rmtree("/tmp/ckan-pilot", ignore_errors=True)
