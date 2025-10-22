import click

from ckan_pilot.helpers import subproc
from ckan_pilot.root import logger


@click.command()
@click.option("-v", is_flag=True, help="Delete disks on cleanup")
@click.pass_obj
def cli(project, v):
    """Stop the CKAN pilot project."""
    logger.info("Stopping CKAN Pilot...")

    project_name = "{0}".format(project.get_project_metadata()[0])

    subproc._compose_down(project.projectdir, v=v, project_name=project_name)
