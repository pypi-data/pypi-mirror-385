import unittest
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from ckan_pilot.commands.catalog import CKAN_EXT_CATALOG_URL, cli


class TestCatalogCommand(unittest.TestCase):
    def setUp(self):
        """Set up test data before each test."""
        # Sample mock YAML data that simulates extensions
        self.mock_yaml_data = {
            "extensions": [
                {"name": "test-extension-1", "description": "A sample extension."},
                {"name": "test-extension-2", "description": "Another extension."},
            ]
        }
        self.runner = CliRunner()  # CLI test runner

        # Define a mock project object that can be used in tests
        self.mock_project = MagicMock()

        self.mock_project.projectdir = "/mock/project"

    @patch("ckan_pilot.helpers.catalog.get")
    @patch("rich.table.Table.add_row")
    def test_list_extensions_with_data(self, mock_add_row, mock_catalog_get):
        """
        Test the 'list' subcommand of the 'extensions' CLI group when called with a valid
        catalog source containing multiple extensions.

        This test mocks the catalog YAML retrieval to provide a controlled set of extensions,
        and patches the Table.add_row method to track how the CLI formats and adds extension
        data to the output table.

        The CLI is invoked with the `--catalog-source` option followed by the list subcommand,
        and a mock project object is passed as the Click context.

        Assertions:
        - The CLI exits successfully (exit code 0).
        - The Table.add_row method is called with correct extension name and description pairs,
        matching the mock YAML data.

        Args:
            mock_add_row (MagicMock): Mock of the rich.table.Table.add_row method.
            mock_catalog_get (MagicMock): Mock of the catalog.get function.

        Returns:
            None
        """
        # Setup mock catalog.get() to return sample data
        mock_catalog_get.return_value = self.mock_yaml_data

        # Prepare CLI context object (project) with projectdir
        ctx_obj = self.mock_project

        # Invoke the CLI as: ckan-pilot extensions list --catalog-source <url>
        result = self.runner.invoke(
            cli,
            ["--catalog-source", CKAN_EXT_CATALOG_URL, "list"],
            obj=ctx_obj,
        )

        # Assert the command succeeded
        self.assertEqual(result.exit_code, 0)

        # Now check the table.add_row calls for extension names and descriptions
        expected_calls = [
            ("test-extension-1", "A sample extension."),
            ("test-extension-2", "Another extension."),
        ]

        actual_calls = [call.args for call in mock_add_row.call_args_list]

        for expected_call in expected_calls:
            self.assertIn(expected_call, actual_calls)

    @patch("ckan_pilot.helpers.catalog.get")  # Mock Catalog YAML loading
    @patch("ckan_pilot.commands.catalog.print")  # Mock print to capture output
    def test_list_extensions_with_empty_data(self, mock_print, mock_catalog_file):
        """
        Test the 'list' command of the extensions CLI when YAML is empty.

        Simulates an empty YAML file. Verifies that no rows are added to the table
        and that an appropriate error message is printed.

        Failure Case:
        - Fails if the table is populated despite no data in the YAML file.
        - Fails if the "No extensions found" message is not printed.
        """
        # Simulate empty YAML data
        mock_catalog_file.return_value = {}

        # Invoke the list_extensions command with the --catalog-source argument
        result = self.runner.invoke(
            cli,
            ["--catalog-source", CKAN_EXT_CATALOG_URL, "list"],
            obj=self.mock_project,
        )

        # Check if the command ran successfully
        self.assertEqual(result.exit_code, 0)

        # Verify that no extensions found was logged
        self.assertIn("No extensions found", result.output)  # Ensure appropriate message is printed

    @patch("ckan_pilot.commands.catalog.logger")
    @patch("ckan_pilot.helpers.catalog.get")  # Mock Catalog YAML loading
    def test_list_extensions_with_invalid_yaml(self, mock_catalog_get, mock_logger):
        """
        Test the 'list' command of the extensions CLI when YAML loading fails.

        Simulates a failure in loading the YAML file (e.g., it returns None).
        Verifies that no rows are added and an error message is logged.
        """
        mock_catalog_get.return_value = None  # Simulate invalid YAML

        result = self.runner.invoke(
            cli,
            ["--catalog-source", CKAN_EXT_CATALOG_URL, "list"],
            obj=self.mock_project,
        )

        self.assertEqual(result.exit_code, 0)

        mock_logger.error.assert_called_once_with("No extensions found in catalog: {0}".format(CKAN_EXT_CATALOG_URL))

    @patch("ckan_pilot.commands.catalog.logger")
    @patch("ckan_pilot.helpers.catalog.fetch_extension_metadata")
    @patch("ckan_pilot.helpers.catalog.install_extension")
    @patch("ckan_pilot.helpers.catalog.install_requirements_file")
    @patch("ckan_pilot.helpers.catalog.write_configuration_file")
    def test_extension_add(
        self,
        mock_write_configuration_file,
        mock_install_requirements_file,
        mock_install_extension,
        mock_fetch_extension_metadata,
        mock_logger,
    ):
        """
        Test the 'add' command of the extensions CLI for adding an extension from the catalog.

        Verifies that the extension is added successfully by checking if:
        - The extension metadata is fetched.
        - The extension is installed using the correct URL and version.
        - The required dependencies are installed.

        Failure Case:
        - Fails if the extension installation or requirement installations fail.
        - Fails if the configuration file is not written correctly.
        """
        # Define mock return values
        mock_extension_data = {
            "url": "https://github.com/ckan/ckanext-xloader",
            "version": "2.1.0",
            "setup": {
                "required_system_packages": [],
                "has_requirements": True,
                "has_dev_requirements": False,
            },
        }
        mock_fetch_extension_metadata.return_value = mock_extension_data

        # Run the CLI command with the runner
        result = self.runner.invoke(
            cli,
            ["--catalog-source", CKAN_EXT_CATALOG_URL, "add", "ckanext-xloader"],
            obj=self.mock_project,
        )

        # Ensure the exit status is correct
        self.assertEqual(result.exit_code, 0)

        # Assert that the correct functions were called
        mock_fetch_extension_metadata.assert_called_once_with(
            "https://extensions.ckan.app/catalog.yaml", "ckanext-xloader"
        )
        mock_install_extension.assert_called_once_with(
            self.mock_project.projectdir, "https://github.com/ckan/ckanext-xloader", "2.1.0", False, "ckanext-xloader"
        )
        mock_install_requirements_file.assert_called_once_with(
            self.mock_project.projectdir,
            "https://github.com/ckan/ckanext-xloader",
            "2.1.0",
            "ckanext-xloader",
            "requirements.txt",
            editable=False,
        )
        mock_write_configuration_file.assert_called_once_with(
            self.mock_project.projectdir, mock_extension_data, "ckanext-xloader"
        )
        mock_logger.info.assert_any_call("Installing requirements for: ckanext-xloader")

    @patch("ckan_pilot.commands.catalog.logger")
    @patch("ckan_pilot.helpers.catalog.fetch_extension_metadata")
    @patch("ckan_pilot.helpers.catalog.install_extension")
    @patch("ckan_pilot.helpers.catalog.install_requirements_file")
    @patch("ckan_pilot.helpers.catalog.write_configuration_file")
    def test_extension_add_dev_mode(
        self,
        mock_write_configuration_file,
        mock_install_requirements_file,
        mock_install_extension,
        mock_fetch_extension_metadata,
        mock_logger,
    ):
        # Mock extension data to simulate a proper extension with requirements
        mock_extension_data = {
            "url": "https://github.com/ckan/ckanext-xloader",
            "version": "2.1.0",
            "setup": {
                "required_system_packages": [],
                "has_requirements": True,
                "has_dev_requirements": True,
            },
        }
        mock_fetch_extension_metadata.return_value = mock_extension_data

        # Simulate running the CLI command with --dev flag
        result = self.runner.invoke(
            cli,
            ["--catalog-source", CKAN_EXT_CATALOG_URL, "add", "--dev", "ckanext-xloader"],
            obj=self.mock_project,
        )

        self.assertEqual(result.exit_code, 0)

        # Assert the correct fetch and install functions were called
        mock_fetch_extension_metadata.assert_called_once_with(
            "https://extensions.ckan.app/catalog.yaml", "ckanext-xloader"
        )
        mock_install_extension.assert_called_once_with(
            self.mock_project.projectdir, "https://github.com/ckan/ckanext-xloader", "2.1.0", True, "ckanext-xloader"
        )

        # Assert the install_requirements_file was called for both sets of requirements
        mock_install_requirements_file.assert_any_call(
            self.mock_project.projectdir,
            "https://github.com/ckan/ckanext-xloader",
            "2.1.0",
            "ckanext-xloader",
            "requirements.txt",
            editable=False,
        )
        mock_install_requirements_file.assert_any_call(
            self.mock_project.projectdir,
            "https://github.com/ckan/ckanext-xloader",
            "2.1.0",
            "ckanext-xloader-dev",
            "dev-requirements.txt",
            editable=False,
        )

        # Check that logger.info was called for both requirement installations
        mock_logger.info.assert_any_call("Installing requirements for: ckanext-xloader")
        mock_logger.info.assert_any_call("Installing dev requirements for: ckanext-xloader")

        # Check that write_configuration_file was called to save the extension's configuration
        mock_write_configuration_file.assert_called_once_with(
            self.mock_project.projectdir, mock_extension_data, "ckanext-xloader-dev"
        )

    @patch("ckan_pilot.commands.catalog.logger")
    @patch("ckan_pilot.helpers.catalog.fetch_extension_metadata")
    @patch("ckan_pilot.helpers.catalog.install_extension")
    @patch("ckan_pilot.helpers.catalog.install_requirements_file")
    @patch("ckan_pilot.helpers.catalog.write_configuration_file")
    def test_extension_add_requirements_only(
        self,
        mock_write_configuration_file,
        mock_install_requirements_file,
        mock_install_extension,
        mock_fetch_extension_metadata,
        mock_logger,
    ):
        # Define mock return values
        mock_extension_data = {
            "url": "https://github.com/ckan/ckanext-someext",
            "version": "1.0.0",
            "setup": {
                "required_system_packages": [],
                "has_requirements": True,
                "has_dev_requirements": False,
            },
        }
        mock_fetch_extension_metadata.return_value = mock_extension_data

        # Mock install_extension to simulate success
        mock_install_extension.return_value = None  # Simulate successful extension installation

        # Run the CLI command
        result = self.runner.invoke(
            cli,
            ["--catalog-source", CKAN_EXT_CATALOG_URL, "add", "ckanext-someext"],
            obj=self.mock_project,
        )

        # Assert the CLI command succeeded
        assert result.exit_code == 0

        # Assert the correct functions were called
        mock_fetch_extension_metadata.assert_called_once_with(
            "https://extensions.ckan.app/catalog.yaml", "ckanext-someext"
        )
        mock_install_extension.assert_called_once_with(
            self.mock_project.projectdir, "https://github.com/ckan/ckanext-someext", "1.0.0", False, "ckanext-someext"
        )
        mock_install_requirements_file.assert_called_once_with(
            self.mock_project.projectdir,
            "https://github.com/ckan/ckanext-someext",
            "1.0.0",
            "ckanext-someext",
            "requirements.txt",
            editable=False,
        )
        mock_logger.info.assert_any_call("Installing requirements for: ckanext-someext")

        mock_write_configuration_file.assert_called_once_with(
            self.mock_project.projectdir, mock_extension_data, "ckanext-someext"
        )

    @patch("ckan_pilot.commands.catalog.logger")
    @patch("ckan_pilot.helpers.catalog.fetch_extension_metadata")
    @patch("ckan_pilot.helpers.catalog.install_extension")
    @patch("ckan_pilot.helpers.catalog.install_requirements_file")
    @patch("ckan_pilot.helpers.catalog.write_configuration_file")
    def test_extension_add_no_requirements(
        self,
        mock_write_configuration_file,
        mock_install_requirements_file,
        mock_install_extension,
        mock_fetch_extension_metadata,
        mock_logger,
    ):
        """
        Test the 'add' command of the extensions CLI for an extension that has no requirements.
        This verifies that the function correctly skips the requirement installation.
        """
        # Define mock return values for an extension with no requirements
        mock_extension_data = {
            "url": "https://github.com/ckan/ckanext-xloader",
            "version": "2.1.0",
            "setup": {
                "required_system_packages": [],
                "has_requirements": False,
                "has_dev_requirements": False,
            },
        }
        mock_fetch_extension_metadata.return_value = mock_extension_data

        # Run the CLI command
        result = self.runner.invoke(
            cli,
            ["--catalog-source", CKAN_EXT_CATALOG_URL, "add", "ckanext-xloader"],
            obj=self.mock_project,
        )

        # Ensure the exit status is correct
        self.assertEqual(result.exit_code, 0)

        # Assert the correct functions were called
        mock_fetch_extension_metadata.assert_called_once_with(
            "https://extensions.ckan.app/catalog.yaml", "ckanext-xloader"
        )
        mock_install_extension.assert_called_once_with(
            self.mock_project.projectdir, "https://github.com/ckan/ckanext-xloader", "2.1.0", False, "ckanext-xloader"
        )

        # Ensure that no requirement file installation occurs
        mock_install_requirements_file.assert_not_called()

        # Check that write_configuration_file was called to save the extension's configuration
        mock_write_configuration_file.assert_called_once_with(
            self.mock_project.projectdir, mock_extension_data, "ckanext-xloader"
        )

    @patch("ckan_pilot.helpers.catalog.fetch_extension_metadata")
    def test_invalid_catalog_source(self, mock_fetch_extension_metadata):
        """
        Test what happens when the catalog source URL is invalid.

        This test simulates an invalid catalog source URL and verifies that:
        - The correct exception is raised.
        - The exit code is non-zero to indicate failure.
        - The exception message is correctly included in the result output.

        In this case, we simulate an invalid catalog source by making the
        `fetch_extension_metadata` function raise an exception.
        """
        # Simulate the exception when the fetch_extension_metadata is called
        mock_fetch_extension_metadata.side_effect = Exception("Invalid catalog source")

        # Run the CLI command
        result = self.runner.invoke(
            cli,
            ["--catalog-source", "invalid_url", "add", "ckanext-xloader"],
            obj=self.mock_project,
        )

        # Check that the result exit code is not 0 (indicating failure)
        self.assertNotEqual(result.exit_code, 0)

        # Check if the exception is in the output or captured via exception info
        if result.exc_info:
            exception_type, exception_value, traceback = result.exc_info
            self.assertIn("Invalid catalog source", str(exception_value))
