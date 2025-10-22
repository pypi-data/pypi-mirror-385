import configparser
import os

import click

from ckan_pilot.helpers import subproc
from ckan_pilot.root import logger


@click.group("git", short_help="Manages git repositories")
def cli():
    """Group of commands related to managing git."""


@cli.command("init")
@click.option(
    "--git-repo",
    help="Path to remote git repository where to init submodules",
)
@click.pass_obj
def init_command(project, git_repo):
    """
    Group of commands related to managing git.
    """

    project_dir_path = project.projectdir
    extensions_folder_path = project_dir_path + "/extensions"

    cmd = ["init", project_dir_path]

    subproc.git_wrapper(cmd, None)

    if git_repo:
        cmd = ["remote", "add", "origin", git_repo]
        try:
            subproc.git_wrapper(cmd, None)
        except Exception as e:
            logger.error(f"Failed to add remote repository: {e}")
            raise click.Abort() from e

    # List all items in the extensions directory
    all_items = os.listdir(extensions_folder_path)

    # Exclude specific folders
    excluded = {".git"}
    available_extensions = [
        item for item in all_items if item not in excluded and os.path.isdir(os.path.join(extensions_folder_path, item))
    ]

    # Parse all extensions and get remote URLs from .git config file
    for extension in available_extensions:
        extension_path = os.path.join(extensions_folder_path, extension)
        git_config_path = os.path.join(extension_path, ".git", "config")

        if not os.path.exists(git_config_path):
            logger.info(f"Skipping {extension}: no .git/config found")
            continue

        config = configparser.ConfigParser()
        config.read(git_config_path)

        try:
            remote_url = config['remote "origin"']["url"]
        except KeyError:
            logger.error(f"Skipping {extension}: no remote origin URL found")
            continue

        # Add all extensions as submodules
        try:
            subproc.git_wrapper(["submodule", "add", "--force", remote_url, extension], None)
            logger.info(f"Added submodule: {extension} -> {remote_url}")
        except Exception as e:
            logger.error(f"Failed to add submodule {extension}: {e}")
            raise click.Abort() from e
