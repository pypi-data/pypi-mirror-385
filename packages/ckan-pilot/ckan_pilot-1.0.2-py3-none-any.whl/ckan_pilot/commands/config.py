import click

from ckan_pilot.helpers import config


@click.group("config", short_help="Manages configuration")
def cli():
    """
    CLI group for configuration management commands.
    """
    pass


@cli.command("generate", short_help="Generate .env configuration from .ini files")
@click.pass_obj
def generate_config(project):
    """
    Generate a `.env` configuration file from `.ini` files in the project.

    Reads `.ini` configuration files from the project's `config` directory,
    combines them into a single `.env` file, and writes the output to the
    `compose-dev/config/ckan/.env` directory inside the project.

    Args:
        project: The CKAN project object, expected to have a `projectdir` attribute.
    """
    preserved_keys = [
        "CKAN__PLUGINS",
        "CKAN_MAX_UPLOAD_SIZE_MB",
        "CKAN_SQLALCHEMY_URL",
        "CKAN_DATASTORE_WRITE_URL",
        "CKAN_DATASTORE_READ_URL",
        "CKAN_SOLR_URL",
        "CKAN_REDIS_URL",
        "MAINTENANCE_MODE",
        "CKAN_SITE_URL",
        "CKAN_PORT",
        "CKAN__STORAGE_PATH",
        "CKAN__WEBASSETS__PATHCKAN_SYSADMIN_NAME",
        "CKAN_SYSADMIN_PASSWORD",
        "CKAN_SYSADMIN_EMAIL",
        "CKAN_SYSADMIN_NAME",
        "CKAN_SITE_ID",
        "CKAN__RESOURCE_FORMATS",
    ]
    input_dir = project.projectdir + "/config"
    output_dir = project.projectdir + "/compose-dev/config/ckan/.env"
    config.combine_ini_files_to_env(input_dir, output_dir, preserved_keys)
