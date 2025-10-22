import click

from ckan_pilot.helpers import subproc
from ckan_pilot.root import logger


@click.command()
@click.option("--development", "--dev", is_flag=True, help="Run in development (foreground) mode.")
@click.option("-v", is_flag=True, help="Delete disks on cleanup")
@click.option("-b", is_flag=True, help="Start compose with --build")
@click.pass_obj
def cli(project, development, v, b):
    """Start the CKAN pilot project."""
    logger.info("Starting CKAN Pilot...")
    d = not development  # Detached unless --development is passed
    project_name = "{0}".format(project.get_project_metadata()[0])
    enable_bake = None

    if development:
        # If running in development mode, set the environment variable to enable bake
        enable_bake = {"COMPOSE_BAKE": "true"}

    logger.info("Starting ckan-pilot this may take a while...")

    subproc.start_compose(project.projectdir, d=d, v=v, b=b, project_name=project_name, bake=enable_bake)
