import unittest
from unittest.mock import mock_open, patch

import click

from ckan_pilot.helpers import extensions


class TestExtractRepoName(unittest.TestCase):
    def test_valid_github_url(self):
        self.assertEqual(extensions.extract_repo_name("https://github.com/ckan/ckanext-pages.git"), "ckanext-pages")
        self.assertEqual(extensions.extract_repo_name("git@github.com:ckan/ckanext-pages.git"), "ckanext-pages")
        self.assertEqual(extensions.extract_repo_name("https://github.com/ckan/ckanext-pages/"), "ckanext-pages")
        self.assertEqual(extensions.extract_repo_name("ckan/ckanext-pages.git"), "ckanext-pages")

    def test_invalid_url(self):
        with self.assertRaises(ValueError):
            extensions.extract_repo_name("not-a-url")


class TestWriteLocalConfigDeclaration(unittest.TestCase):
    @patch("ckan_pilot.helpers.extensions.logger")
    @patch("os.path.exists", return_value=False)
    def test_config_file_not_found(self, mock_exists, mock_logger):
        extensions.write_local_config_declaration("/mock/project", "ckanext-pages", "/mock/path/config.yaml")
        mock_logger.info.assert_any_call("Config declaration file not found: /mock/path/config.yaml")
        mock_logger.info.assert_any_call("Please add your own configuration options to .env")

    @patch("ckan_pilot.helpers.extensions.logger")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="invalid: [yaml")
    def test_yaml_load_error(self, mock_file, mock_exists, mock_logger):
        with self.assertRaises(click.Abort):
            extensions.write_local_config_declaration("/mock/project", "ckanext-pages", "/mock/path/config.yaml")
        mock_logger.error.assert_any_call("Failed to load YAML from /mock/path/config.yaml")

    @patch("ckan_pilot.helpers.extensions.logger")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="key: value")
    @patch("ckan_pilot.helpers.extensions.os.makedirs")
    @patch("ckan_pilot.helpers.extensions.os.path.dirname", return_value="/mock/project/config")
    @patch("ckan_pilot.helpers.extensions.yaml.safe_load", return_value={"key": "value"})
    @patch("ckan_pilot.helpers.extensions.open", new_callable=mock_open)
    def test_successful_write(  # noqa: PLR0913
        self, mock_file, mock_safe_load, mock_dirname, mock_makedirs, mock_openfile, mock_exists, mock_logger
    ):
        # Patch parse_config_declaration to return a string
        with patch("ckan_pilot.helpers.catalog.parse_config_declaration", return_value="key=value\n"):
            extensions.write_local_config_declaration("/mock/project", "ckanext-pages", "/mock/path/config.yaml")
        mock_logger.info.assert_any_call("Local configuration written to /mock/project/config/ckanext-pages.ini")

    @patch("ckan_pilot.helpers.extensions.logger")
    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data="key: value")
    @patch("ckan_pilot.helpers.extensions.os.makedirs")
    @patch("ckan_pilot.helpers.extensions.os.path.dirname", return_value="/mock/project/config")
    @patch("ckan_pilot.helpers.extensions.yaml.safe_load", return_value={"key": "value"})
    @patch("ckan_pilot.helpers.extensions.open", new_callable=mock_open)
    def test_write_error(  # noqa: PLR0913
        self, mock_file, mock_safe_load, mock_dirname, mock_makedirs, mock_openfile, mock_exists, mock_logger
    ):
        # Patch parse_config_declaration to raise Exception
        with patch("ckan_pilot.helpers.catalog.parse_config_declaration", side_effect=Exception("fail")):
            with self.assertRaises(click.Abort):
                extensions.write_local_config_declaration("/mock/project", "ckanext-pages", "/mock/path/config.yaml")
        mock_logger.error.assert_any_call("Failed to write local config for: ckanext-pages")
