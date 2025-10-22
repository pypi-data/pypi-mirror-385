"""Manages CKAN extensions and catalogs.

Fetches, processes, and displays CKAN extension data from YAML files or URLs,
supporting multiple extension management commands.
"""

import os
import subprocess as sp

import click
from dotenv import dotenv_values, set_key
from rich import print
from rich.table import Table

from ckan_pilot.helpers import catalog, extensions, subproc
from ckan_pilot.root import CKAN_EXT_CATALOG_URL, logger

# Define CKAN .env path as a constant for reuse
CKAN_ENV_PATH = os.path.join("compose-dev", "config", "ckan", ".env")


@click.group("extensions", short_help="Manages extensions")
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
@click.option("--enabled", is_flag=True)
@click.pass_obj
def list_extensions(project, enabled):
    """
    List available extensions in extension catalog.

    This command fetches the extensions data from a specified YAML source
    (either a file or a URL). If no source is provided, it uses the default URL
    defined in `CKAN_EXT_CATALOG_URL`. The extensions' name and description are
    displayed in a table.

    Returns:
        None
    """
    # # Use the global catalog from the context
    catalog_source = cli.catalog_source

    # # Determine source and load YAML
    data = catalog.get(catalog_source)

    # Set path of .env
    env_path = os.path.join(project.projectdir, CKAN_ENV_PATH)

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
        return

    # Create a table to display extension information
    # Load installed extensions
    installed_extensions = catalog.get_installed_extensions(os.path.join(project.projectdir, "pyproject.toml"))

    # Build a name → description lookup from the catalog
    catalog_extensions = {ext.get("name"): ext.get("description", "").strip() for ext in data.get("extensions", [])}

    # Create the output table
    table = Table(show_header=True, show_lines=True)
    table.add_column("Name", header_style="bold", vertical="middle")
    table.add_column("Description", header_style="bold")

    # Loop only through installed extensions
    for ext_name in installed_extensions:
        description = catalog_extensions.get(ext_name, "")
        table.add_row(ext_name, description)

    # Print the table
    print(table)


@cli.command("add", help="Add extensions to CKAN from git")
@click.argument("extension_url", nargs=1)
@click.option(
    "-b",
    "--branch",
    default=None,
    show_default=True,
    help="Which branch/tag to use when adding. Defaults to 'main' or 'master'.",
)
@click.pass_obj
def extension_add(project, extension_url, branch):
    """
    Add a CKAN extension from a git repository.

    This command clones a CKAN extension repository into the project's extensions directory,
    attempts to install it (along with any associated requirements), and registers its config declaration.

    If no branch is specified, the command will try 'main' and then 'master' until successful.

    Args:
        project (object): The Click-passed project object, containing project metadata and directory path.
        extension_url (str): The URL of the git repository to clone.
        branch (str, optional): Specific branch or tag to use. If not provided, tries 'main' then 'master'.

    Raises:
        click.Abort: If cloning fails for all branches, installation fails, or the extension name format is invalid.
    """

    extension_name = extensions.extract_repo_name(extension_url)

    clone_target_dir = os.path.join(project.projectdir, "extensions", extension_name)

    project_dir = project.projectdir

    branches_to_try = [branch] if branch else ["main", "master"]
    clone_succeeded = False

    for b in branches_to_try:
        try:
            subproc.git_clone_wrapper(
                version=b, git_url=extension_url, extra_flags=False, clone_target_dir=clone_target_dir
            )
            clone_succeeded = True
            break  # Exit loop if clone was successful
        except sp.CalledProcessError as err:
            logger.warning(f"Failed to clone branch '{b}' for repo: {extension_url}")
            logger.debug(err.stderr.decode("utf-8"))

    if not clone_succeeded:
        logger.error(f"Failed to clone repository: {extension_url}")
        logger.error(f"Could not clone from any of the branches: {branches_to_try}")
        raise click.Abort()

    try:
        subproc.uv_add_wrapper(
            project_dir, group=extension_name, target=clone_target_dir, editable=True, requirements_file=None
        )
    except sp.CalledProcessError as err:
        logger.error("Failed to install requirements for {0}".format(extension_name))
        logger.debug(err.stderr.decode("utf-8"))
        raise click.Abort() from err

    requirements_file = os.path.join(clone_target_dir, "requirements.txt")
    has_requirements = os.path.exists(requirements_file)

    dev_requirements_file = os.path.join(clone_target_dir, "dev-requirements.txt")
    has_dev_requirements = os.path.exists(dev_requirements_file)

    if has_requirements:
        try:
            subproc.uv_add_wrapper(
                project_dir,
                group=extension_name,
                target=None,
                editable=False,
                requirements_file=requirements_file,
            )
        except sp.CalledProcessError as err:
            logger.error("Failed to install {0} for extension".format(requirements_file))
            logger.debug(err.stderr.decode("utf-8"))
            raise click.Abort() from err

    elif has_dev_requirements:
        try:
            subproc.uv_add_wrapper(
                project_dir,
                group=extension_name,
                target=None,
                editable=False,
                requirements_file=dev_requirements_file,
            )
        except sp.CalledProcessError as err:
            logger.error("Failed to install {0} for extension".format(dev_requirements_file))
            logger.debug(err.stderr.decode("utf-8"))
            raise click.Abort() from err

    # Improved error handling for extension name format
    parts = extension_name.split("-")
    extension_name_split = 2
    if len(parts) != extension_name_split:
        logger.error(f"Extension name '{extension_name}' does not follow the 'prefix-suffix' format.")
        raise click.Abort()
    config_dec = os.path.join(clone_target_dir, parts[0], parts[1], "config_declaration.yaml")

    extensions.write_local_config_declaration(project_dir, extension_name=extension_name, config_path=config_dec)
    logger.info(f"Extension '{extension_name}' successfully added.")


@cli.command("remove", short_help="Remove extensions from CKAN")
@click.option("--extra_flags", is_flag=True, default=False)
@click.argument("extension_name", nargs=1)
@click.pass_obj
def extension_remove(project, extension_name, extra_flags):
    """Removes an extension from CKAN, including dependencies and editable installations if requested.

    Args:
        project (obj): The project object passed via @click.pass_obj.
        extension_name (str): The name of the extension to be removed.
        extra_flags (bool): Flag indicating additional removal options.
        dev (bool): Flag indicating whether to remove development dependencies.

    Raises:
        click.Abort: If the operation is canceled by the user or any error occurs.
    """
    toml_data = catalog.get_from_toml(os.path.join(project.projectdir, "pyproject.toml"))

    if extension_name not in toml_data.get("dependency-groups", {}):
        logger.error("Extension '{0}' not found in pyproject.toml.".format(extension_name))
        return

    extension_requirements = toml_data["dependency-groups"][extension_name]
    extension_path = os.path.join(project.projectdir, "extensions", extension_name)
    extension_editable_location = os.path.isdir(extension_path)

    logger.debug("Extension '{0}' has dependencies: {1}".format(extension_name, extension_requirements))

    # Confirm extension removal
    if not click.confirm("Are you sure you want to remove the extension '{0}'?".format(extension_name), default=True):
        logger.info("Operation canceled.")
        return

    # Remove main extension and its dependencies
    catalog.remove_extension(project.projectdir, extension_name, extension_requirements, extension_name, extra_flags)

    # Handle editable installation
    if extension_editable_location:
        if click.confirm(
            "An editable installation of '{0}' was found. Delete it?".format(extension_name), default=False
        ):
            dev_requirements = extension_name + "-dev"
            if dev_requirements in toml_data["dependency-groups"]:
                extension_requirements = toml_data["dependency-groups"][dev_requirements]
                catalog.remove_extension(
                    project.projectdir, extension_name, extension_requirements, dev_requirements, extra_flags
                )
            catalog.remove_editable_extension(extension_path)
        else:
            logger.warning("Editable installation for '{0}' was not removed.".format(extension_name))

    # If the editable extension still exists, inform the user that manual removal may be required.
    if os.path.isdir(extension_path):
        logger.warning(
            "The editable installation at '{0}' still exists. Run the command again or manually remove it.".format(
                extension_path
            )
        )
    else:
        logger.info("Successfully deleted extension '{0}'.".format(extension_name))

    # Sync project after removal
    subproc.sync_project(project.projectdir)


@cli.command("enable", short_help="Enable CKAN extensions")
@click.argument("extension_name", nargs=1)
@click.pass_obj
def extension_enable(project, extension_name):
    """Enable a CKAN extension by modifying the CKAN__PLUGINS variable in the .env file.

    This command appends the given extension name to the CKAN__PLUGINS environment
    variable in the project's .env file, preserving the order and avoiding duplicates.

    Args:
        project: An object containing the project directory path (via click.pass_obj).
        extension_name (str): The name of the CKAN extension to enable.

    Raises:
        Logs an error and shows a user message if the .env file cannot be updated.
    """
    # Strip "ckanext-" prefix if present
    if extension_name.startswith("ckanext-"):
        extension_name = extension_name[len("ckanext-") :]

    env_path = os.path.join(project.projectdir, CKAN_ENV_PATH)

    try:
        env_vars = dotenv_values(env_path)

        current_plugins = env_vars.get("CKAN__PLUGINS", "")
        plugin_list = current_plugins.strip().split()

        if extension_name in plugin_list:
            logger.info("Extension {} already enabled.".format(extension_name))
            return

        plugin_list.append(extension_name)

        # Preserve order and uniqueness
        seen = set()
        ordered_unique_plugins = [p for p in plugin_list if not (p in seen or seen.add(p))]
        new_plugins = " ".join(ordered_unique_plugins)

        set_key(env_path, "CKAN__PLUGINS", new_plugins)
        logger.info("Enabled extension: {}".format(extension_name))

    except Exception as e:
        logger.error("Failed to enable extension: {}".format(extension_name))
        logger.debug("Exception: {}".format(e))
        logger.error("Could not update the .env file. See logs for details.")


@cli.command("disable", short_help="Disable CKAN extensions")
@click.argument("extension_name", nargs=1)
@click.pass_obj
def extension_disable(project, extension_name):
    """Disable a CKAN extension by modifying the CKAN__PLUGINS variable in the .env file.

    This command removes the given extension name from the CKAN__PLUGINS environment
    variable in the project's .env file, if it exists.

    Args:
        project: An object containing the project directory path (via click.pass_obj).
        extension_name (str): The name of the CKAN extension to disable.

    Raises:
        Logs an error and shows a user message if the .env file cannot be updated.
    """
    # Strip "ckanext-" prefix if present
    if extension_name.startswith("ckanext-"):
        extension_name = extension_name[len("ckanext-") :]

    env_path = os.path.join(project.projectdir, CKAN_ENV_PATH)

    try:
        env_vars = dotenv_values(env_path)

        current_plugins = env_vars.get("CKAN__PLUGINS", "")
        plugin_list = current_plugins.strip().split()

        if extension_name not in plugin_list:
            logger.info("Extension {} is not currently enabled.".format(extension_name))
            return

        plugin_list = [p for p in plugin_list if p != extension_name]
        new_plugins = " ".join(plugin_list)

        set_key(env_path, "CKAN__PLUGINS", new_plugins)
        logger.info("Disabled extension: {}".format(extension_name))

    except Exception as e:
        logger.error("Failed to disable extension: {}".format(extension_name))
        logger.debug("Exception: {}".format(e))
        logger.error("Could not update the .env file. See logs for details.")
