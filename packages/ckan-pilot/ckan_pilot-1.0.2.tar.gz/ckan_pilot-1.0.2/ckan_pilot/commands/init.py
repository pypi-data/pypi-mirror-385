import pathlib
import shutil
import subprocess as sp

import click
import copier

from ckan_pilot.helpers import catalog, checks, subproc
from ckan_pilot.root import CKAN_EXT_CATALOG_URL, CKAN_PROJECT_TEMPLATE, CKAN_VERSIONS, logger


# Clean up function to be used in case of init failure
def clean_up(dir):
    if click.confirm(f"Init failed. Do you want to delete the project directory {dir}?"):
        shutil.rmtree(dir)
        logger.info("Project directory deleted.")
    else:
        logger.info("Project directory left intact.")


# Initialize a CKAN project
@click.command("init", short_help="Initialize CKAN project")
@click.option("-n", "--project-name", help="CKAN project name", prompt="CKAN Project Name")
@click.option("--project-description", help="CKAN project description", prompt="CKAN Project description")
@click.option(
    "--ckan-version", help="CKAN version to use for project", prompt="CKAN Version", type=click.Choice(CKAN_VERSIONS)
)
@click.option(
    "-p",
    "--python-version",
    help="Python version to use",
    prompt="Python version for CKAN Project\nTo get a full list run `uv python list`\nRecommended versions: 3.9.22, 3.10.17",  # noqa: E501
)
@click.argument("project_dir", nargs=1, type=click.Path(file_okay=False, writable=True, path_type=pathlib.Path))
def cli(project_name, project_description, ckan_version, python_version, project_dir):  # noqa: PLR0915
    """Initialize a CKAN project using the Copier based CKAN project template
    from https://github.com/keitaroinc/ckan-project-template"""

    # Check that all required tools are in place otherwise Abort
    tools_required = ["uv", "git", "pg_config"]
    if not checks.check_tools(tools_required):
        raise click.Abort() from None

    # Create a dict with answers to the Copier CKAN project template
    # ref: https://github.com/keitaroinc/ckan-project-template/blob/main/copier.yaml
    template_answers = {
        "project_name": project_name,
        "project_description": project_description,
        "ckan_version": ckan_version,
        "python_version": python_version,
    }

    # Make sure to use absolute path of project_dir
    project_dir = project_dir.absolute()

    # Create CKAN project from template
    try:
        with copier.Worker(
            src_path=CKAN_PROJECT_TEMPLATE, dst_path=project_dir, data=template_answers, quiet=True
        ) as worker:
            worker.run_copy()
        logger.info("\N{CHECK MARK} CKAN project {0} created at {1}".format(project_name, project_dir))
    except FileNotFoundError:
        logger.error("CKAN Project {0} can not be created, check permissions.".format(project_dir.absolute()))
        raise click.Abort() from None
    except ValueError as err:
        logger.error(err)
        raise click.Abort() from err

    # Create a .ckan-pilot file to mark the project as a ckan-pilot managed project
    ckan_pilot_file = project_dir / ".ckan-pilot"
    ckan_pilot_file.touch(mode=0o400)

    # Represent as string the absolute path to the project directory to pass as parameter
    project_dir_abs = str(project_dir)

    # Add CKAN requirements to project
    try:
        subproc.add_ckan_requirements(project_dir_abs, ckan_version)
    except sp.CalledProcessError as err:
        logger.error("Add CKAN requirements to project failed")
        logger.debug(err.stderr.decode("utf-8"))
        clean_up(project_dir)
        raise click.Abort() from err

    # Add CKAN dev-requirements to project
    try:
        subproc.add_ckan_dev_requirements(project_dir_abs, ckan_version)
    except sp.CalledProcessError as err:
        logger.error("Add CKAN dev requirements to project failed")
        logger.debug(err.stderr.decode("utf-8"))
        clean_up(project_dir)
        raise click.Abort() from err

    # Shallow clone CKAN source code in projects virtual env and install it editable
    try:
        subproc.setup_ckan_src(project_dir_abs, ckan_version)
    except sp.CalledProcessError as err:
        logger.error("Add CKAN to project failed")
        logger.debug(err.stderr.decode("utf-8"))
        clean_up(project_dir)
        raise click.Abort() from err

    logger.info("CKAN Project {0} initialized at {1}".format(project_name, project_dir_abs))

    # Get core ckan config declaration
    catalog.write_core_ckan_configuration(project_dir)

    # Include by default ckanext-ennvars so we can load configuration from environment variables
    # Load yaml source and fetch extension metadata
    extension = catalog.fetch_extension_metadata(CKAN_EXT_CATALOG_URL, "ckanext-envvars")

    # Get extension version and url
    extension_version = extension["version"]
    extension_url = extension["url"]

    # Install ckanext-envvars
    catalog.install_extension(project_dir, extension_url, extension_version, False, "ckanext-envvars")
