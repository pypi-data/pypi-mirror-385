import subprocess as sp

import click

from ckan_pilot.helpers import checks, subproc
from ckan_pilot.root import logger


# Sync a CKAN project
@click.command("sync", short_help="Sync CKAN project")
@click.pass_obj
def cli(project):
    """Sync a CKAN project, its dependencies, extensions and config"""
    # Check if projectdir is a ckan-pilot project and if not Abort
    project.is_ckan_pilot_project()

    # Check that all required tools are in place otherwise Abort
    tools_required = ["uv", "git", "pg_config"]
    if not checks.check_tools(tools_required):
        raise click.Abort()

    # Check if we have a virtual environment
    if not project.has_virtual_env():
        try:
            subproc.create_virtual_env(project.projectdir)
        except sp.CalledProcessError as err:
            logger.error("Failed to create a virtual environment in {0}".format(project.projectdir))
            logger.debug(err.stderr.decode("utf-8"))
            raise click.Abort() from err

    # Check if we have CKAN source code in .venv and if not add it
    if not project.has_ckan_src():
        try:
            subproc.setup_ckan_src(project.projectdir, project.ckan_version)
        except sp.CalledProcessError as err:
            logger.error("Add CKAN to project failed")
            logger.debug(err.stderr.decode("utf-8"))
            raise click.Abort() from err

    # Sync ckan-pilot project
    try:
        subproc.sync_project(project.projectdir)
    except sp.CalledProcessError as err:
        logger.error("Failed to sync project")
        logger.debug(err.stderr.decode("utf-8"))
        raise click.Abort() from err

    logger.info("CKAN project synchronized at {0}".format(project.projectdir))
