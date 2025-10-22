import subprocess as sp
import traceback
from platform import system
from shutil import which
from urllib.request import urlopen

import click

from ckan_pilot.root import logger


# Command to get the current version
@click.group("tools", short_help="Ensure required tools")
def cli():
    """Ensure required tools"""
    pass


@cli.command("list", short_help="List installed tools")
def list():
    """List installed tools and their versions"""
    uv_path = which("uv")
    if uv_path is None:
        logger.info("uv executable not found on $PATH")
    else:
        get_uv_version = sp.run(["uv", "version"], capture_output=True, check=False)
        uv_version = get_uv_version.stdout.strip().decode("utf-8")
        logger.info("{0} available on PATH at: {1}".format(uv_version, uv_path))


@cli.command("install", short_help="Install tools")
def install():
    """Install tools"""
    uv_path = which("uv")
    os_platform = system()

    if uv_path is None and os_platform in ["Linux", "Darwin"]:
        try:
            logger.info("Installing uv, please follow any additional steps from installation")
            uv_install = urlopen("https://astral.sh/uv/install.sh")
            uv_install_script = uv_install.read().decode("utf-8")
            uv_installation = sp.run([uv_install_script + " | sh"], capture_output=True, shell=True, check=True)
            logger.info(uv_installation.stdout.decode("utf-8"))
        except Exception:
            logger.error("Failed to install uv, traceback below: ")
            logger.error(traceback.format_exc())
            raise click.Abort() from None
    elif uv_path is not None and os_platform in ["Linux", "Darwin"]:
        logger.info("uv already installed: {0}".format(uv_path))
    else:
        logger.error("Unsupported platform: {0}".format(os_platform))
        raise click.Abort()
