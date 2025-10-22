import unittest
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from ckan_pilot.commands.start import cli as start_cli


class TestStartCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.mock_project = MagicMock()
        self.mock_project.projectdir = "/fake/path"
        self.mock_project.get_project_metadata.return_value = ("testproject",)

    @patch("ckan_pilot.commands.start.subproc.start_compose")
    def test_start_default(self, mock_start_compose):
        result = self.runner.invoke(start_cli, obj=self.mock_project)
        self.assertEqual(result.exit_code, 0)
        mock_start_compose.assert_called_once_with(
            "/fake/path", d=True, v=False, b=False, project_name="testproject", bake=None
        )

    @patch("ckan_pilot.commands.start.subproc.start_compose")
    def test_start_development_mode(self, mock_start_compose):
        result = self.runner.invoke(start_cli, ["--development"], obj=self.mock_project)

        self.assertEqual(result.exit_code, 0)
        mock_start_compose.assert_called_once_with(
            "/fake/path", d=False, v=False, b=False, project_name="testproject", bake={"COMPOSE_BAKE": "true"}
        )

    @patch("ckan_pilot.commands.start.subproc.start_compose")
    def test_start_with_all_flags(self, mock_start_compose):
        result = self.runner.invoke(start_cli, ["--development", "-v", "-b"], obj=self.mock_project)

        self.assertEqual(result.exit_code, 0)
        mock_start_compose.assert_called_once_with(
            "/fake/path", d=False, v=True, b=True, project_name="testproject", bake={"COMPOSE_BAKE": "true"}
        )

    @patch("ckan_pilot.commands.start.subproc.start_compose")
    def test_start_with_v_and_b_only(self, mock_start_compose):
        result = self.runner.invoke(start_cli, ["-v", "-b"], obj=self.mock_project)

        self.assertEqual(result.exit_code, 0)
        mock_start_compose.assert_called_once_with(
            "/fake/path", d=True, v=True, b=True, project_name="testproject", bake=None
        )
