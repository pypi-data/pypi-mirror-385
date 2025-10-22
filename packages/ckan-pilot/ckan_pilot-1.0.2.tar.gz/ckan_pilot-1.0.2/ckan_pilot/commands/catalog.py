"""Manages CKAN extensions and catalogs.

Fetches, processes, and displays CKAN extension data from YAML files or URLs,
supporting multiple extension management commands.
"""

import sys

import click
from dotenv import dotenv_values
from rich import print
from rich.table import Table

from ckan_pilot.helpers import catalog
from ckan_pilot.root import CKAN_EXT_CATALOG_URL, logger


@click.group("catalog", short_help="Manages catalog")
@click.option(
    "--catalog-source",
    default=CKAN_EXT_CATALOG_URL,
    help="Path to CKAN extension catalog file or URL, default: https://extensions.ckan.app/catalog.yaml",
)
def cli(catalog_source):
    """
    Group of commands related to managing extensions.
    """
    # Store the global catalog in a context variable
    logger.debug("Using Catalog source: {0}".format(catalog))
    cli.catalog_source = catalog_source


@cli.command("list", short_help="List extensions from a YAML file")
@click.option("--installed", is_flag=True)
@click.option("--enabled", is_flag=True)
@click.pass_obj
def list_extensions(project, installed, enabled):
    """
    List available extensions in extension catalog.

    This command fetches the extensions data from a specified YAML source
    (either a file or a URL). If no source is provided, it uses the default URL
    defined in `CKAN_EXT_CATALOG_URL`. The extensions' name and description are
    displayed in a table.

    Returns:
        None
    """
    # Use the global catalog from the context
    catalog_source = cli.catalog_source

    # Determine source and load YAML
    data = catalog.get(catalog_source)

    # Set path of .env
    env_path = project.projectdir + "/compose-dev/config/ckan/.env"

    # Check if the data is empty or not loaded properly
    if not data or "extensions" not in data or not data["extensions"]:
        logger.error("No extensions found in catalog: {0}".format(catalog_source))
        return

    if enabled:
        # Read .env and store as object
        env_vars = dotenv_values(env_path)

        # Get all CKAN__PLUGINS
        current_plugins = env_vars.get("CKAN__PLUGINS", "")

        # Create a table to display extension information
        table = Table(show_header=True, show_lines=True)
        table.add_column("Name", header_style="bold", vertical="middle")
        table.add_column("Description", header_style="bold")

        # Build a lookup from catalog name → description
        extension_lookup = {ext.get("name"): ext.get("description", "").strip() for ext in data.get("extensions", [])}

        # Add each enabled plugin to the table
        for plugin in current_plugins.split():
            full_name = "ckanext-" + plugin
            description = extension_lookup.get(full_name, "") or "No description available"
            table.add_row(full_name, description)

        print(table)
        sys.exit()

    # Create a table to display extension information
    table = Table(show_header=True, show_lines=True)
    table.add_column("Name", header_style="bold", vertical="middle")
    table.add_column("Description", header_style="bold")

    if installed:
        installed_extensions_in_toml = catalog.get_installed_extensions(project.projectdir + "/pyproject.toml", None)
        # Loop through catalog and include only installed ones
        for ext in data.get("extensions", []):
            if ext.get("name") in installed_extensions_in_toml:
                name = "{}".format(ext.get("name"))
                description = "{}".format(ext.get("description", "").strip())
                table.add_row(name, description)
    else:
        # Add rows for each extension
        for ext in data.get("extensions", []):
            name = "{}".format(ext.get("name"))
            description = "{}".format(ext.get("description").strip())
            table.add_row(name, description)

    # Output table of extensions using print from rich
    print(table)


@cli.command("add", short_help="Add extensions to CKAN from catalog")
@click.option("--dev", is_flag=True)
@click.argument("extension_name", nargs=1)
@click.pass_obj
def extension_add(project, extension_name, dev):
    """
    Add a CKAN extension from the catalog.

    This command fetches the extension metadata from the catalog and installs it.
    If --dev is specified, the extension is cloned directly from its Git repository,
    instead of being installed as a packaged version.
    This allows developers to modify the source code locally while testing changes.
    The extension is installed in 'editable' mode, meaning changes take effect without needing reinstallation.

    Args:
        project (object): The CKAN project instance.
        extension_name (str): The name of the extension to add.
        dev (bool): Whether to install in development mode.
    """
    # Use the global yaml_source from the context
    catalog_source = cli.catalog_source
    extension = catalog.fetch_extension_metadata(catalog_source, extension_name)
    if not extension:
        logger.error(f"Extension '{extension_name}' not found in catalog {catalog_source}, skipping add.")
        return

    # Retrieve extension metadata
    extension_url = extension["url"]
    extension_version = extension["version"]
    # system_requirements = extension["setup"]["required_system_packages"]
    requirements = extension["setup"]["has_requirements"]
    requirements_dev = extension["setup"]["has_dev_requirements"]

    # Install the extension
    # If --dev is called it will install the extension as editable and clone it.
    catalog.install_extension(project.projectdir, extension_url, extension_version, dev, extension_name)

    # Install requirements if necessary
    if requirements:
        logger.info(f"Installing requirements for: {extension_name}")
        catalog.install_requirements_file(
            project.projectdir, extension_url, extension_version, extension_name, "requirements.txt", editable=False
        )

    if dev and requirements_dev:
        logger.info(f"Installing dev requirements for: {extension_name}")
        extension_name = extension_name + "-dev"
        catalog.install_requirements_file(
            project.projectdir, extension_url, extension_version, extension_name, "dev-requirements.txt", editable=False
        )

    # Install system requirements (Placeholder)
    # if system_requirements:
    #     logger.info("TODO: To be implemented")

    # Write configuration options to a .env file
    catalog.write_configuration_file(project.projectdir, extension, extension_name)
