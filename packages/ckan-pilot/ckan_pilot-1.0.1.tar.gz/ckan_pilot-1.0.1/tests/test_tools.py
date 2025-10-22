import unittest
from unittest.mock import patch

from click.testing import CliRunner

from ckan_pilot.root import cli


class TestVersionCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @staticmethod
    def _side_effect_except():
        return StopIteration

    @patch("shutil.which", autospec=True)
    def test_tools_list_available(self, mock_which):
        result = self.runner.invoke(cli, ["tools", "list"])
        self.assertIn("available", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("shutil.which", autospec=True)
    def test_tools_list_not_found(self, mock_which):
        mock_which.return_value = None
        result = self.runner.invoke(cli, ["tools", "list"])
        self.assertIn("not found", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("shutil.which", autospec=True)
    @patch("platform.system", autospec=True)
    @patch("subprocess.run", autospec=True)
    def test_tools_install_success(self, mock_subprocess_run, mock_system, mock_which):
        mock_which.return_value = None
        mock_system.return_value = "Linux"
        result = self.runner.invoke(cli, ["tools", "install"])
        self.assertIn("Installing", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("shutil.which", autospec=True)
    @patch("platform.system", autospec=True)
    def test_tools_install_already_installed(self, mock_system, mock_which):
        mock_system.return_value = "Linux"
        result = self.runner.invoke(cli, ["tools", "install"])
        self.assertIn("uv already installed", result.output)
        self.assertEqual(result.exit_code, 0)

    @patch("shutil.which", autospec=True)
    @patch("platform.system", autospec=True)
    def test_tools_install_unsupported_platform(self, mock_which, mock_system):
        mock_which.return_value = None
        mock_system.return_value = "Windows"
        result = self.runner.invoke(cli, ["tools", "install"])
        self.assertIn("Unsupported", result.output)
        self.assertEqual(result.exit_code, 1)

    @patch("urllib.request.urlopen", autospec=True)
    @patch("shutil.which", autospec=True)
    @patch("platform.system", autospec=True)
    @patch("subprocess.run", autospec=True)
    def test_tools_install_exception(self, mock_subprocess_run, mock_system, mock_which, mock_urlopen):
        mock_which.return_value = None
        mock_system.return_value = "Linux"
        mock_subprocess_run.side_effect = self._side_effect_except()
        result = self.runner.invoke(cli, ["tools", "install"])
        self.assertIn("Failed", result.output)
        self.assertEqual(result.exit_code, 1)
