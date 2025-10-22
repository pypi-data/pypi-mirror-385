import unittest
from unittest.mock import patch

from click.testing import CliRunner

from ckan_pilot.commands.config import cli


class DummyProject:
    def __init__(self, projectdir):
        self.projectdir = projectdir


class TestConfigCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.dummy_project = DummyProject("/fake/project/path")

    @patch("ckan_pilot.helpers.config.combine_ini_files_to_env")
    def test_generate_config_calls_combine(self, mock_combine):
        result = self.runner.invoke(cli, ["generate"], obj=self.dummy_project)

        self.assertEqual(result.exit_code, 0)
        mock_combine.assert_called_once_with(
            "/fake/project/path/config",
            "/fake/project/path/compose-dev/config/ckan/.env",
            [
                "CKAN__PLUGINS",
                "CKAN_MAX_UPLOAD_SIZE_MB",
                "CKAN_SQLALCHEMY_URL",
                "CKAN_DATASTORE_WRITE_URL",
                "CKAN_DATASTORE_READ_URL",
                "CKAN_SOLR_URL",
                "CKAN_REDIS_URL",
                "MAINTENANCE_MODE",
                "CKAN_SITE_URL",
                "CKAN_PORT",
                "CKAN__STORAGE_PATH",
                "CKAN__WEBASSETS__PATHCKAN_SYSADMIN_NAME",
                "CKAN_SYSADMIN_PASSWORD",
                "CKAN_SYSADMIN_EMAIL",
                "CKAN_SYSADMIN_NAME",
                "CKAN_SITE_ID",
                "CKAN__RESOURCE_FORMATS",
            ],
        )

    def test_cli_group_has_generate_command(self):
        self.assertIn("generate", cli.commands)
