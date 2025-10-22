import os
import re

import click
import yaml

from ckan_pilot.root import logger


def extract_repo_name(repo_url):
    # Strip whitespace and trailing slash only
    repo_url = repo_url.strip().rstrip("/")

    # Match the last path component, optionally ending in .git
    match = re.search(r"[:/](?P<name>[^/]+?)(?:\.git)?$", repo_url)
    if match:
        return match.group("name")
    else:
        raise ValueError("Invalid Git URL: {0}".format(repo_url))


def write_local_config_declaration(project_dir, extension_name, config_path):
    """
    Load a local config_declaration.yaml file, parse it, and write to an INI-style config file.

    Args:
        project_dir (str): Root directory of the CKAN project.
        extension_name (str): The name of the extension (e.g. "ckanext-pages").
        config_path (str): Full path to the local config_declaration.yaml file.
    """
    if not os.path.exists(config_path):
        logger.info("Config declaration file not found: {0}".format(config_path))
        logger.info("Please add your own configuration options to .env")
        return

    try:
        with open(config_path, "r") as f:
            declaration_data = yaml.safe_load(f)
    except Exception as err:
        logger.error("Failed to load YAML from {0}".format(config_path))
        raise click.Abort() from err

    try:
        from .catalog import parse_config_declaration  # or import it at the top if same module

        config_output = parse_config_declaration(declaration_data)

        output_file = os.path.join(project_dir, "config", f"{extension_name}.ini")

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w") as f:
            f.write("### {0} ###\n".format(extension_name))
            f.write(config_output)

        logger.info("Local configuration written to {0}".format(output_file))
    except Exception as err:
        logger.error("Failed to write local config for: {0}".format(extension_name))
        raise click.Abort() from err
