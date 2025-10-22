import unittest
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from ckan_pilot.commands.stop import cli as stop_cli


class TestStopCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.mock_project = MagicMock()
        self.mock_project.projectdir = "/fake/path"
        self.mock_project.get_project_metadata.return_value = ("testproject", "1.0.0")

    @patch("ckan_pilot.commands.stop.subproc._compose_down")
    def test_stop_default(self, mock_compose_down):
        result = self.runner.invoke(stop_cli, obj=self.mock_project)

        self.assertEqual(result.exit_code, 0)
        mock_compose_down.assert_called_once_with("/fake/path", v=False, project_name="testproject")

    @patch("ckan_pilot.commands.stop.subproc._compose_down")
    def test_stop_with_v(self, mock_compose_down):
        result = self.runner.invoke(stop_cli, ["-v"], obj=self.mock_project)

        self.assertEqual(result.exit_code, 0)
        mock_compose_down.assert_called_once_with("/fake/path", v=True, project_name="testproject")
