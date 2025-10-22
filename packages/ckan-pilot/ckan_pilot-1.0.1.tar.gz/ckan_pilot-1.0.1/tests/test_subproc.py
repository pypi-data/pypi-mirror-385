import subprocess
import unittest
from unittest.mock import MagicMock, patch

import ckan_pilot.helpers.subproc


class TestHelpers(unittest.TestCase):
    @patch("subprocess.run")
    def test_git_clone_wrapper(self, mock_run):
        """
        Test git_clone_wrapper function.

        Simulates a successful git clone operation and checks that the function
        constructs the correct command and calls subprocess.run with the expected arguments.

        Failure Case:
        - Fails if subprocess.run is not called with the correct arguments.
        """
        # Setup mock
        mock_run.return_value = MagicMock(stdout=b"success", stderr=b"", returncode=0)

        # Test parameters
        version = "v1.0"
        git_url = "https://github.com/example/repo"
        extra_flags = ["--depth", "1"]
        clone_target_dir = "/path/to/clone/dir"

        # Call the function
        ckan_pilot.helpers.subproc.git_clone_wrapper(version, git_url, extra_flags, clone_target_dir)

        # Check if subprocess.run was called with the expected command
        mock_run.assert_called_once_with(
            ["git", "clone", "--branch", version, "--depth", "1", git_url, clone_target_dir],
            capture_output=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_git_clone_wrapper_without_extra_flags(self, mock_run):
        """
        Test git_clone_wrapper function when no extra flags are provided.

        Ensures the function correctly constructs the command without additional flags.
        """
        mock_run.return_value = MagicMock(stdout=b"success", stderr=b"", returncode=0)

        version = "v1.0"
        git_url = "https://github.com/example/repo"
        extra_flags = None  # No extra flags
        clone_target_dir = "/path/to/clone/dir"

        # Call the function
        ckan_pilot.helpers.subproc.git_clone_wrapper(version, git_url, extra_flags, clone_target_dir)

        # Verify subprocess.run was called with the correct command (no extra flags)
        mock_run.assert_called_once_with(
            ["git", "clone", "--branch", version, git_url, clone_target_dir],  # No extra flags included
            capture_output=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_uv_add_wrapper(self, mock_run):
        """
        Test uv_add_wrapper function.

        Simulates a successful uv add operation and checks that the function
        constructs the correct command and calls subprocess.run with the expected arguments.

        Failure Case:
        - Fails if subprocess.run is not called with the correct arguments.
        """
        # Setup mock
        mock_run.return_value = MagicMock(stdout=b"success", stderr=b"", returncode=0)

        # Test parameters
        project_dir = "/path/to/project"
        group = "ckanext"
        target = "extension_name"
        editable = True
        requirements_file = None

        # Call the function
        result = ckan_pilot.helpers.subproc.uv_add_wrapper(project_dir, group, target, editable, requirements_file)

        # Check if subprocess.run was called with the expected command
        mock_run.assert_called_once_with(
            ["uv", "--directory", project_dir, "add", "--group", group, "--editable", target],
            capture_output=True,
            check=True,
        )

        # Ensure the return value is as expected
        self.assertEqual(result.stdout, b"success")
        self.assertEqual(result.stderr, b"")

    @patch("subprocess.run")
    def test_uv_add_wrapper_no_target_or_requirements(self, mock_run):
        """
        Test uv_add_wrapper function with no target or requirements_file, ensuring valid command is run.

        Failure Case:
        - Fails if both target and requirements_file are provided.
        - Fails if no arguments are passed but the function proceeds.
        """
        # Setup mock
        mock_run.return_value = MagicMock(stdout=b"success", stderr=b"", returncode=0)

        # Test parameters with no target and no requirements_file
        project_dir = "/path/to/project"
        group = "ckanext"
        target = None
        editable = False
        requirements_file = None

        # Call the function
        result = ckan_pilot.helpers.subproc.uv_add_wrapper(project_dir, group, target, editable, requirements_file)

        # Check if subprocess.run was called with the expected command
        mock_run.assert_called_once_with(
            ["uv", "--directory", project_dir, "add", "--group", group], capture_output=True, check=True
        )

        # Ensure the return value is as expected
        self.assertEqual(result.stdout, b"success")
        self.assertEqual(result.stderr, b"")

    @patch("subprocess.run")
    def test_uv_add_wrapper_with_no_group(self, mock_run):
        """
        Test uv_add_wrapper function when no group is specified.

        Ensures the function correctly includes no --group flag in the command.
        """
        mock_run.return_value = MagicMock(stdout=b"success", stderr=b"", returncode=0)

        project_dir = "/path/to/project"
        group = None
        target = "my-package"
        editable = None
        requirements_file = None

        ckan_pilot.helpers.subproc.uv_add_wrapper(project_dir, group, target, editable, requirements_file)

        mock_run.assert_called_once_with(
            ["uv", "--directory", project_dir, "add", target],
            capture_output=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_uv_add_wrapper_with_requirements_file(self, mock_run):
        """
        Test uv_add_wrapper function when a requirements file is provided.

        Ensures the function correctly includes the -r flag with the requirements file.
        """
        mock_run.return_value = MagicMock(stdout=b"success", stderr=b"", returncode=0)

        project_dir = "/path/to/project"
        group = None
        target = None
        editable = None
        requirements_file = "/path/to/requirements.txt"

        ckan_pilot.helpers.subproc.uv_add_wrapper(project_dir, group, target, editable, requirements_file)

        mock_run.assert_called_once_with(
            ["uv", "--directory", project_dir, "add", "-r", requirements_file],
            capture_output=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_uv_remove_wrapper_no_flags(self, mock_run):
        """
        Test case for calling the uv_remove_wrapper function without any group, target, or extra_flags.

        This test simulates a call to the `uv_remove_wrapper` function with no group,
        target, or extra_flags, and verifies that the correct command is constructed and passed to subprocess.run.

        Expected behavior:
        - The function constructs the command with default options and calls `subprocess.run` with the correct arguments
        - The subprocess result is returned correctly.
        """
        # Simulate a subprocess.CompletedProcess return value
        mock_completed_process = MagicMock()
        mock_completed_process.returncode = 0
        mock_completed_process.stderr = ""
        mock_run.return_value = mock_completed_process

        # Call the function with no group, target, or extra_flags
        result = ckan_pilot.helpers.subproc.uv_remove_wrapper("/path/to/project", None, None, None)

        # Check that subprocess.run was called with the correct arguments
        mock_run.assert_called_once_with(
            ["uv", "--directory", "/path/to/project", "remove", "--no-sync"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert the return value is the mocked subprocess result
        self.assertEqual(result, mock_completed_process)

    @patch("subprocess.run")
    def test_uv_remove_wrapper_with_group_and_flags(self, mock_run):
        """
        Test case for calling the uv_remove_wrapper function with a group, target, and extra_flags.

        This test simulates a call to the `uv_remove_wrapper` function with a specified group,
        target, and extra_flags, and verifies that the correct command is constructed and passed to subprocess.run.

        Expected behavior:
        - The function constructs the command with the specified group, target, and extra flags.
        - The subprocess result is returned correctly.
        """
        # Simulate a subprocess.CompletedProcess return value
        mock_completed_process = MagicMock()
        mock_completed_process.returncode = 0
        mock_completed_process.stderr = "Error occurred"
        mock_run.return_value = mock_completed_process

        # Call the function with group, target, and extra_flags
        result = ckan_pilot.helpers.subproc.uv_remove_wrapper(
            "/path/to/project", "group-name", "target-name", ["--force", "--quiet"]
        )

        # Check that subprocess.run was called with the correct arguments
        mock_run.assert_called_once_with(
            [
                "uv",
                "--directory",
                "/path/to/project",
                "remove",
                "--no-sync",
                "--group",
                "group-name",
                "--force",
                "--quiet",
                "target-name",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert the return value is the mocked subprocess result
        self.assertEqual(result, mock_completed_process)

    @patch("subprocess.run")
    def test_uv_remove_wrapper_with_target_only(self, mock_run):
        """
        Test case for calling the uv_remove_wrapper function with a target only.

        This test simulates a call to the `uv_remove_wrapper` function with only a,
        target specified (and no group or extra_flags), and verifies that the correct,
        command is constructed and passed to subprocess.run.

        Expected behavior:
        - The function constructs the command with the target and default options.
        - The subprocess result is returned correctly.
        """
        # Simulate a subprocess.CompletedProcess return value
        mock_completed_process = MagicMock()
        mock_completed_process.returncode = 0
        mock_completed_process.stderr = ""
        mock_run.return_value = mock_completed_process

        # Call the function with only a target and no group or extra_flags
        result = ckan_pilot.helpers.subproc.uv_remove_wrapper("/path/to/project", None, "target-name", None)

        # Check that subprocess.run was called with the correct arguments
        mock_run.assert_called_once_with(
            ["uv", "--directory", "/path/to/project", "remove", "--no-sync", "target-name"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert the return value is the mocked subprocess result
        self.assertEqual(result, mock_completed_process)

    @patch("subprocess.run")
    def test_uv_remove_wrapper_error_handling(self, mock_run):
        """
        Test case for handling errors in the uv_remove_wrapper function.

        This test simulates a scenario where an error occurs during the execution of the command
        (e.g., subprocess fails). It verifies that the function handles errors correctly and,
        that the subprocess result with an error is returned.

        Expected behavior:
        - The function constructs the command with the provided parameters.
        - The subprocess result with an error is returned.
        """
        # Simulate a subprocess.CompletedProcess return value with an error
        mock_completed_process = MagicMock()
        mock_completed_process.returncode = 1
        mock_completed_process.stderr = "Some error occurred"
        mock_run.return_value = mock_completed_process

        # Call the function with parameters that cause an error
        result = ckan_pilot.helpers.subproc.uv_remove_wrapper(
            "/path/to/project", "group-name", "target-name", ["--force"]
        )

        # Check that subprocess.run was called with the correct arguments
        mock_run.assert_called_once_with(
            [
                "uv",
                "--directory",
                "/path/to/project",
                "remove",
                "--no-sync",
                "--group",
                "group-name",
                "--force",
                "target-name",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        # Assert the return value is the mocked subprocess result
        self.assertEqual(result, mock_completed_process)

    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.run")
    def test_ckan_cli_base_command(self, mock_run, mock_logger):
        mock_run.return_value = MagicMock(stdout=b"CKAN started", returncode=0)

        ckan_pilot.helpers.subproc.ckan_cli("/fake/project", generate_config=False, dev=False, prod=False)

        mock_run.assert_called_once_with(["uv", "run", "ckan"], capture_output=True, check=True, cwd="/fake/project")
        mock_logger.info.assert_called_with("CKAN started")

    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.run")
    def test_ckan_cli_generate_config(self, mock_run, mock_logger):
        mock_run.return_value = MagicMock(stdout=b"Config generated")

        ckan_pilot.helpers.subproc.ckan_cli("/project", generate_config=True, dev=False, prod=False)

        mock_run.assert_called_once_with(
            ["uv", "run", "ckan", "generate", "config"], capture_output=True, check=True, cwd="/project"
        )
        mock_logger.info.assert_called_with("Config generated")

    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.run")
    def test_ckan_cli_dev_and_prod(self, mock_run, mock_logger):
        mock_run.return_value = MagicMock(stdout=b"Both ini files used")

        ckan_pilot.helpers.subproc.ckan_cli("/project", generate_config=False, dev=True, prod=True)

        mock_run.assert_called_once_with(
            ["uv", "run", "ckan", "development.ini", "production.ini"], capture_output=True, check=True, cwd="/project"
        )
        mock_logger.info.assert_called_with("Both ini files used")

    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.run", side_effect=FileNotFoundError)
    def test_ckan_cli_command_not_found(self, mock_run, mock_logger):
        ckan_pilot.helpers.subproc.ckan_cli("/project", generate_config=False, dev=False, prod=False)

        mock_logger.error.assert_called_with("Command not found: %s", "uv")

    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.run", side_effect=Exception("Boom"))
    def test_ckan_cli_unexpected_error(self, mock_run, mock_logger):
        ckan_pilot.helpers.subproc.ckan_cli("/project", generate_config=False, dev=False, prod=False)

        mock_logger.exception.assert_called_with("An unexpected error occurred: %s", "Boom")

    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.run", side_effect=MagicMock(side_effect=RuntimeError("CKAN failed")))
    def test_ckan_cli_called_process_error(self, mock_run, mock_logger):
        # Simulate a CalledProcessError
        error = subprocess.CalledProcessError(
            returncode=1, cmd=["uv", "run", "ckan"], output=b"Partial output", stderr=b"Something broke"
        )
        mock_run.side_effect = error

        ckan_pilot.helpers.subproc.ckan_cli("/project", generate_config=False, dev=False, prod=False)

        mock_logger.error.assert_any_call("CKAN command failed with exit code %s", 1)
        mock_logger.error.assert_any_call("Stdout:\n%s", "Partial output")
        mock_logger.error.assert_any_call("Stderr:\n%s", "Something broke")

    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.run")
    def test_start_compose_detached_with_build(self, mock_run, mock_logger):
        mock_run.return_value = MagicMock(returncode=0, stdout="Started in detached mode")
        code = ckan_pilot.helpers.subproc.start_compose("/fake/project", d=True, v=False, b=True, project_name="test")

        mock_run.assert_called_once_with(
            ["docker", "compose", "-p", "test", "up", "--build", "-d"],
            cwd="/fake/project/compose-dev",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        mock_logger.debug.assert_any_call("Started in detached mode")
        self.assertEqual(code, 0)

    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.run")
    def test_start_compose_detached_without_build(self, mock_run, mock_logger):
        mock_run.return_value = MagicMock(returncode=0, stdout="Detached no build")
        code = ckan_pilot.helpers.subproc.start_compose("/fake/project", d=True, v=False, b=False, project_name="test")

        mock_run.assert_called_once_with(
            ["docker", "compose", "-p", "test", "up", "-d"],
            cwd="/fake/project/compose-dev",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        self.assertEqual(code, 0)

    @patch("ckan_pilot.helpers.subproc._compose_down")
    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.Popen")
    def test_start_compose_foreground_completes(self, mock_popen, mock_logger, mock_down):
        mock_process = MagicMock()
        mock_process.stdout = ["Line 1\n", "Line 2\n"]
        mock_process.wait.return_value = 123
        mock_popen.return_value = mock_process

        code = ckan_pilot.helpers.subproc.start_compose("/fake/project", d=False, v=False, b=False, project_name="test")

        mock_popen.assert_called_once_with(
            ["docker", "compose", "-p", "test", "up", "-w"],
            cwd="/fake/project/compose-dev",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        mock_logger.debug.assert_any_call("Line 1")
        mock_logger.debug.assert_any_call("Line 2")
        self.assertEqual(code, 123)

    @patch("ckan_pilot.helpers.subproc._compose_down")
    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.Popen")
    def test_start_compose_foreground_keyboard_interrupt(self, mock_popen, mock_logger, mock_down):
        mock_process = MagicMock()

        def side_effect():
            raise KeyboardInterrupt

        mock_process.stdout = MagicMock()
        mock_process.stdout.__iter__.side_effect = side_effect
        mock_process.wait.return_value = 1
        mock_popen.return_value = mock_process

        code = ckan_pilot.helpers.subproc.start_compose("/fake/project", d=False, v=True, b=False, project_name="test")

        mock_down.assert_called_once_with("/fake/project", True, "test")
        self.assertEqual(code, 1)

    @patch("ckan_pilot.helpers.subproc.sp.run")
    def test_compose_down_no_volumes(self, mock_run):
        mock_run.return_value = MagicMock(stdout="Stopped containers", stderr="", returncode=0)

        ckan_pilot.helpers.subproc._compose_down("/fake/project", v=False, project_name="testproject")

        mock_run.assert_called_once_with(
            ["docker", "compose", "-p", "testproject", "down"],
            cwd="/fake/project/compose-dev",
            capture_output=True,
            text=True,
            check=False,  # noqa: E501
        )

    @patch("ckan_pilot.helpers.subproc.sp.run")
    def test_compose_down_with_volumes(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", stderr="Warning: volume will be removed", returncode=0)

        ckan_pilot.helpers.subproc._compose_down("/fake/project", v=True, project_name="testproject")

        mock_run.assert_called_once_with(
            ["docker", "compose", "-p", "testproject", "down", "-v"],
            cwd="/fake/project/compose-dev",
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("ckan_pilot.helpers.subproc.logger")
    @patch("ckan_pilot.helpers.subproc.sp.run", side_effect=Exception("Docker not found"))
    def test_compose_down_exception(self, mock_run, mock_logger):
        ckan_pilot.helpers.subproc._compose_down("/fake/project", v=True, project_name="testproject")

        mock_logger.error.assert_called_once()
        self.assertIn("Docker not found", mock_logger.error.call_args[0][0])

    @patch("ckan_pilot.helpers.subproc.sp.run")
    def test_git_wrapper_success_no_flags(self, mock_run):
        mock_result = MagicMock()
        mock_result.stderr.decode.return_value = ""
        mock_result.stdout = b"Success"
        mock_run.return_value = mock_result

        result = ckan_pilot.helpers.subproc.git_wrapper(["status"], None)
        mock_run.assert_called_once_with(["git", "status"], capture_output=True, check=True)
        self.assertEqual(result, mock_result)

    @patch("ckan_pilot.helpers.subproc.sp.run")
    def test_git_wrapper_success_with_flags(self, mock_run):
        mock_result = MagicMock()
        mock_result.stderr.decode.return_value = ""
        mock_result.stdout = b"Success"
        mock_run.return_value = mock_result

        result = ckan_pilot.helpers.subproc.git_wrapper(["log"], "--oneline")
        mock_run.assert_called_once_with(["git", "log", "--oneline"], capture_output=True, check=True)
        self.assertEqual(result, mock_result)

    @patch("ckan_pilot.helpers.subproc.sp.run")
    def test_git_wrapper_failure(self, mock_run):
        error = subprocess.CalledProcessError(returncode=1, cmd=["git", "pull"], stderr=b"fatal: not a git repository")
        mock_run.side_effect = error

        with self.assertRaises(subprocess.CalledProcessError):
            ckan_pilot.helpers.subproc.git_wrapper(["pull"], None)

        mock_run.assert_called_once_with(["git", "pull"], capture_output=True, check=True)
