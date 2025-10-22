import os
import re
import subprocess as sp
from urllib.parse import urlparse

import click
import requests
import tomllib
import yaml

from ckan_pilot.helpers import subproc
from ckan_pilot.root import Project, logger

RAW_GH_URL = "https://raw.githubusercontent.com"


def get(catalog):
    """
    Opens a CKAN extension catalog YAML file from a local path or a URL and returns its contents.

    This function handles both local file paths and URLs. If a URL is provided,
    it fetches the content from the URL. If a file path is provided, it reads
    the YAML file from disk. In case of errors, it logs the error message.

    Args:
        catalog (str): Path to a YAML file or a URL.

    Returns:
        dict: Parsed YAML data.

    Raises:
        requests.exceptions.RequestException: If there is an error fetching from the URL.
        FileNotFoundError: If the file is not found.
        yaml.YAMLError: If there is an error parsing the YAML.
        Exception: For any other unforeseen errors.
    """
    try:
        if catalog.startswith("http"):
            logger.debug("Fetching YAML from URL: {0}".format(catalog))
            response = requests.get(catalog, timeout=10)
            response.raise_for_status()  # Raise error if request fails
            return yaml.safe_load(response.text)

        logger.info("Loading YAML from file: {0}".format(catalog))
        with open(catalog, "r") as file:
            return yaml.safe_load(file)

    except requests.exceptions.RequestException as e:
        logger.error("Error fetching YAML from URL: {0}".format(catalog))
        logger.debug(e)
        raise click.Abort() from e
    except FileNotFoundError:
        logger.error("Error: File not found - {0}".format(catalog))
        raise click.Abort() from None
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML: {0}".format(catalog))
        logger.debug(e)
        raise click.Abort() from e
    except Exception as e:
        logger.error("Unexpected error: {0}".format(e))
        raise click.Abort() from e


def get_from_toml(file_path):
    """
    Opens a CKAN extension catalog TOML file from a local path and returns its contents.

    Args:
        file_path (str): Path to a TOML file.

    Returns:
        dict: Parsed TOML data.

    Raises:
        FileNotFoundError: If the file is not found.
        tomllib.TOMLDecodeError: If there is an error parsing the TOML file.
        Exception: For any other unforeseen errors.
    """
    try:
        logger.debug("Loading TOML from file: {0}".format(file_path))
        with open(file_path, "rb") as file:
            return tomllib.load(file)

    except FileNotFoundError:
        logger.error("Error: File not found - {0}".format(file_path))
        raise click.Abort() from None
    except tomllib.TOMLDecodeError as e:
        logger.error("Error parsing TOML: {0}".format(file_path))
        logger.debug(e)
        raise click.Abort() from e
    except Exception as e:
        logger.error("Unexpected error: {0}".format(e))
        raise click.Abort() from e


def get_installed_extensions(pyproject_path, excluded=None):
    """
    Parse a pyproject.toml and return a list of all installed extensions
    that start with 'ckanext-', optionally excluding certain extensions.

    :param pyproject_path: Full path to the pyproject.toml file
    :param excluded: Optional list of extension names to exclude (e.g., ["ckanext-envvars"])
    :return: Sorted list of unique ckanext-* extension names (without -dev)
    """
    if not os.path.exists(pyproject_path):
        raise FileNotFoundError("pyproject.toml not found at: {}".format(pyproject_path))

    if excluded is None:
        excluded = []

    toml_data = get_from_toml(pyproject_path)
    groups = toml_data.get("dependency-groups", {})

    ckanext_extensions = set()

    for group_name, packages in groups.items():
        if group_name.startswith("ckanext-") and group_name.endswith("-dev"):
            continue

        if group_name.startswith("ckanext-"):
            base_name = group_name.removesuffix("-dev")
            if base_name not in excluded:
                ckanext_extensions.add(base_name)

        for pkg in packages:
            match = re.match(r"^(ckanext-[\w\-]+)", pkg)
            if match:
                clean_pkg = match.group(1).removesuffix("-dev")
                if clean_pkg not in excluded:
                    ckanext_extensions.add(clean_pkg)

    return sorted(ckanext_extensions)


def strip_version(requirement):
    """
    Remove version constraints from a package string.

    This function strips version constraints (like <, >, =, ~) from package requirements
    to keep only the package name.

    Args:
        requirement (str): The package string which may include version constraints.

    Returns:
        str: The package name without version constraints.
    """
    return re.split(r"[<>=!~]", requirement)[0]


#### CHANGE DOCUMENTATION WHERE PROJECT OBJECT WAS USEED
def remove_extension(project_dir, extension_name, extension_requirements, group, extra_flags):
    """
    Removes an extension and its dependencies from the project, ensuring full cleanup.

    This function first removes the extension itself, then removes any dependencies listed
    in the provided extension requirements, making sure not to remove the extension again.

    Args:
        project_dir (str): The project directory containing project details.
        extension_name (str): The name of the extension to remove.
        extension_requirements (list): A list of dependencies required by the extension.
        group (str): The group name to associate with the dependencies.
        extra_flags (list): A list of extra flags to pass to the removal process.
    """
    clean_requirements = [strip_version(req) for req in extension_requirements]

    logger.debug("Removing extension '{0}' and its dependencies: {1}".format(extension_name, clean_requirements))

    # First, remove the extension itself
    subproc.uv_remove_wrapper(project_dir, group=extension_name, target=extension_name, extra_flags=extra_flags)

    # Now, remove the dependencies (ensure the extension itself is not removed again)
    for requirement in clean_requirements:
        if requirement != extension_name:  # Prevent duplicate removal of the extension itself
            subproc.uv_remove_wrapper(project_dir, group=group, target=requirement, extra_flags=extra_flags)


def remove_editable_extension(extension_path):
    """
    Deletes an editable extension folder.

    This function removes the specified editable extension folder from the filesystem.

    Args:
        extension_path (str): The path to the editable extension to be removed.
    """
    os.system("rm -rf {0}".format(extension_path))
    logger.info("Deleted editable extension: {0}".format(extension_path))


def extract_url(extension_url, extension_version):
    """
    Extracts repository owner, repository name, branch, and extension name from a GitHub extension URL.

    Args:
        extension_url (str): The Git repository URL of the CKAN extension.
        extension_version (str): The branch or version to use.

    Returns:
        tuple: (owner, repo, branch, extension_name) extracted from the URL.
    """
    # Extracts the owner, repo and extension name from the extension url
    parsed_url = urlparse(extension_url)
    owner = parsed_url.path[1:].split("/")[0]
    repo = parsed_url.path[1:].split("/")[1]
    branch = extension_version.strip()
    extension_name = parsed_url.path[1:].split("/")[1].removeprefix("ckanext-")

    return owner, repo, branch, extension_name


def retrieve_requirements_url(extension_url, extension_version, requirements_file):
    """
    Constructs the URL to fetch a requirements file (e.g., `requirements.txt` or `dev-requirements.txt`).

    Args:
        extension_url (str): Base URL of the extension repository.
        extension_version (str): Branch or version of the extension.
        requirements_file (str): The name of the requirements file.

    Returns:
        str: The formatted URL pointing to the `requirements` file.
    """
    owner, repo, branch, extension_name = extract_url(extension_url, extension_version)

    # Set the full url to requirements file
    return "{0}/{1}/{2}/{3}/{4}".format(RAW_GH_URL, owner, repo, branch, requirements_file)


def retrieve_declaration_url(extension_url, extension_version):
    """
    Constructs the URL for the configuration declaration file of a CKAN extension.

    Args:
        extension_url (str): Base URL of the extension repository.
        extension_version (str): Branch or version of the extension.

    Returns:
        str: The formatted URL pointing to `config_declaration.yaml`.
    """
    # Extracts the owner, repo and extension name from the extension url
    owner, repo, branch, extension_name = extract_url(extension_url, extension_version)

    # Set the full url to declaration config
    return "{0}/{1}/{2}/{3}/ckanext/{4}/config_declaration.yaml".format(RAW_GH_URL, owner, repo, branch, extension_name)


def parse_extension_options(options):
    """
    Parses a list of extension configuration options and formats them as an environment-variable-like structure.

    This function converts a list of option dictionaries into a `.env`-style formatted string,
    including descriptions, examples, and default values.

    Args:
        options (list[dict]): A list of option dictionaries, each containing keys such as
                              'description', 'example', 'default', and 'key'.

    Returns:
        str: A formatted string containing descriptions and key-value pairs for `.env` files.
    """
    env_output = ""

    for option in options:
        # Add a new line before each extension option
        env_output += "\n"

        env_output += f"# DESCRIPTION: {option.get('description', '').replace('\n', ' ')}\n"
        env_output += f"# EXAMPLE: {option.get('example', '')}\n"
        env_output += f"# DEFAULT: {option.get('default', '')}\n"

        if option.get("required", False):
            env_output += f"{option['key']}={option.get('default', '')}\n"
        else:
            env_output += f"# {option['key']}={option.get('default', '')}\n"

    return env_output


def fetch_extension_metadata(catalog_source, extension_name):
    """
    Fetch extension metadata from the catalog.

    Args:
        catalog_source (str): The catalog source to fetch from.
        extension_name (str): The name of the extension.

    Returns:
        dict or None: The extension metadata if found, else None.
    """
    data = get(catalog_source)
    for ext in data.get("extensions", []):
        if extension_name == ext.get("name"):
            return ext
    return None


def install_extension(project_dir, extension_url, extension_version, dev, extension_name):
    """
    Install the CKAN extension.

    Args:
        project_dir (str): The project directory containing project details.
        extension_url (str): The URL of the extension.
        extension_version (str): The version of the extension.
        dev (bool): Whether to install in development mode.
        extension_name (str): The name of the extension.
    """
    target = f"git+{extension_url}@{extension_version}"
    logger.info(f"Installing extension: {extension_name}")

    if not dev:
        try:
            subproc.uv_add_wrapper(
                project_dir, group=extension_name, target=target, requirements_file=None, editable=None
            )
        except sp.CalledProcessError as err:
            logger.error("Failed to install {0}".format(extension_name))
            logger.debug(err.stderr.decode("utf-8"))
            raise click.Abort() from err
    else:
        target_dir = "{0}/extensions/{1}".format(project_dir, extension_name)

        try:
            subproc.git_clone_wrapper(
                version=extension_version, git_url=extension_url, extra_flags=None, clone_target_dir=target_dir
            )
        except sp.CalledProcessError as err:
            logger.error("Failed to git clone extension: {0}".format(extension_name))
            logger.debug(err.stderr.decode("utf-8"))
            raise click.Abort() from err

        try:
            subproc.uv_add_wrapper(
                project_dir, group=extension_name, target=target_dir, editable=True, requirements_file=None
            )
        except sp.CalledProcessError as err:
            logger.error("Failed to install dev requirements for {0}".format(extension_name))
            logger.debug(err.stderr.decode("utf-8"))
            raise click.Abort() from err


def install_requirements_file(  # noqa
    project_dir, extension_url, extension_version, extension_name, requirements_file, editable=False
):
    """
    Install requirements from a given requirements file URL.

    Args:
        project_dir (str): The project directory containing project details.
        extension_url (str): The URL of the extension.
        extension_version (str): The version of the extension.
        requirements_file (str): The name of the requirements file.
        editable (bool): Whether to install in editable mode (for dev requirements).
    """
    extension_requirements_url = retrieve_requirements_url(extension_url, extension_version, requirements_file)

    try:
        subproc.uv_add_wrapper(
            project_dir,
            group=extension_name,
            target=None,
            editable=editable,
            requirements_file=extension_requirements_url,
        )
    except sp.CalledProcessError as err:
        logger.error("Failed to install {0} for extension".format(requirements_file))
        logger.debug(err.stderr.decode("utf-8"))
        raise click.Abort() from err


def parse_config_declaration(declaration):
    """
    Parse a CKAN configuration declaration and return a .ini formatted string.

    Args:
        declaration (dict): The parsed config declaration (e.g., from a YAML or JSON file).

    Returns:
        str: .ini-formatted configuration section with parsed options.
    """
    output = ""
    annotations = declaration.get("groups", [])

    for annotation in annotations:
        raw_annotation = annotation.get("annotation")

        # If annotation is None (was ~ in YAML), use "Generic Settings"
        if raw_annotation is None:
            group_name = "Generic Settings"
        else:
            group_name = raw_annotation.upper() or "UNNAMED SECTION"

        output += f"\n# === {group_name} ===\n"

        options = annotation.get("options", [])
        output += parse_extension_options(options)

    return output


def write_configuration_file(project_dir, extension, extension_name):
    """
    Write configuration options to a .env file.

    Args:
        project_dir (str): The project directory containing project details.
        extension (dict): The extension metadata.
        extension_name (str): The name of the extension.
    """
    # Start building the configuration content with a header indicating which extension it belongs to
    env_output = f"### {extension.get('name')} ###\n"

    # Check if the extension declares a remote config specification (via a config declaration URL)
    if extension.get("configuration", {}).get("has_config_declaration"):
        # Retrieve the full URL to the config declaration based on the extension's URL and version
        declaration_url = retrieve_declaration_url(extension["url"], extension["version"])

        # Fetch the config declaration (typically a JSON or YAML structure from the remote URL)
        declaration = get(declaration_url)

        # Parse the remote configuration options and append them to the output
        env_output += parse_config_declaration(declaration)
    else:
        # If there’s no external declaration, fall back to using static config options from the metadata
        env_output += parse_extension_options(extension["configuration"]["options"])

    try:
        output_file = f"{project_dir}/config/{extension_name}.ini"
        with open(output_file, "w") as f:
            f.write(env_output)
        logger.info(f"Configuration written to {output_file}")
    except sp.CalledProcessError as err:
        logger.error(f"Failed to write env file: {output_file}")
        logger.debug(err.stderr.decode("utf-8"))
        raise click.Abort() from err


def write_core_ckan_configuration(project_dir):
    """
    Fetch the CKAN core configuration declaration and write it to a config file.

    This function downloads the CKAN core configuration schema (from the official CKAN GitHub repository),
    parses it, formats it as a .ini-style configuration file, and writes the result to
    `<project_dir>/config/core-ckan.ini`.

    Args:
        project_dir (str): Path to the CKAN project directory where the config should be saved.
    """
    # Start building the configuration content for core-ckan
    env_output = "### CORE-CKAN ###\n"

    project = Project(projectdir=project_dir)
    ckan_version = project.ckan_version

    # Fetch the config declaration (YAML structure) from the CKAN GitHub release tag
    declaration = get(
        "https://raw.githubusercontent.com/ckan/ckan/refs/tags/ckan-{0}/ckan/config/config_declaration.yaml".format(
            ckan_version
        )
    )

    # Parse the declaration and convert it into .ini-style formatted text
    env_output += parse_config_declaration(declaration)

    try:
        # Define the output path and write the formatted config content to a file
        output_file = f"{project_dir}/config/core-ckan.ini"
        with open(output_file, "w") as f:
            f.write(env_output)
        logger.info(f"Core CKAN configuration written to {output_file}")
    except sp.CalledProcessError as err:
        # Handle file writing errors
        logger.error(f"Failed to write env file: {output_file}")
        logger.debug(err.stderr.decode("utf-8"))
        raise click.Abort() from err


def set_ini_key_value_preserve_comments(path_to_ini, section, key, value):
    """
    Sets a key=value in a given section of an INI file, preserving all comments and formatting.

    Args:
        path_to_ini (str): Path to the INI file.
        section (str): The section header (e.g., 'app:main').
        key (str): The configuration key to set.
        value (str): The value to assign.
    """
    if not os.path.exists(path_to_ini):
        raise FileNotFoundError(f".ini file not found: {path_to_ini}")

    with open(path_to_ini, "r", encoding="utf-8") as f:
        lines = f.readlines()

    section_header = f"[{section}]"
    in_section = False
    output_lines = []
    inserted = False

    for _i, line in enumerate(lines):
        stripped = line.strip()

        # Detect the section
        if stripped.startswith("[") and stripped.endswith("]"):
            if stripped == section_header:
                in_section = True
            else:
                # Leaving the target section
                if in_section and not inserted:
                    # Insert the key=value before exiting the section
                    output_lines.append(f"{key} = {value}\n")
                    inserted = True
                in_section = False

        # Replace existing key if found in the target section
        if in_section and not stripped.startswith("#") and "=" in stripped:
            current_key = stripped.split("=", 1)[0].strip()
            if current_key == key:
                output_lines.append(f"{key} = {value}\n")
                inserted = True
                continue

        output_lines.append(line)

    # If section was found but key wasn't inserted yet (e.g. empty section)
    if in_section and not inserted:
        output_lines.append(f"{key} = {value}\n")

    # If section was never found, add it at the end
    if not any(f"[{section}]" in line for line in lines):
        output_lines.append(f"\n[{section}]\n{key} = {value}\n")

    with open(path_to_ini, "w", encoding="utf-8") as f:
        f.writelines(output_lines)

    logger.debug(f"Set {key} = {value} in section [{section}] of {path_to_ini} (preserved comments)")
