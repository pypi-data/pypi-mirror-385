"""ckan-pilot"""

import logging
import os
import pathlib

import click
import click_log
from auto_click_auto import enable_click_shell_completion
from auto_click_auto.constants import ShellType

# Supported CKAN Versions
CKAN_VERSIONS = ["2.10.8", "2.11.3"]

# Supported tools
TOOLS_SUPPORTED = ["uv"]

# CKAN Github URLs
CKAN_GIT_URL = "https://github.com/ckan/ckan"
CKAN_GH_RAW_URL_PREFIX = "https://raw.githubusercontent.com/ckan/ckan/ckan-"

# Copier CKAN project template
CKAN_PROJECT_TEMPLATE = "https://github.com/keitaroinc/ckan-project-template"

# Add ckan-pilot prefix to all envvars
CONTEXT_SETTINGS = {"auto_envvar_prefix": "CKAN_PILOT"}

# Extension catalog url
CKAN_EXT_CATALOG_URL = "https://extensions.ckan.app/catalog.yaml"

# Directory to load subcommands from
cmd_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))

# Initialize and set click-log to use logger
logger = logging.getLogger(__name__)
click_log.basic_config(logger)


# Project class to hold all project options
class Project(object):
    def __init__(self, projectdir=None, ckan_version=None, python_version=None):
        self.projectdir = os.path.abspath(projectdir or ".")
        self.ckan_version = self.__get_ckan_version(projectdir)
        self.python_version = self.__get_python_version(projectdir)
        logger.debug("Project directory: {0}".format(self.projectdir))
        logger.debug("CKAN version: {0}".format(self.ckan_version))
        logger.debug("Python version: {0}".format(self.python_version))

    def __get_version_from_file(self, file):
        file_path = pathlib.Path(file)
        if file_path.exists():
            with open(file) as f:
                version = f.read().strip()
                f.close()
        else:
            version = None
        return version

    def __get_ckan_version(self, ckan_version):
        """Get the project CKAN version from projectdir/.ckan-version"""
        ckan_ver = self.__get_version_from_file(pathlib.Path(self.projectdir) / ".ckan-version")
        return ckan_ver

    def __get_python_version(self, python_version):
        """Get the project python version from projectdir/.python-version"""
        py_ver = self.__get_version_from_file(pathlib.Path(self.projectdir) / ".python-version")
        return py_ver

    def has_virtual_env(self):
        """Check if Project has a virtual env"""
        project_venv = pathlib.Path(self.projectdir) / ".venv"
        return project_venv.exists()

    def is_ckan_pilot_project(self):
        """Check if project_dir is a ckan-pilot project and if not abort"""
        ckan_pilot_file = pathlib.Path(self.projectdir) / ".ckan-pilot"
        if not ckan_pilot_file.exists():
            logger.error("{0} is not a valid ckan-pilot project, missing .ckan-pilot?".format(self.projectdir))
            raise click.Abort()

    def has_ckan_src(self):
        """Check if CKAN source code is present in projects virtual env"""
        ckan_src_dir = pathlib.Path(self.projectdir) / "src/ckan"
        return ckan_src_dir.exists()

    def get_project_metadata(self):
        from ckan_pilot.helpers.catalog import get_from_toml  # noqa

        name = get_from_toml(os.path.join(self.projectdir, "pyproject.toml"))["project"]["name"]
        version = get_from_toml(os.path.join(self.projectdir, "pyproject.toml"))["project"]["version"]
        return name, version


# ckan-pilot main CLI class and options
# Subcommands are loaded from the commands directory
class PckanCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = os.path.join(cmd_dir, name + ".py")
        with open(fn) as f:
            code = compile(f.read(), fn, "exec")
            eval(code, ns, ns)
        return ns["cli"]


# Define top level ckan-pilot CLI
@click.command(cls=PckanCLI, context_settings=CONTEXT_SETTINGS)
@click.option("-d", "--project-dir", help="CKAN project directory", required=False)
@click_log.simple_verbosity_option(logger, default="INFO", show_default=True)
@click.pass_context
def cli(ctx, project_dir):
    """ckan-pilot CLI for managing CKAN projects"""
    enable_click_shell_completion(program_name="ckan-pilot", shells={ShellType.BASH, ShellType.ZSH, ShellType.FISH})
    ctx.obj = Project(project_dir)
