import os
import subprocess as sp
import unittest
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock, mock_open, patch

import click
import requests
import tomllib
import yaml

import ckan_pilot.helpers.catalog

# Sample YAML as a Python dictionary
mock_catalog_data = yaml.safe_load("""
extensions:
  - name: "ckanext-xloader"
    url: "https://github.com/ckan/ckanext-xloader"
    version: "2.1.0"
    description: >-
      Loads CSV (and similar) data into CKAN's DataStore.
      Designed as a replacement for DataPusher
      because it offers ten times the speed and more robustness
      (hence the name, derived from "Express Loader").
    supported_ckan_versions:
      - "2.11"
      - "2.10"
    plugins:
      - "xloader"
    configuration:
      has_config_declaration: true
      options:
    setup:
      required_system_packages: [sqlalchemy]
      has_pyproject_toml: true
      has_requirements: true
      has_dev_requirements: true
      init-config:
      afterinit-config:
    metadata:
      keywords:
        - "xloader"
        - "datastore"
        - "loader"
        - "express"

  - name: "ckanext-pages"
    url: "https://github.com/ckan/ckanext-pages"
    version: "v0.5.2"
    description: >-
      This extension gives you an easy way to add simple pages to CKAN.
    supported_ckan_versions:
      - "2.10"
    plugins:
      - "pages"
    configuration:
      has_config_declaration: false
      options:
        - key: "ckanext.pages.organization"
          example: "False"
          default: "False"
          required: false
    setup:
      required_system_packages: []
      has_requirements: true
      has_dev_requirements: true
    metadata:
      keywords:
        - "pages"
        - "ckanext-pages"
""")


# Normalize indentation by removing the leading spaces
def normalize_indentation(text):
    """
    Normalizes the indentation of a given text by removing leading spaces.

    Args:
        text (str): The input text to normalize.

    Returns:
        str: The input text with normalized indentation.
    """
    return "\n".join([line.lstrip() for line in text.strip().split("\n")])


class TestHelpers(unittest.TestCase):
    @patch("requests.get")  # Mocking requests.get for URL retrieval
    @patch("ckan_pilot.helpers.catalog.logger")
    def test_get_from_url(self, mock_logger, mock_get):
        """
        Test the retrieval of YAML data from a URL.
        """
        # Setup the mock response for requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = yaml.dump({"key": "value"})
        mock_get.return_value = mock_response

        catalog_url = "http://example.com/catalog.yaml"

        # Call the method
        result = ckan_pilot.helpers.catalog.get(catalog_url)

        # Assert the result matches the expected parsed YAML
        self.assertEqual(result, {"key": "value"})

        # Check if requests.get was called correctly
        mock_get.assert_called_once_with(catalog_url, timeout=10)

        # Check if the correct log messages were recorded
        mock_logger.debug.assert_any_call("Fetching YAML from URL: {0}".format(catalog_url))

    @patch("builtins.open", new_callable=mock_open, read_data=yaml.dump({"key": "value"}))
    @patch("ckan_pilot.helpers.catalog.logger")
    def test_get_from_file(self, mock_logger, mock_file):
        """
        Test the retrieval of YAML data from a local file.
        """
        catalog_file = "path/to/catalog.yaml"

        # Call the method
        result = ckan_pilot.helpers.catalog.get(catalog_file)

        # Assert the result matches the expected parsed YAML
        self.assertEqual(result, {"key": "value"})

        # Check if the open function was called correctly
        mock_file.assert_called_once_with(catalog_file, "r")

        # Check if the correct log messages were recorded
        mock_logger.info.assert_any_call("Loading YAML from file: {0}".format(catalog_file))

    @patch("requests.get")  # Mocking requests.get for failure scenario
    @patch("ckan_pilot.helpers.catalog.logger")
    def test_get_from_url_failure(self, mock_logger, mock_get):
        """
        Test the failure scenario when retrieving YAML data from a URL.
        """
        # Mock the response to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        catalog_url = "http://example.com/catalog.yaml"
        with self.assertRaises(click.Abort):  # Expecting click.Abort to be raised, not just Exception
            ckan_pilot.helpers.catalog.get(catalog_url)

        # Check if the correct error log was recorded
        mock_logger.error.assert_any_call("Error fetching YAML from URL: {0}".format(catalog_url))

    @patch("builtins.open")
    @patch("ckan_pilot.helpers.catalog.logger")
    def test_get_from_file_not_found(self, mock_logger, mock_file):
        """
        Test the failure scenario when the file is not found.
        """
        # Simulate a FileNotFoundError when trying to open the file
        mock_file.side_effect = FileNotFoundError

        catalog_file = "path/to/nonexistent/catalog.yaml"
        with self.assertRaises(click.Abort):  # Expecting click.Abort to be raised, not just Exception
            ckan_pilot.helpers.catalog.get(catalog_file)

        # Check if the correct error log was recorded
        mock_logger.error.assert_any_call("Error: File not found - {0}".format(catalog_file))

    @patch("builtins.open", new_callable=mock_open, read_data="invalid: yaml: data")
    @patch("yaml.safe_load", side_effect=yaml.YAMLError("YAML parsing error"))  # Mock safe_load instead of read
    @patch("ckan_pilot.helpers.catalog.logger")
    def test_get_from_yaml_error(self, mock_logger, mock_yaml, mock_file):
        """
        Test the failure scenario when the YAML parsing fails.
        """
        catalog_file = "path/to/catalog.yaml"

        with self.assertRaises(click.Abort):  # Expecting click.Abort to be raised
            ckan_pilot.helpers.catalog.get(catalog_file)

        # Check if the correct error log was recorded
        mock_logger.error.assert_any_call(f"Error parsing YAML: {catalog_file}")

    @patch("builtins.open")
    @patch("ckan_pilot.helpers.catalog.logger")
    def test_get_unexpected_error(self, mock_logger, mock_file):
        """
        Test the failure scenario for an unexpected error.
        """
        # Simulate a generic exception
        mock_file.side_effect = Exception("Unexpected error")

        catalog_file = "path/to/catalog.yaml"
        with self.assertRaises(click.Abort):  # Expecting click.Abort to be raised
            ckan_pilot.helpers.catalog.get(catalog_file)

        # Check if the correct error log was recorded
        mock_logger.error.assert_any_call("Unexpected error: {0}".format("Unexpected error"))

    @patch("builtins.open", new_callable=mock_open, read_data="key = 'value'")
    @patch("tomllib.load")
    def test_get_from_toml_success(self, mock_load, mock_open):
        """
        Test case for successful TOML file parsing.

        This test simulates the scenario where a TOML file is successfully loaded and parsed.
        It mocks the `open` and `tomllib.load` functions to verify that the file is opened correctly,
        the `tomllib.load` function is called to parse the file, and the correct result is returned.

        Expected behavior:
        - The file is opened with the correct path.
        - The `tomllib.load` function is called to parse the file.
        - The parsed content is returned correctly.
        """
        # Simulate TOML parsing success
        mock_load.return_value = {"key": "value"}

        # Test the function
        result = ckan_pilot.helpers.catalog.get_from_toml("/path/to/toml/file")

        # Check that the file was opened with the correct path
        mock_open.assert_called_once_with("/path/to/toml/file", "rb")

        # Check that tomllib.load was called to parse the file
        mock_load.assert_called_once_with(mock_open())

        # Assert the return value is correct
        self.assertEqual(result, {"key": "value"})

    @patch("builtins.open", new_callable=mock_open)
    @patch("tomllib.load")
    def test_get_from_toml_file_not_found(self, mock_load, mock_open):
        """
        Test case for handling a FileNotFoundError when loading a TOML file.

        This test simulates the scenario where the TOML file does not exist and a `FileNotFoundError` is raised.
        It verifies that the function raises a `click.Abort` exception as expected when the file is not found.

        Expected behavior:
        - A `click.Abort` exception is raised when the file is not found.
        - The file is opened with the correct path.
        - `tomllib.load` is not called due to the missing file.
        """
        # Simulate a FileNotFoundError
        mock_open.side_effect = FileNotFoundError

        # Test the function and assert that it raises click.Abort()
        with self.assertRaises(click.Abort):
            ckan_pilot.helpers.catalog.get_from_toml("/path/to/nonexistent/file")

        # Check that the file was opened with the correct path
        mock_open.assert_called_once_with("/path/to/nonexistent/file", "rb")

        # Ensure tomllib.load was not called because the file wasn't found
        mock_load.assert_not_called()

    @patch("builtins.open", new_callable=mock_open, read_data="key = 'value'")
    @patch("tomllib.load")
    def test_get_from_toml_toml_decode_error(self, mock_load, mock_open):
        """
        Test case for handling a TOML decoding error.

        This test simulates the scenario where there is an error while decoding the TOML file.
        It verifies that the function raises a `click.Abort` exception when a `tomllib.TOMLDecodeError` occurs.

        Expected behavior:
        - A `click.Abort` exception is raised due to the TOML decode error.
        - The file is opened with the correct path.
        - The `tomllib.load` function is called and raises the decode error.
        """
        # Simulate a TOML decode error
        mock_load.side_effect = tomllib.TOMLDecodeError("Error in TOML file")

        # Test the function and assert that it raises click.Abort()
        with self.assertRaises(click.Abort):
            ckan_pilot.helpers.catalog.get_from_toml("/path/to/toml/file")

        # Check that the file was opened with the correct path
        mock_open.assert_called_once_with("/path/to/toml/file", "rb")

        # Ensure tomllib.load was called and it raised the decode error
        mock_load.assert_called_once_with(mock_open())

    @patch("builtins.open", new_callable=mock_open, read_data="key = 'value'")
    @patch("tomllib.load")
    def test_get_from_toml_unexpected_error(self, mock_load, mock_open):
        """
        Test case for handling an unexpected error while loading a TOML file.

        This test simulates a generic unexpected error during the TOML file parsing.
        It ensures that the function raises a `click.Abort` exception when any unexpected error occurs.

        Expected behavior:
        - A `click.Abort` exception is raised due to the unexpected error.
        - The file is opened with the correct path.
        - The `tomllib.load` function is called and raises the unexpected error.
        """
        # Simulate an unexpected error
        mock_load.side_effect = Exception("Unexpected error")

        # Test the function and assert that it raises click.Abort()
        with self.assertRaises(click.Abort):
            ckan_pilot.helpers.catalog.get_from_toml("/path/to/toml/file")

        # Check that the file was opened with the correct path
        mock_open.assert_called_once_with("/path/to/toml/file", "rb")

        # Ensure tomllib.load was called and it raised the unexpected error
        mock_load.assert_called_once_with(mock_open())

    def test_strip_version(self):
        """
        Test case for stripping version specifiers from package strings.

        This test checks that the function correctly strips version specifiers
        (e.g., `>=`, `<=`, `==`) from package names in version strings.

        Expected behavior:
        - The function returns the package name without the version specifier.
        """
        self.assertEqual(ckan_pilot.helpers.catalog.strip_version("package>=1.2.3"), "package")
        self.assertEqual(ckan_pilot.helpers.catalog.strip_version("package<=2.0.0"), "package")
        self.assertEqual(ckan_pilot.helpers.catalog.strip_version("package==1.0.0"), "package")
        self.assertEqual(ckan_pilot.helpers.catalog.strip_version("package"), "package")  # No version

    @patch("ckan_pilot.helpers.catalog.subproc.uv_remove_wrapper")
    @patch("ckan_pilot.helpers.catalog.strip_version")
    def test_remove_extension(self, mock_strip_version, mock_uv_remove):
        """
        Test that remove_extension properly removes an extension and its dependencies.
        """
        # Mock project object
        project = MagicMock()
        project.projectdir = "/fake/project/dir"

        extension_name = "ckanext-example"
        extension_requirements = ["dep1>=1.0", "dep2<=2.0", "ckanext-example==1.2"]
        group = "default"
        extra_flags = ["--force"]

        # Improved mock strip_version to handle all constraint symbols
        mock_strip_version.side_effect = (
            lambda x: x.split("<")[0].split(">")[0].split("=")[0].split("~")[0].split("!")[0]
        )

        # Call function
        ckan_pilot.helpers.catalog.remove_extension(
            project.projectdir, extension_name, extension_requirements, group, extra_flags
        )

        # Check extension removal
        mock_uv_remove.assert_any_call(
            "/fake/project/dir", group=extension_name, target=extension_name, extra_flags=extra_flags
        )

        # Check dependencies removal (excluding the extension itself)
        mock_uv_remove.assert_any_call("/fake/project/dir", group=group, target="dep1", extra_flags=extra_flags)
        mock_uv_remove.assert_any_call("/fake/project/dir", group=group, target="dep2", extra_flags=extra_flags)

        # Ensure extension itself isn't removed twice
        removed_targets = [call.kwargs["target"] for call in mock_uv_remove.call_args_list if "target" in call.kwargs]
        self.assertEqual(removed_targets.count(extension_name), 1)

    @patch("ckan_pilot.helpers.catalog.logger")
    @patch("ckan_pilot.helpers.catalog.os.system")
    def test_remove_editable_extension(self, mock_os_system, mock_logger):
        """
        Test that remove_editable_extension properly deletes the specified folder and logs the action.
        """
        extension_path = "/fake/path/to/extension"

        # Call the function
        ckan_pilot.helpers.catalog.remove_editable_extension(extension_path)

        # Check if os.system was called correctly
        mock_os_system.assert_called_once_with("rm -rf {0}".format(extension_path))

        # Ensure correct logging
        mock_logger.info.assert_called_once_with("Deleted editable extension: {0}".format(extension_path))

    def test_extract_url_success(self):
        """
        Test extracting URL components successfully.

        This test verifies that the `extract_url` method correctly parses an extension
        URL and version into its individual components.
        """
        # Test data
        extension_url = "https://github.com/ckan/ckanext-example"
        extension_version = "main"

        result = ckan_pilot.helpers.catalog.extract_url(extension_url, extension_version)
        expected = ("ckan", "ckanext-example", "main", "example")
        self.assertEqual(result, expected)

    def test_extract_url_failure(self):
        """
        Test the failure scenario when extracting URL components.

        This test verifies that the `extract_url` method raises an `IndexError`
        when given an invalid URL.
        """
        # Test data
        extension_url = "not-a-valid-url"
        extension_version = "not-a-valid-version"

        with self.assertRaises(IndexError):
            ckan_pilot.helpers.catalog.extract_url(extension_url, extension_version)

    def test_retrieve_requirements_url_success(self):
        """
        Test successful retrieval of a requirements URL for a given extension.

        This test ensures that the `retrieve_requirements_url` method correctly
        constructs the requirements URL based on the given extension URL and version.
        """
        # Test data
        extension_url = "https://github.com/ckan/ckanext-example"
        extension_version = "main"
        requirements_file = "requirements.txt"

        result = ckan_pilot.helpers.catalog.retrieve_requirements_url(
            extension_url, extension_version, requirements_file
        )
        expected = "https://raw.githubusercontent.com/ckan/ckanext-example/main/requirements.txt"
        self.assertEqual(result, expected)

    def test_retrieve_requirements_url_failure(self):
        """
        Test the failure scenario when retrieving the requirements URL.

        This test verifies that an invalid URL or version raises an `IndexError`.
        """
        # Test data
        extension_url = "not-a-valid-url"
        extension_version = "nota-valid-version"
        requirements_file = "not-a-valid-file"

        with self.assertRaises(IndexError):
            ckan_pilot.helpers.catalog.retrieve_requirements_url(extension_url, extension_version, requirements_file)

    def test_retrieve_declaration_url_success(self):
        """
        Test successful retrieval of a configuration declaration URL.

        This test verifies that the `retrieve_declaration_url` method correctly
        constructs the declaration URL based on the given extension URL and version.
        """
        extension_url = "https://github.com/ckan/ckanext-example"
        extension_version = "main"

        result = ckan_pilot.helpers.catalog.retrieve_declaration_url(extension_url, extension_version)
        expected = "https://raw.githubusercontent.com/ckan/ckanext-example/main/ckanext/example/config_declaration.yaml"
        self.assertEqual(result, expected)

    def test_retrieve_declaration_url_failure(self):
        """
        Test the failure scenario when retrieving the configuration declaration URL.

        This test verifies that an invalid URL or version raises an `IndexError`.
        """
        extension_url = "not-a-valid-url"
        extension_version = "not-a-valid-branch"

        with self.assertRaises(IndexError):
            ckan_pilot.helpers.catalog.retrieve_declaration_url(extension_url, extension_version)

    def test_parse_extension_options_success(self):
        """
        Test the successful parsing of extension options.

        This test ensures that the `parse_extension_options` method correctly formats
        and generates environment variable-like output for a list of extension options.
        """
        # Test data
        options = [
            {
                "description": "This is option 1",
                "example": "option_1_example",
                "default": "value1",
                "key": "OPTION_1",
                "required": True,
            },
            {
                "description": "This is option 2",
                "example": "option_2_example",
                "default": "value2",
                "key": "OPTION_2",
                "required": False,
            },
        ]

        expected_output = """
            # DESCRIPTION: This is option 1
            # EXAMPLE: option_1_example
            # DEFAULT: value1
            OPTION_1=value1

            # DESCRIPTION: This is option 2
            # EXAMPLE: option_2_example
            # DEFAULT: value2
            # OPTION_2=value2
        """

        result = ckan_pilot.helpers.catalog.parse_extension_options(options)

        # Strip leading/trailing whitespaces for a clean comparison
        self.assertEqual(normalize_indentation(result), normalize_indentation(expected_output))

    def test_parse_extension_options_failure(self):
        """
        Test the failure scenario when parsing extension options.

        This test simulates incorrect or missing fields in the extension options
        and ensures the method does not return the expected result.
        """
        # Test data with missing or incorrect fields
        options = [
            {
                "description": "This is option 1",
                "example": "option_1_example",
                "default": "value1",
                "key": "OPTION_1",
                # Missing 'required' field
            },
            {
                "description": "This is option 2",
                "example": "option_2_example",
                "default": "value2",
                "key": "OPTION_2",
                # Missing 'required' field
            },
        ]

        # Incorrect expected output (missing some fields or wrong format)
        expected_output = """
        # DESCRIPTION: This is option 1
        # EXAMPLE: option_1_example
        # DEFAULT: value1
        OPTION_1=value1

        # DESCRIPTION: This is option 2
        # EXAMPLE: option_2_example
        # DEFAULT: value2
        OPTION_2=value2  # Missing '#' comment in this test case for failure
        """

        result = ckan_pilot.helpers.catalog.parse_extension_options(options)

        # Assert that the result does not match the incorrect expected output
        self.assertNotEqual(normalize_indentation(result), normalize_indentation(expected_output))

    @patch("ckan_pilot.helpers.catalog.get")
    def test_fetch_extension_success(self, mock_get):
        """
        Test fetching metadata of an extension from the catalog.

        This test ensures that the `fetch_extension_metadata` method returns
        the correct metadata for a given extension.

        Args:
            mock_get (MagicMock): Mocked `ckan_pilot.helpers.catalog.get` function.
        """
        # Mock catalog data
        mock_get.return_value = mock_catalog_data

        catalog_source = "mock_catalog_source"
        extension_name = "ckanext-xloader"

        result = ckan_pilot.helpers.catalog.fetch_extension_metadata(catalog_source, extension_name)

        assert result["name"] == "ckanext-xloader"
        assert result["url"] == "https://github.com/ckan/ckanext-xloader"
        assert result["version"] == "2.1.0"

    @patch("ckan_pilot.helpers.catalog.get")
    def test_fetch_extension_not_found(self, mock_get):
        """
        Test fetching a non-existing extension.

        This test verifies that when trying to fetch metadata for an extension
        that does not exist in the catalog, the function returns None.
        """
        mock_get.return_value = mock_catalog_data

        catalog_source = "mock_catalog_source"
        extension_name = "nonexistent-extension"

        result = ckan_pilot.helpers.catalog.fetch_extension_metadata(catalog_source, extension_name)
        self.assertIsNone(result)

    def setUp(self):
        """
        Set up a mock project instance.

        This method sets up a mock project object with a predefined project directory
        to be used in various tests.
        """
        self.mock_project = MagicMock()
        self.mock_project.projectdir = "/mock/path/to/project"
        self.pyproject_path = "/mock/path/to/project/pyproject.toml"

    @patch("ckan_pilot.helpers.subproc.uv_add_wrapper")
    def test_install_extension_production_mode(self, mock_uv_add_wrapper):
        """
        Test installing an extension in production mode (non-dev).

        This test verifies that when installing an extension in production mode,
        the correct `uv_add_wrapper` function is called with the correct arguments.
        """
        ckan_pilot.helpers.catalog.install_extension(
            project_dir=self.mock_project.projectdir,
            extension_url="https://github.com/ckan/ckanext-xloader",
            extension_version="2.1.0",
            dev=False,
            extension_name="ckanext-xloader",
        )

        mock_uv_add_wrapper.assert_called_once_with(
            "/mock/path/to/project",
            group="ckanext-xloader",
            target="git+https://github.com/ckan/ckanext-xloader@2.1.0",
            requirements_file=None,
            editable=None,
        )

    @patch("ckan_pilot.helpers.subproc.uv_add_wrapper", side_effect=click.Abort)
    def test_install_extension_production_failure(self, mock_uv_add_wrapper):
        """
        Test failure when installing an extension in production mode.

        This test verifies that when an invalid extension URL is passed in production mode,
        the function raises a `click.Abort` exception.
        """
        with self.assertRaises(click.Abort):
            ckan_pilot.helpers.catalog.install_extension(
                project_dir=self.mock_project.projectdir,
                extension_url="bad_url",
                extension_version="no_version",
                dev=False,
                extension_name="ckanext-xloader",
            )

    @patch("ckan_pilot.helpers.subproc.git_clone_wrapper")
    @patch("ckan_pilot.helpers.subproc.uv_add_wrapper")
    def test_install_extension_dev_mode(self, mock_uv_add_wrapper, mock_git_clone_wrapper):
        """
        Test installing an extension in development mode.

        This test verifies that when installing an extension in development mode,
        both `git_clone_wrapper` and `uv_add_wrapper` are called with the appropriate arguments.
        """
        ckan_pilot.helpers.catalog.install_extension(
            project_dir=self.mock_project.projectdir,
            extension_url="https://github.com/ckan/ckanext-xloader",
            extension_version="2.1.0",
            dev=True,
            extension_name="ckanext-xloader",
        )

        mock_git_clone_wrapper.assert_called_once_with(
            version="2.1.0",
            git_url="https://github.com/ckan/ckanext-xloader",
            extra_flags=None,
            clone_target_dir="/mock/path/to/project/extensions/ckanext-xloader",
        )

        mock_uv_add_wrapper.assert_called_once_with(
            "/mock/path/to/project",
            group="ckanext-xloader",
            target="/mock/path/to/project/extensions/ckanext-xloader",
            editable=True,
            requirements_file=None,
        )

    @patch("ckan_pilot.helpers.subproc.git_clone_wrapper", side_effect=click.Abort)
    def test_install_extension_dev_clone_failure(self, mock_git_clone_wrapper):
        """
        Test failure when cloning an extension in development mode.

        This test verifies that when an invalid extension URL is passed in development mode,
        the function raises a `click.Abort` exception.
        """
        with self.assertRaises(click.Abort):
            ckan_pilot.helpers.catalog.install_extension(
                project_dir=self.mock_project.projectdir,
                extension_url="bad_url",
                extension_version="no_version",
                dev=True,
                extension_name="ckanext-xloader",
            )

    @patch(
        "ckan_pilot.helpers.catalog.retrieve_requirements_url",
        return_value="https://mocked-requirements-url/requirements.txt",
    )
    @patch("ckan_pilot.helpers.subproc.uv_add_wrapper")
    def test_install_requirements_success(self, mock_uv_add_wrapper, mock_retrieve_url):
        """
        Test successful installation of requirements.

        This test verifies that when a valid requirements file is provided,
        the function installs the required dependencies by calling `uv_add_wrapper` with
        the correct URL and file paths.
        """
        ckan_pilot.helpers.catalog.install_requirements_file(
            project_dir=self.mock_project.projectdir,
            extension_url="https://github.com/ckan/ckanext-xloader",
            extension_version="2.1.0",
            extension_name="ckanext-xloader",
            requirements_file="requirements.txt",
            editable=False,
        )

        mock_retrieve_url.assert_called_once_with(
            "https://github.com/ckan/ckanext-xloader", "2.1.0", "requirements.txt"
        )

        mock_uv_add_wrapper.assert_called_once_with(
            "/mock/path/to/project",
            group="ckanext-xloader",
            target=None,
            editable=False,
            requirements_file="https://mocked-requirements-url/requirements.txt",
        )

    @patch(
        "ckan_pilot.helpers.catalog.retrieve_requirements_url",
        return_value="https://mocked-requirements-url/requirements.txt",
    )
    @patch(
        "ckan_pilot.helpers.subproc.uv_add_wrapper",
        side_effect=sp.CalledProcessError(1, "mock_cmd", stderr=b"mocked error"),
    )
    def test_install_requirements_failure(self, mock_uv_add_wrapper, mock_retrieve_url):
        """
        Test failure when installing requirements with invalid data.

        This test verifies that when an invalid extension URL or requirements file is provided,
        the function raises a `click.Abort` exception.
        """
        with self.assertRaises(click.Abort):
            ckan_pilot.helpers.catalog.install_requirements_file(
                project_dir=self.mock_project.projectdir,
                extension_url="https://invalid-url.com/invalid-repo",  # Invalid URL
                extension_version="999.999.999",  # Invalid version
                extension_name="bad_name",
                requirements_file="nonexistent_requirements.txt",  # Invalid requirements file
                editable=False,
            )

        mock_retrieve_url.assert_called_once()
        mock_uv_add_wrapper.assert_called_once()

    @patch(
        "ckan_pilot.helpers.catalog.retrieve_requirements_url",
        return_value="https://mocked-requirements-url/dev-requirements.txt",
    )
    @patch("ckan_pilot.helpers.subproc.uv_add_wrapper")
    def test_install_requirements_editable(self, mock_uv_add_wrapper, mock_retrieve_url):
        """
        Test installing requirements in editable mode (for dev).

        This test verifies that when installing a requirements file in editable mode,
        `uv_add_wrapper` is called with the correct editable flag and URL.
        """
        ckan_pilot.helpers.catalog.install_requirements_file(
            project_dir=self.mock_project.projectdir,
            extension_url="https://github.com/ckan/ckanext-xloader",
            extension_version="2.1.0",
            extension_name="ckanext-xloader",
            requirements_file="dev-requirements.txt",
            editable=True,
        )

        mock_retrieve_url.assert_called_once_with(
            "https://github.com/ckan/ckanext-xloader", "2.1.0", "dev-requirements.txt"
        )

        mock_uv_add_wrapper.assert_called_once_with(
            "/mock/path/to/project",
            group="ckanext-xloader",
            target=None,
            editable=True,
            requirements_file="https://mocked-requirements-url/dev-requirements.txt",
        )

    @patch("ckan_pilot.helpers.catalog.retrieve_declaration_url", return_value="https://mocked-declaration-url")
    @patch("ckan_pilot.helpers.catalog.get", return_value={"groups": [{"options": ["option1", "option2"]}]})
    @patch("ckan_pilot.helpers.catalog.parse_extension_options", return_value="mocked option output")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_configuration_file_success(self, mock_open, mock_parse, mock_get, mock_retrieve):
        """
        Test writing a configuration file successfully.

        This test verifies that when a valid extension is passed, the function
        writes the correct configuration to the file.
        """
        mock_project = type("Project", (object,), {"projectdir": "/mock/projectdir"})
        mock_extension = {
            "name": "test_extension",
            "url": "https://mocked-url",
            "version": "1.0.0",
            "configuration": {"has_config_declaration": True, "options": []},
        }
        extension_name = "test_extension"

        ckan_pilot.helpers.catalog.write_configuration_file(mock_project.projectdir, mock_extension, extension_name)

        mock_open.assert_called_once_with("/mock/projectdir/config/test_extension.ini", "w")
        mock_open().write.assert_called_once_with(
            "### test_extension ###\n\n# === Generic Settings ===\nmocked option output"
        )

    @patch("ckan_pilot.helpers.catalog.retrieve_declaration_url", return_value="https://mocked-declaration-url")
    @patch("ckan_pilot.helpers.catalog.get", return_value={"groups": [{"options": ["option1", "option2"]}]})
    @patch("ckan_pilot.helpers.catalog.parse_extension_options", return_value="mocked option output")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_configuration_file_no_declaration(self, mock_open, mock_parse, mock_get, mock_retrieve):
        """
        Test writing a configuration file when no declaration exists.

        This test verifies that when an extension has no configuration declaration,
        the function writes the correct configuration options to the file.
        """
        mock_project = type("Project", (object,), {"projectdir": "/mock/projectdir"})
        mock_extension = {
            "name": "test_extension",
            "url": "https://mocked-url",
            "version": "1.0.0",
            "configuration": {"has_config_declaration": False, "options": ["option1", "option2"]},
        }
        extension_name = "test_extension"

        ckan_pilot.helpers.catalog.write_configuration_file(mock_project.projectdir, mock_extension, extension_name)

        mock_open.assert_called_once_with("/mock/projectdir/config/test_extension.ini", "w")
        mock_open().write.assert_called_once_with("### test_extension ###\nmocked option output")

    @patch("ckan_pilot.helpers.catalog.retrieve_declaration_url", return_value="https://mocked-declaration-url")
    @patch("ckan_pilot.helpers.catalog.get", return_value={"groups": [{"options": ["option1", "option2"]}]})
    @patch("ckan_pilot.helpers.catalog.parse_extension_options", return_value="mocked option output")
    @patch("builtins.open", new_callable=mock_open)
    def test_write_configuration_file_error(self, mock_open, mock_parse, mock_get, mock_retrieve):
        """
        Test error handling when writing a configuration file.

        This test verifies that if an error occurs during the file write operation,
        a `click.Abort` exception is raised.
        """
        mock_project = type("Project", (object,), {"projectdir": "/mock/projectdir"})
        mock_extension = {
            "name": "test_extension",
            "url": "https://mocked-url",
            "version": "1.0.0",
            "configuration": {"has_config_declaration": True, "options": []},
        }
        extension_name = "test_extension"

        mock_open.side_effect = sp.CalledProcessError(1, "mock_cmd", stderr=b"mocked error")

        with self.assertRaises(click.Abort):
            ckan_pilot.helpers.catalog.write_configuration_file(mock_project, mock_extension, extension_name)

    @patch("ckan_pilot.helpers.catalog.os.path.exists")
    @patch("ckan_pilot.helpers.catalog.get_from_toml")
    def test_file_not_found(self, mock_get_from_toml, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            ckan_pilot.helpers.catalog.get_installed_extensions(self.pyproject_path)
        mock_get_from_toml.assert_not_called()

    @patch("ckan_pilot.helpers.catalog.os.path.exists", return_value=True)
    @patch("ckan_pilot.helpers.catalog.get_from_toml")
    def test_empty_dependency_groups(self, mock_get_from_toml, mock_exists):
        mock_get_from_toml.return_value = {}
        result = ckan_pilot.helpers.catalog.get_installed_extensions(self.pyproject_path)
        self.assertEqual(result, [])

    @patch("ckan_pilot.helpers.catalog.os.path.exists", return_value=True)
    @patch("ckan_pilot.helpers.catalog.get_from_toml")
    def test_ignore_dev_groups_and_envvars(self, mock_get_from_toml, mock_exists):
        mock_get_from_toml.return_value = {
            "dependency-groups": {
                "ckanext-foo-dev": ["ckanext-bar-dev"],
                "ckanext-envvars": ["ckanext-envvars"],
                "ckanext-bar": ["ckanext-bar-dev", "ckanext-envvars"],
            }
        }
        result = ckan_pilot.helpers.catalog.get_installed_extensions(self.pyproject_path, "ckanext-envvars")
        self.assertEqual(result, ["ckanext-bar"])

    @patch("ckan_pilot.helpers.catalog.os.path.exists", return_value=True)
    @patch("ckan_pilot.helpers.catalog.get_from_toml")
    def test_without_ignore_dev_groups_and_envvars(self, mock_get_from_toml, mock_exists):
        mock_get_from_toml.return_value = {
            "dependency-groups": {
                "ckanext-foo-dev": ["ckanext-bar-dev"],
                "ckanext-envvars": ["ckanext-envvars"],
                "ckanext-bar": ["ckanext-bar-dev", "ckanext-envvars"],
            }
        }
        result = ckan_pilot.helpers.catalog.get_installed_extensions(self.pyproject_path)
        self.assertEqual(result, ["ckanext-bar", "ckanext-envvars"])

    @patch("ckan_pilot.helpers.catalog.os.path.exists", return_value=True)
    @patch("ckan_pilot.helpers.catalog.get_from_toml")
    def test_parse_multiple_extensions(self, mock_get_from_toml, mock_exists):
        mock_get_from_toml.return_value = {
            "dependency-groups": {
                "ckanext-foo": ["ckanext-bar", "ckanext-baz-dev"],
                "ckanext-qux": ["other-package", "ckanext-quux"],
                "random-group": ["ckanext-random"],
            }
        }
        result = ckan_pilot.helpers.catalog.get_installed_extensions(self.pyproject_path)
        expected = ["ckanext-bar", "ckanext-baz", "ckanext-foo", "ckanext-quux", "ckanext-qux", "ckanext-random"]
        self.assertEqual(result, expected)

    @patch("ckan_pilot.helpers.catalog.os.path.exists", return_value=True)
    @patch("ckan_pilot.helpers.catalog.get_from_toml")
    def test_duplicates_and_sorting(self, mock_get_from_toml, mock_exists):
        mock_get_from_toml.return_value = {
            "dependency-groups": {
                "ckanext-foo": ["ckanext-bar", "ckanext-bar-dev", "ckanext-foo"],
                "ckanext-bar": ["ckanext-foo-dev"],
            }
        }
        result = ckan_pilot.helpers.catalog.get_installed_extensions(self.pyproject_path)
        self.assertEqual(result, ["ckanext-bar", "ckanext-foo"])

    @patch("ckan_pilot.helpers.catalog.Project")
    @patch("ckan_pilot.helpers.catalog.get")
    @patch("ckan_pilot.helpers.catalog.parse_config_declaration")
    @patch("builtins.open", new_callable=mock_open)
    @patch("ckan_pilot.helpers.catalog.logger")
    def test_write_core_ckan_configuration_success(
        self, mock_logger, mock_open_func, mock_parse, mock_get, mock_project
    ):
        # Setup mocks
        mock_project.return_value.ckan_version = "2.10"
        mock_project.return_value.projectdir = "/fake/project"

        mock_get.return_value = "yaml-content"
        mock_parse.return_value = "[ini]\nkey=value\n"

        # Call function
        ckan_pilot.helpers.catalog.write_core_ckan_configuration("/fake/project")

        # Assert correct URL requested
        mock_get.assert_called_once_with(
            "https://raw.githubusercontent.com/ckan/ckan/refs/tags/ckan-2.10/ckan/config/config_declaration.yaml"
        )

        # Assert parse called with the fetched yaml
        mock_parse.assert_called_once_with("yaml-content")

        # Assert file opened for writing core-ckan.ini
        mock_open_func.assert_called_once_with("/fake/project/config/core-ckan.ini", "w")

        # Assert write was called with correct content
        handle = mock_open_func()
        handle.write.assert_called_once_with("### CORE-CKAN ###\n[ini]\nkey=value\n")

        # Assert info log called
        mock_logger.info.assert_called_with("Core CKAN configuration written to /fake/project/config/core-ckan.ini")

    @patch("ckan_pilot.helpers.catalog.Project")
    @patch("ckan_pilot.helpers.catalog.get")
    @patch("ckan_pilot.helpers.catalog.parse_config_declaration")
    @patch("builtins.open", new_callable=mock_open)
    @patch("ckan_pilot.helpers.catalog.logger")
    def test_write_core_ckan_configuration_write_error(
        self, mock_logger, mock_open_func, mock_parse, mock_get, mock_project
    ):
        mock_project.return_value.ckan_version = "2.10"
        mock_project.return_value.projectdir = "/fake/project"
        mock_get.return_value = "yaml-content"
        mock_parse.return_value = "[ini]\nkey=value\n"

        err = sp.CalledProcessError(returncode=1, cmd="write")
        err.stderr = b"mocked error message"
        mock_open_func.side_effect = err

        with self.assertRaises(click.Abort):
            ckan_pilot.helpers.catalog.write_core_ckan_configuration("/fake/project")

        mock_logger.error.assert_called_with("Failed to write env file: /fake/project/config/core-ckan.ini")
        mock_logger.debug.assert_called_with("mocked error message")

    def write_ini(self, content):
        """Utility to create a temp INI file with content and return the file path."""
        tmp = NamedTemporaryFile("w+", delete=False)
        tmp.write(content)
        tmp.flush()
        tmp.close()
        self.addCleanup(lambda: os.remove(tmp.name))
        return tmp.name

    def read_ini(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def test_modify_existing_key(self):
        ini = self.write_ini("[app:main]\nckan.plugins = stats\n")
        ckan_pilot.helpers.catalog.set_ini_key_value_preserve_comments(ini, "app:main", "ckan.plugins", "envvars")
        content = self.read_ini(ini)
        self.assertIn("ckan.plugins = envvars", content)
        self.assertNotIn("ckan.plugins = stats", content)

    def test_insert_key_into_existing_section(self):
        ini = self.write_ini("[app:main]\n# some comment\n\n")
        ckan_pilot.helpers.catalog.set_ini_key_value_preserve_comments(ini, "app:main", "ckan.plugins", "envvars")
        content = self.read_ini(ini)
        self.assertIn("ckan.plugins = envvars", content)
        self.assertIn("[app:main]", content)
        self.assertIn("# some comment", content)

    def test_add_new_section_and_key(self):
        ini = self.write_ini("[other]\nkey = value\n")
        ckan_pilot.helpers.catalog.set_ini_key_value_preserve_comments(ini, "app:main", "ckan.plugins", "envvars")
        content = self.read_ini(ini)
        self.assertIn("[app:main]", content)
        self.assertIn("ckan.plugins = envvars", content)
        self.assertIn("[other]", content)

    def test_preserve_comments_and_formatting(self):
        ini = self.write_ini("[app:main]\n# a comment\nsome_key = some_value\n")
        ckan_pilot.helpers.catalog.set_ini_key_value_preserve_comments(ini, "app:main", "ckan.plugins", "envvars")
        content = self.read_ini(ini)
        self.assertIn("# a comment", content)
        self.assertIn("some_key = some_value", content)
        self.assertIn("ckan.plugins = envvars", content)

    def test_append_key_to_empty_section(self):
        ini = self.write_ini("[app:main]\n")
        ckan_pilot.helpers.catalog.set_ini_key_value_preserve_comments(ini, "app:main", "ckan.plugins", "envvars")
        content = self.read_ini(ini)
        self.assertIn("[app:main]", content)
        self.assertIn("ckan.plugins = envvars", content)

    def test_file_not_found_raises(self):
        with self.assertRaises(FileNotFoundError):
            ckan_pilot.helpers.catalog.set_ini_key_value_preserve_comments("/no/such/file.ini", "main", "x", "y")
