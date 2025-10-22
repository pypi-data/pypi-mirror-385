import unittest
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from ckan_pilot.commands.git import cli


class TestGitInitCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.project = MagicMock()
        self.project.projectdir = "/fake/project"

    @patch("ckan_pilot.commands.git.os.listdir")
    @patch("ckan_pilot.commands.git.os.path.isdir")
    @patch("ckan_pilot.commands.git.os.path.exists")
    @patch("ckan_pilot.commands.git.configparser.ConfigParser")
    @patch("ckan_pilot.commands.git.subproc.git_wrapper")
    def test_init_command_basic_success(
        self, mock_git_wrapper, mock_config_parser, mock_exists, mock_isdir, mock_listdir
    ):
        mock_listdir.return_value = ["ext1"]
        mock_isdir.return_value = True
        mock_exists.return_value = True

        mock_config = MagicMock()
        mock_config.__getitem__.return_value = {"url": "https://example.com/repo.git"}
        mock_config_parser.return_value = mock_config

        result = self.runner.invoke(cli, ["init"], obj=self.project)

        self.assertEqual(result.exit_code, 0)
        mock_git_wrapper.assert_any_call(["init", "/fake/project"], None)
        mock_git_wrapper.assert_any_call(["submodule", "add", "--force", "https://example.com/repo.git", "ext1"], None)

    @patch("ckan_pilot.commands.git.os.listdir", return_value=[])
    @patch("ckan_pilot.commands.git.os.path.isdir", return_value=True)
    @patch("ckan_pilot.commands.git.subproc.git_wrapper")
    def test_git_repo_add_remote(self, mock_git_wrapper, mock_isdir, mock_listdir):
        result = self.runner.invoke(cli, ["init", "--git-repo", "https://example.com/repo.git"], obj=self.project)
        self.assertEqual(result.exit_code, 0)
        mock_git_wrapper.assert_any_call(["remote", "add", "origin", "https://example.com/repo.git"], None)

    @patch("ckan_pilot.commands.git.os.listdir")
    @patch("ckan_pilot.commands.git.os.path.isdir")
    @patch("ckan_pilot.commands.git.os.path.exists")
    @patch("ckan_pilot.commands.git.subproc.git_wrapper")
    def test_missing_git_config_skips_extension(self, mock_git_wrapper, mock_exists, mock_isdir, mock_listdir):
        mock_listdir.return_value = ["ext1"]
        mock_isdir.return_value = True
        mock_exists.return_value = False  # missing .git/config

        result = self.runner.invoke(cli, ["init"], obj=self.project)

        self.assertEqual(result.exit_code, 0)
        mock_git_wrapper.assert_called_once_with(["init", "/fake/project"], None)

    @patch("ckan_pilot.commands.git.os.listdir")
    @patch("ckan_pilot.commands.git.os.path.isdir")
    @patch("ckan_pilot.commands.git.os.path.exists")
    @patch("ckan_pilot.commands.git.configparser.ConfigParser")
    @patch("ckan_pilot.commands.git.subproc.git_wrapper")
    def test_missing_remote_origin_url(
        self, mock_git_wrapper, mock_config_parser, mock_exists, mock_isdir, mock_listdir
    ):
        mock_listdir.return_value = ["ext1"]
        mock_isdir.return_value = True
        mock_exists.return_value = True

        mock_config = MagicMock()
        mock_config.__getitem__.side_effect = KeyError  # missing remote origin
        mock_config_parser.return_value = mock_config

        result = self.runner.invoke(cli, ["init"], obj=self.project)
        self.assertEqual(result.exit_code, 0)
        mock_git_wrapper.assert_called_once_with(["init", "/fake/project"], None)

    @patch("ckan_pilot.commands.git.os.listdir")
    @patch("ckan_pilot.commands.git.os.path.isdir")
    @patch("ckan_pilot.commands.git.os.path.exists")
    @patch("ckan_pilot.commands.git.configparser.ConfigParser")
    @patch("ckan_pilot.commands.git.subproc.git_wrapper")
    def test_submodule_add_fails_and_aborts(
        self, mock_git_wrapper, mock_config_parser, mock_exists, mock_isdir, mock_listdir
    ):
        mock_listdir.return_value = ["ext1"]
        mock_isdir.return_value = True
        mock_exists.return_value = True

        mock_config = MagicMock()
        mock_config.__getitem__.return_value = {"url": "https://example.com/repo.git"}
        mock_config_parser.return_value = mock_config

        def git_wrapper_side_effect(cmd, _):
            if cmd[0] == "submodule":
                raise Exception("Submodule add failed")
            return MagicMock()

        mock_git_wrapper.side_effect = git_wrapper_side_effect

        result = self.runner.invoke(cli, ["init"], obj=self.project)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Submodule add failed", result.output)

    @patch("ckan_pilot.commands.git.os.listdir", return_value=[])
    @patch("ckan_pilot.commands.git.os.path.isdir", return_value=True)
    @patch("ckan_pilot.commands.git.subproc.git_wrapper")
    def test_git_repo_add_remote_raises_and_aborts(self, mock_git_wrapper, mock_isdir, mock_listdir):
        def side_effect(cmd, flags):
            if cmd == ["remote", "add", "origin", "https://example.com/repo.git"]:
                raise Exception("simulated failure")
            else:
                return MagicMock()

        mock_git_wrapper.side_effect = side_effect

        result = self.runner.invoke(
            cli,
            ["init", "--git-repo", "https://example.com/repo.git"],
            obj=self.project,
        )

        mock_git_wrapper.assert_any_call(["remote", "add", "origin", "https://example.com/repo.git"], None)

        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Failed to add remote repository: simulated failure", result.output)
