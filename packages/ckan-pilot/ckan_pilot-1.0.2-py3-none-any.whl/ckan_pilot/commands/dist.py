import os

import click
import docker

from ckan_pilot.helpers import catalog, subproc
from ckan_pilot.root import CKAN_EXT_CATALOG_URL, logger
from ckan_pilot.templates import docker as docker_template


@click.group("dist", short_help="Manages distributions")
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


@cli.command("build", short_help="Build CKAN Docker image")
@click.option(
    "--tag",
    help="Tag name for the Docker image",
)
@click.option(
    "--dev",
    help="If specified starts CKAN for local-dev",
    is_flag=True,
)
@click.pass_obj
def build(project, tag, dev):  # noqa: PLR0912 PLR0915
    """
    Build a Docker image for the CKAN project using a dynamically generated Dockerfile.

    The image is built using the local CKAN project directory and the Dockerfile generated
    based on whether the development mode is enabled.

    Args:
        project (object): The CKAN project object passed by Click. It should contain `.projectdir`
                          and `.get_project_metadata()` methods.
        tag (str): Optional. The Docker image tag to use (e.g., 'my-ckan:2.10'). If not provided,
                   it is generated from the project's metadata.
        dev (str): Optional. If specified, builds the image for local development mode.

    Raises:
        click.ClickException: If Docker build or API operations fail.
    """

    if not tag:
        tag = "{0}".format(project.get_project_metadata()[0])

    logger.debug("Setting docker image tag to {0}".format(tag))

    # Get projectdir
    projectdir = project.projectdir

    # Use the global catalog from the context
    catalog_source = cli.catalog_source

    # Dockerfile that is generated and values that are replaced
    dockerfile_content = docker_template.DOCKERFILE_CONTENT

    excluded_extensions = ["ckanext-envvars"]
    installed_extensions_in_toml = catalog.get_installed_extensions(projectdir + "/pyproject.toml", excluded_extensions)

    system_requirements = []
    before_init = []

    for ext in installed_extensions_in_toml:
        data = catalog.fetch_extension_metadata(catalog_source, ext)

        # Skip if no data is returned
        if not data:
            continue

        # --- Collect system requirements ---
        dist_data = data.get("setup", {}).get("distributions", {})
        if isinstance(dist_data, dict):
            alpine_data = dist_data.get("alpine", {})
            if isinstance(alpine_data, dict):
                system_requirements += alpine_data.get("required_system_packages", [])

        # --- Collect init-config commands ---
        init_config = data.get("setup", {}).get("init-config", [])
        if isinstance(init_config, list):
            before_init.extend(init_config)

    # Filter out duplicates
    system_requirements = list(set(system_requirements))

    # Add system requriements to dockerfile
    dockerfile_content = add_system_requirements(system_requirements, dockerfile_content)

    # Generate Dockerfile content based on mode
    if dev:
        # Generate dev ini
        logger.info("Generating dev ini...")
        subproc.ckan_cli(project.projectdir, generate_config=True, dev=True, prod=False)
        # Add envvars to ckan.plugins in ini
        catalog.set_ini_key_value_preserve_comments(
            project.projectdir + "/development.ini", "app:main", "ckan.plugins", "envvars"
        )
        # Set dev ckan.ini
        ckan_ini = "COPY development.ini /app/src/ckan/ckan.ini"
        # Set docker CMD
        cmd = '["ckan", "-c", "/app/src/ckan/ckan.ini", "run", "-p", "5000", "-H", "0.0.0.0"]'
        dockerfile_content = dockerfile_content.replace("{ckan_ini}", ckan_ini).replace("{cmd}", cmd)
    else:
        # Generate prod ini
        logger.info("Generating prod ini...")
        subproc.ckan_cli(project.projectdir, generate_config=True, dev=False, prod=True)
        # Add envvars to ckan.plugins in ini
        catalog.set_ini_key_value_preserve_comments(
            project.projectdir + "/production.ini", "app:main", "ckan.plugins", "envvars"
        )
        # Set prod ckan.ini
        ckan_ini = "COPY production.ini /app/src/ckan/ckan.ini"
        # Set docker CMD
        cmd = '["uwsgi", "--socket", "/tmp/uwsgi.sock", "--http", ":5000", "--master", "--enable-threads", "--wsgi-file", "/app/src/ckan/wsgi.py", "--lazy-apps", "-p", "2", "-L", "--vacuum", "--harakiri", "50", "--callable", "application"]'  # noqa: E501
        dockerfile_content = dockerfile_content.replace("{ckan_ini}", ckan_ini).replace("{cmd}", cmd)

    dockerfile_path = os.path.join(projectdir, "Dockerfile")

    logger.debug("Generating Dockerfile in {0}".format(projectdir))

    # Write the Dockerfile
    with open(dockerfile_path, "w") as dockerfile:
        dockerfile.write(dockerfile_content)

    # Add before-init command to the entrypoint script
    entrypoint_script_path = os.path.join(projectdir, "compose-dev", "services", "ckan", "image", "before-init.sh")
    create_entrypoint_script(entrypoint_script_path, before_init)

    client = docker.APIClient(base_url="unix://var/run/docker.sock")

    logger.debug("Building Docker image '{0}' from {1}".format(tag, projectdir))
    logger.info("Please wait while logs are being generated...")
    try:
        logs = client.build(path=projectdir, tag=tag, rm=True, decode=True, nocache=True)

        for chunk in logs:
            if "stream" in chunk:
                logger.info(chunk["stream"].strip())
            elif "error" in chunk:
                logger.error("Build error: " + chunk["error"].strip())
                raise click.ClickException("Docker build failed: " + chunk["error"].strip())

    except docker.errors.BuildError as e:
        logger.error("Build failed.")
        for err in e.build_log:
            if "stream" in err:
                logger.error(err["stream"].strip())
        raise click.ClickException("Docker build failed.") from e

    except docker.errors.APIError as e:
        logger.error("Docker API error: {0}".format(str(e)))
        logger.error("Docker build failed.")
        raise click.ClickException("Docker build failed.") from e

    logger.info("Image '{0}' built successfully.".format(tag))


def add_system_requirements(system_requirements, dockerfile_content):
    """
    Inserts system package installation commands into a Dockerfile template.

    This function takes a list of system package requirements and appends them
    to a Dockerfile's content by replacing the `{additional_system_packages}`
    placeholder with a properly formatted `RUN apk add --no-cache` command.
    If no requirements are provided, the placeholder is replaced with an empty string.

    Parameters:
        system_requirements (list of str): A list of system packages to install.
        dockerfile_content (str): The content of the Dockerfile containing a
        `{additional_system_packages}` placeholder.

    Returns:
        str: The updated Dockerfile content with system package installation
             commands inserted, or with the placeholder removed if no packages
             are specified.
    """
    if system_requirements:
        logger.info("Writing system requirements in Dockerfile...")

        additional_system_packages = "RUN apk add --no-cache"
        for i, requirement in enumerate(system_requirements):
            if len(system_requirements) == 1:
                additional_system_packages += " {}".format(requirement)
                break

            if i == 0:
                additional_system_packages += " {} \\\n".format(requirement)
            elif i < len(system_requirements) - 1:
                additional_system_packages += "\t" * 2 + "{} \\\n".format(requirement)
            else:
                additional_system_packages += "\t" * 2 + requirement

        return dockerfile_content.replace("{additional_system_packages}", additional_system_packages)
    else:
        return dockerfile_content.replace("{additional_system_packages}", "")


def create_entrypoint_script(output_path, before_init_cmds=None):
    if not before_init_cmds:
        logger.debug("No before-init commands provided, skipping entrypoint script creation.")
        script_lines = [
            "#!/bin/sh",
            "set -e",
            "",
            'echo "Running before-init commands..."',
            "# Example prerun command",
            "# ckan -c /app/src/ckan/ckan.ini db init",
        ]

    # Prepend CKAN command prefix to each command
    before_init_cmds = ["ckan -c /app/src/ckan/ckan.ini " + cmd for cmd in before_init_cmds]

    script_lines = [
        "#!/bin/sh",
        "set -e",
        "",
        'echo "Running before-init commands..."',
        "# Example prerun command",
        "# ckan -c /app/src/ckan/ckan.ini db init",
        "# Run any before-init commands",
    ]

    for cmd in before_init_cmds:
        script_lines.append(cmd)

    with open(output_path, "w") as f:
        f.write("\n".join(script_lines) + "\n")

    # Make the script executable
    os.chmod(output_path, 0o755)

    logger.debug("Entrypoint script created at: {}".format(output_path))
