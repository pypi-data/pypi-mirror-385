import unittest
from unittest.mock import MagicMock, mock_open, patch

from click.testing import CliRunner
from docker.errors import APIError, BuildError

from ckan_pilot.commands.dist import add_system_requirements, cli


class TestBuildCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.mock_project = MagicMock()
        self.mock_project.projectdir = "/fake/project"
        self.mock_project.get_project_metadata.return_value = ("my-ckan", "2.10")

    @patch("ckan_pilot.commands.dist.os.chmod")
    @patch("ckan_pilot.commands.dist.open", new_callable=mock_open)
    @patch("ckan_pilot.commands.dist.catalog.set_ini_key_value_preserve_comments")
    @patch("ckan_pilot.commands.dist.subproc.ckan_cli")
    @patch("ckan_pilot.commands.dist.docker.APIClient")
    @patch("ckan_pilot.commands.dist.catalog.fetch_extension_metadata")
    @patch("ckan_pilot.commands.dist.catalog.get_installed_extensions")
    def test_build_dev_mode(  # noqa
        self,
        mock_get_extensions,
        mock_fetch_metadata,
        mock_docker_api,
        mock_ckan_cli,
        mock_set_ini,
        mock_open_file,
        mock_chmod,
    ):
        mock_set_ini.return_value = None
        mock_client = MagicMock()
        mock_docker_api.return_value = mock_client
        mock_client.build.return_value = iter([{"stream": "Successfully built\n"}])

        mock_get_extensions.return_value = ["ckanext-test"]
        mock_fetch_metadata.return_value = {
            "setup": {
                "distributions": {"alpine": {"required_system_packages": ["bash"]}},
                "init-config": ["pages initdb"],
            }
        }

        result = self.runner.invoke(
            cli,
            ["--catalog-source", "dummy-url", "build", "--dev"],
            obj=self.mock_project,
        )
        print(result)  # For debugging purposes
        assert result.exit_code == 0
        mock_ckan_cli.assert_called_once_with("/fake/project", generate_config=True, dev=True, prod=False)
        mock_open_file.assert_any_call("/fake/project/Dockerfile", "w")
        mock_open_file.assert_any_call("/fake/project/compose-dev/services/ckan/image/before-init.sh", "w")
        mock_client.build.assert_called_once_with(
            path="/fake/project", tag="my-ckan", rm=True, decode=True, nocache=True
        )  # noqa: E501

        # Ensure the INI modification was attempted
        mock_set_ini.assert_called_once_with("/fake/project/development.ini", "app:main", "ckan.plugins", "envvars")

    @patch("ckan_pilot.commands.dist.catalog.get_installed_extensions")
    @patch("ckan_pilot.commands.dist.catalog.fetch_extension_metadata")
    @patch("ckan_pilot.commands.dist.docker.APIClient")
    @patch("ckan_pilot.commands.dist.open", new_callable=mock_open)
    @patch("ckan_pilot.commands.dist.os.chmod")
    @patch("ckan_pilot.commands.dist.subproc.ckan_cli")
    @patch("ckan_pilot.commands.dist.logger")
    @patch("ckan_pilot.commands.dist.catalog.set_ini_key_value_preserve_comments")
    def test_build_prod_mode(  # noqa
        self,
        mock_set_ini,
        mock_logger,
        mock_ckan_cli,
        mock_os_chmod,
        mock_open_file,
        mock_docker_api,
        mock_fetch_metadata,
        mock_get_extensions,
    ):
        mock_client = MagicMock()
        mock_docker_api.return_value = mock_client

        # Return stream-like logs from APIClient.build()
        mock_client.build.return_value = iter([{"stream": "Built prod image\n"}])

        mock_set_ini.return_value = None

        mock_get_extensions.return_value = ["ckanext-test"]
        mock_fetch_metadata.return_value = {
            "setup": {"distributions": {"alpine": {"required_system_packages": ["bash"]}}}
        }

        result = self.runner.invoke(cli, ["build"], obj=self.mock_project)

        self.assertEqual(result.exit_code, 0)
        mock_ckan_cli.assert_called_once_with("/fake/project", generate_config=True, dev=False, prod=True)
        mock_open_file.assert_any_call("/fake/project/Dockerfile", "w")
        mock_client.build.assert_called_once_with(
            path="/fake/project", tag="my-ckan", rm=True, decode=True, nocache=True
        )
        mock_logger.info.assert_any_call("Image 'my-ckan' built successfully.")

        # Ensure the INI modification was attempted
        mock_set_ini.assert_called_once_with("/fake/project/production.ini", "app:main", "ckan.plugins", "envvars")

    @patch("ckan_pilot.commands.dist.os.chmod")
    @patch("ckan_pilot.commands.dist.open", new_callable=mock_open)
    @patch("ckan_pilot.commands.dist.catalog.set_ini_key_value_preserve_comments")
    @patch("ckan_pilot.commands.dist.subproc.ckan_cli")
    @patch("ckan_pilot.commands.dist.docker.APIClient")
    @patch("ckan_pilot.commands.dist.catalog.fetch_extension_metadata")
    @patch("ckan_pilot.commands.dist.catalog.get_installed_extensions")
    def test_build_error(  # noqa
        self,
        mock_get_extensions,
        mock_fetch_metadata,
        mock_docker_api,
        mock_ckan_cli,
        mock_set_ini,
        mock_open_file,
        mock_os_chmod,
    ):
        mock_client = MagicMock()
        mock_docker_api.return_value = mock_client
        mock_client.build.side_effect = APIError("Boom")

        mock_set_ini.return_value = None
        mock_get_extensions.return_value = ["ckanext-test"]
        mock_fetch_metadata.return_value = {
            "setup": {"distributions": {"alpine": {"required_system_packages": ["bash"]}}}
        }

        result = self.runner.invoke(cli, ["build"], obj=self.mock_project)

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Docker build failed.", result.output)

    @patch("ckan_pilot.commands.dist.os.chmod")
    @patch("ckan_pilot.commands.dist.catalog.get_installed_extensions")
    @patch("ckan_pilot.commands.dist.catalog.fetch_extension_metadata")
    @patch("ckan_pilot.commands.dist.docker.APIClient")
    @patch("ckan_pilot.commands.dist.open", new_callable=mock_open)
    @patch("ckan_pilot.commands.dist.subproc.ckan_cli")
    @patch("ckan_pilot.commands.dist.catalog.set_ini_key_value_preserve_comments")
    def test_build_error_builderror(  # noqa
        self,
        mock_set_ini,
        mock_ckan_cli,
        mock_open_file,
        mock_docker_api,
        mock_fetch_metadata,
        mock_get_extensions,
        mock_os_chmod,
    ):  # noqa
        mock_client = MagicMock()
        mock_docker_api.return_value = mock_client
        mock_set_ini.return_value = None

        mock_error = BuildError("failed", build_log=[{"stream": "step 1/5"}, {"stream": "step 2/5"}])
        mock_client.build.side_effect = mock_error

        mock_get_extensions.return_value = ["ckanext-test"]
        mock_fetch_metadata.return_value = {
            "setup": {"distributions": {"alpine": {"required_system_packages": ["bash"]}}}
        }

        result = self.runner.invoke(cli, ["build"], obj=self.mock_project)

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Docker build failed.", result.output)

    @patch("ckan_pilot.commands.dist.os.chmod")
    @patch("ckan_pilot.commands.dist.catalog.get_installed_extensions")
    @patch("ckan_pilot.commands.dist.catalog.fetch_extension_metadata")
    @patch("ckan_pilot.commands.dist.docker.APIClient")
    @patch("ckan_pilot.commands.dist.open", new_callable=mock_open)
    @patch("ckan_pilot.commands.dist.subproc.ckan_cli")
    @patch("ckan_pilot.commands.dist.catalog.set_ini_key_value_preserve_comments")
    def test_build_with_custom_tag(  # noqa
        self,
        mock_set_ini,
        mock_ckan_cli,
        mock_open_file,
        mock_docker_api,
        mock_fetch_metadata,
        mock_get_extensions,
        mock_os_chmod,
    ):
        mock_client = MagicMock()
        mock_docker_api.return_value = mock_client

        # Simulate streaming build output
        mock_client.build.return_value = iter([{"stream": "OK\n"}])
        mock_set_ini.return_value = None

        # Fake catalog responses
        mock_get_extensions.return_value = ["ckanext-test"]
        mock_fetch_metadata.return_value = {"setup": {"distributions": {"alpine": {"required_system_packages": []}}}}

        result = self.runner.invoke(cli, ["build", "--tag", "custom-tag:latest"], obj=self.mock_project)
        print(result)

        self.assertEqual(result.exit_code, 0)
        mock_client.build.assert_called_once_with(
            path="/fake/project",
            tag="custom-tag:latest",
            rm=True,
            decode=True,
            nocache=True,
        )

    @patch("ckan_pilot.commands.dist.logger")
    def test_single_requirement(self, mock_logger):
        dockerfile_template = "FROM alpine\n{additional_system_packages}\nCMD echo Hello"
        expected = "FROM alpine\nRUN apk add --no-cache bash\nCMD echo Hello"
        result = add_system_requirements(["bash"], dockerfile_template)
        self.assertEqual(result, expected)
        mock_logger.info.assert_called_once_with("Writing system requirements in Dockerfile...")

    @patch("ckan_pilot.commands.dist.logger")
    def test_multiple_requirements(self, mock_logger):
        dockerfile_template = "FROM alpine\n{additional_system_packages}\nCMD echo Hello"
        expected = "FROM alpine\nRUN apk add --no-cache bash \\\n\t\tcurl \\\n\t\tgit\nCMD echo Hello"
        result = add_system_requirements(["bash", "curl", "git"], dockerfile_template)
        self.assertEqual(result, expected)
        mock_logger.info.assert_called_once_with("Writing system requirements in Dockerfile...")

    def test_placeholder_missing(self):
        # Should not fail even if the placeholder is not present
        dockerfile_template = "FROM alpine\nRUN something\nCMD echo Hello"
        result = add_system_requirements(["bash"], dockerfile_template)
        # Since placeholder is missing, nothing is changed
        self.assertEqual(result, dockerfile_template)
