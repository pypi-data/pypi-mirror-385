from importlib.metadata import version

import click
import pyfiglet
from rich import print

from ckan_pilot.root import logger


# Command to get the current version
@click.command("version", short_help="Get current version of ckan-pilot")
@click.pass_obj
def cli(ctx):
    """Get current version of ckan-pilot"""

    # Generate ASCII art logo using pyfiglet
    logo = pyfiglet.figlet_format("CKAN-Pilot", font="slant")
    print(logo)

    logger.info("ckan-pilot " + version("ckan_pilot"))
