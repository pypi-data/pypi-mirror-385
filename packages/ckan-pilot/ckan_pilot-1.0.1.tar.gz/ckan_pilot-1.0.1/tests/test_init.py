import shutil
import subprocess as sp
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from ckan_pilot.root import cli


class TestInitCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_init_success(self):
        test_init_options = [
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
        result = self.runner.invoke(cli, test_init_options)
        self.assertIn("initialized", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch.dict("os.environ", {"PATH": "/some/path"}, clear=True)
    def test_init_tools_missing(self):
        test_init_options = [
            "init",
            "-n",
            "test",
            "--project-description",
            "Test description",
            "--ckan-version",
            "2.11.3",
            "-p",
            "3.1",
            "/tmp/ckan-pilot/testdir",
        ]
        result = self.runner.invoke(cli, test_init_options)
        self.assertIn("not found", result.output)
        self.assertEqual(result.exit_code, 1)

    def test_init_permissions_error(self):
        test_init_options = [
            "init",
            "-n",
            "test",
            "--project-description",
            "Test description",
            "--ckan-version",
            "2.11.3",
            "-p",
            "3.10.16",
            "/ckan-pilot/testdir",
        ]
        result = self.runner.invoke(cli, test_init_options)
        self.assertIn("check permissions", result.output)
        self.assertEqual(result.exit_code, 1)

    def test_init_value_error(self):
        test_init_options = [
            "init",
            "-n",
            "test",
            "--project-description",
            "Test description",
            "--ckan-version",
            "2.11.3",
            "-p",
            "3.1",
            "/tmp/ckan-pilot/testdir",
        ]
        result = self.runner.invoke(cli, test_init_options)
        self.assertIn("Validation error", result.output)
        self.assertEqual(result.exit_code, 1)

    @patch(
        "ckan_pilot.helpers.subproc.add_ckan_requirements",
        autospec=True,
        side_effect=sp.CalledProcessError(returncode=2, cmd=["bad"], stderr="Something bad happened".encode()),
    )
    def test_init_fail_add_requirements(self, mock_add_ckan_requirements):
        test_init_options = [
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
        result = self.runner.invoke(cli, test_init_options)
        self.assertIn("CKAN requirements to project failed", result.output)
        self.assertEqual(result.exit_code, 1)

    @patch("click.confirm", return_value=True)
    @patch(
        "ckan_pilot.helpers.subproc.add_ckan_requirements",
        autospec=True,
        side_effect=sp.CalledProcessError(returncode=2, cmd=["bad"], stderr="Something bad happened".encode()),
    )
    def test_init_fail_add_requirements_cleanup_yes(self, mock_add_ckan_requirements, mock_confirm):
        test_init_options = [
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
        result = self.runner.invoke(cli, test_init_options)
        self.assertIn("CKAN requirements to project failed", result.output)
        self.assertIn("Project directory deleted.", result.output)
        self.assertEqual(result.exit_code, 1)

    @patch("click.confirm", return_value=False)
    @patch(
        "ckan_pilot.helpers.subproc.setup_ckan_src",
        autospec=True,
        side_effect=sp.CalledProcessError(returncode=2, cmd=["bad"], stderr="Something bad happened".encode()),
    )
    def test_init_fail_setup_ckan_src_cleanup_no(self, mock_setup_ckan_src, mock_confirm):
        test_init_options = [
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
        result = self.runner.invoke(cli, test_init_options)
        self.assertIn("Add CKAN to project failed", result.output)
        self.assertIn("Project directory left intact.", result.output)
        self.assertEqual(result.exit_code, 1)

    @patch(
        "ckan_pilot.helpers.subproc.add_ckan_dev_requirements",
        autospec=True,
        side_effect=sp.CalledProcessError(returncode=2, cmd=["bad"], stderr="Something bad happened".encode()),
    )
    def test_init_fail_add_dev_requirements(self, mock_add_ckan_dev_requirements):
        test_init_options = [
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
        result = self.runner.invoke(cli, test_init_options)
        self.assertIn("dev requirements to project failed", result.output)
        self.assertEqual(result.exit_code, 1)

    @patch(
        "ckan_pilot.helpers.subproc.setup_ckan_src",
        autospec=True,
        side_effect=sp.CalledProcessError(returncode=2, cmd=["bad"], stderr="Something bad happened".encode()),
    )
    def test_init_fail_setup_ckan_src(self, mock_add_ckan_src):
        test_init_options = [
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
        result = self.runner.invoke(cli, test_init_options)
        self.assertIn("Add CKAN to project failed", result.output)
        self.assertEqual(result.exit_code, 1)

    def tearDown(self):
        shutil.rmtree("/tmp/ckan-pilot", ignore_errors=True)
