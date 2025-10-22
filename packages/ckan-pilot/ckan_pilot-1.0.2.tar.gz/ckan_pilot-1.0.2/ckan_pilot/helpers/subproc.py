import os
import subprocess as sp

from ckan_pilot.root import CKAN_GH_RAW_URL_PREFIX, CKAN_GIT_URL, logger


def git_wrapper(command, extra_flags):
    sp_cmd = ["git"] + command

    if extra_flags:
        sp_cmd.append(extra_flags)

    try:
        result = sp.run(sp_cmd, capture_output=True, check=True)
        logger.debug(result.stderr.decode("utf-8"))
        return result
    except sp.CalledProcessError as err:
        logger.debug("Git command failed:\n{0}".format(err.stderr.decode("utf-8")))
        raise


def git_clone_wrapper(version, git_url, extra_flags, clone_target_dir):
    """
    Clones a Git repository using the specified version, URL, and optional flags.

    This function constructs a `git clone` command and executes it, including any
    extra flags provided. It also logs the output of the command for debugging purposes.

    Args:
        version (str): The version (branch) of the repository to clone.
        git_url (str): The URL of the Git repository to clone.
        extra_flags (list[str] | None): Additional flags to pass to the `git clone` command (default is None).
        clone_target_dir (str): The directory where the repository will be cloned.

    Raises:
        subprocess.CalledProcessError: If the `git clone` command fails.
    """
    sp_cmd = ["git", "clone", "--branch", version]

    if extra_flags:
        # adds extra flags
        sp_cmd = sp_cmd + extra_flags
    sp_cmd.append(git_url)
    sp_cmd.append(clone_target_dir)

    try:
        result = sp.run(sp_cmd, capture_output=True, check=True)
        logger.debug(result.stderr.decode("utf-8"))
    except sp.CalledProcessError as err:
        logger.debug("Git clone failed:\n{0}".format(err.stderr.decode("utf-8")))
        raise


def uv_add_wrapper(project_dir, group, target, editable, requirements_file):
    """
    Adds a specified package or requirements to a project using the `uv` command.

    This function constructs a command to add an extension, package, or requirements
    to the project. It ensures only one of `target` or `requirements_file` is provided
    at a time, and optionally installs the extension in editable mode.

    Args:
        project_dir (str): The directory of the project where the extension/package is to be added.
        group (str | None): The group under which the extension/package is categorized (default is None).
        target (str | None): The target extension/package to add (default is None).
        editable (bool | None): Whether to install the extension in editable mode (default is None).
        requirements_file (str | None): The path to a requirements file to install (default is None).

    Returns:
        subprocess.CompletedProcess: The result of the executed `uv add` command, which includes the
                                     output and return code of the command.

    Raises:
        subprocess.CalledProcessError: If the `uv add` command fails.

    Notes:
        - Either `target` or `requirements_file` must be provided, but not both.
        - `editable` must be either `True` or `False`/`None`.
    """
    sp_cmd = ["uv", "--directory", project_dir, "add"]
    if group:
        sp_cmd.append("--group")
        sp_cmd.append(group)

    if editable:
        sp_cmd.append("--editable")

    if target:
        sp_cmd.append(target)

    if requirements_file:
        sp_cmd.append("-r")
        sp_cmd.append(requirements_file)

    try:
        result = sp.run(sp_cmd, capture_output=True, check=True)
        logger.debug(result.stderr.decode("utf-8"))
        return result
    except sp.CalledProcessError as err:
        logger.debug("uv add failed:\n{0}".format(err.stderr.decode("utf-8")))
        raise


def uv_remove_wrapper(project_dir, group, target, extra_flags):
    """
    Removes a specified extension, package, or requirements from the project using the `uv remove` command.

    Args:
        project_dir (str): The directory of the project where the extension/package is to be removed.
        group (str | None): The group under which the extension/package is categorized (default is None).
        target (str | None): The target extension/package to remove (default is None).
        extra_flags (list | None): Extra flags to pass to the `uv remove` command.

    Returns:
        subprocess.CompletedProcess: The result of the executed `uv remove` command, which includes
                                     the output and return code of the command.
    """
    sp_cmd = ["uv", "--directory", project_dir, "remove", "--no-sync"]

    if group:
        sp_cmd.extend(["--group", group])

    if extra_flags:
        sp_cmd.extend(extra_flags)

    if target:
        sp_cmd.append(target)

    logger.debug("Running: {0}".format(" ".join(sp_cmd)))

    # Run the command and capture the output
    uv_remove_run = sp.run(sp_cmd, capture_output=True, text=True, check=False)

    # Log the stderr output (just like in uv_add_wrapper)
    logger.debug(uv_remove_run.stderr)

    return uv_remove_run


def ckan_cli(project_dir, generate_config, dev, prod):
    """
    Run a CKAN CLI command using the `uv` environment.

    Args:
        project_dir (str): The root directory of the CKAN project.
        generate_config (bool): If True, appends 'generate config' to the command.
        dev (bool): If True, appends 'development.ini' to the command.
        prod (bool): If True, appends 'production.ini' to the command.

    Logs:
        - Info logs on successful execution.
        - Error logs with stdout/stderr if the command fails.
        - Exception trace if an unexpected error occurs.
    """
    sp_cmd = ["uv", "run", "ckan"]

    if generate_config:
        sp_cmd.extend(["generate", "config"])

    if dev:
        sp_cmd.append("development.ini")

    if prod:
        sp_cmd.append("production.ini")

    try:
        ckan_cli_run = sp.run(sp_cmd, capture_output=True, check=True, cwd=project_dir)
        logger.info(ckan_cli_run.stdout.decode())
    except sp.CalledProcessError as e:
        logger.error("CKAN command failed with exit code %s", e.returncode)
        logger.error("Stdout:\n%s", e.stdout.decode())
        logger.error("Stderr:\n%s", e.stderr.decode())
    except FileNotFoundError:
        logger.error("Command not found: %s", sp_cmd[0])
    except Exception as e:
        logger.exception("An unexpected error occurred: %s", str(e))


def start_compose(project_dir, d, v, b, project_name, bake=None):  # noqa: PLR0913
    """
    Start Docker Compose services for the CKAN project.

    Args:
        project_dir (str): The root directory of the CKAN project.
        d (bool): Run Docker Compose in detached mode.
        v (bool): If True, remove associated volumes on interrupt in foreground mode.
        b (bool): If True, includes the `--build` flag to rebuild images.

    Returns:
        int: The return code of the Docker Compose process.

    Logs:
        - Debug logs for the command and process output.
        - Info logs on startup or interruption.
        - Error log with the return code on foreground exit.
    """

    # Subprocess command
    sp_cmd = ["docker", "compose", "-p", project_name, "up"]
    cwd = project_dir + "/compose-dev"

    if b:
        sp_cmd.append("--build")
    if d:
        sp_cmd.append("-d")

    logger.debug("Running: {0}".format(" ".join(sp_cmd)))

    if d:
        # Detached mode
        result = sp.run(sp_cmd, cwd=cwd, stdout=sp.PIPE, stderr=sp.STDOUT, text=True, check=False)
        logger.debug(result.stdout)
        logger.info("Docker Compose started in detached mode.")
        return result.returncode
    else:
        # Set bake environment variable
        env = os.environ.copy()
        if bake:
            env.update(bake)

        # Enable watch mode if ran in foreground
        sp_cmd.append("-w")

        # Foreground mode
        process = sp.Popen(sp_cmd, cwd=cwd, stdout=sp.PIPE, stderr=sp.STDOUT, text=True, bufsize=1)

        try:
            for line in process.stdout:
                print(line, end="")
                logger.debug(line.strip())
        except KeyboardInterrupt:
            logger.info("\nInterrupted by user. Cleaning up...")
            _compose_down(project_dir, v, project_name)
            process.terminate()
        finally:
            return_code = process.wait()

        # Exit code 130 typically means "terminated by Ctrl+C" (128 + SIGINT (2)) so we ignore this
        sigint_exit_code = 130
        if return_code == sigint_exit_code:
            return 0

        logger.error("Docker Compose exited with return code {0}".format(return_code))
        return return_code


def _compose_down(project_dir, v, project_name):
    """
    Stop Docker Compose services and optionally remove volumes.

    Args:
        project_dir (str): The root directory of the CKAN project.
        v (bool): If True, includes the `-v` flag to remove volumes.

    Logs:
        - Debug logs for the executed command and completion.
        - Outputs stdout/stderr from Docker if available.
        - Error logs on failure to shut down.
    """
    sp_cmd = ["docker", "compose", "-p", project_name, "down"]
    cwd = project_dir + "/compose-dev"

    if v:
        sp_cmd.append("-v")

    logger.debug("Running cleanup: {0}".format(" ".join(sp_cmd)))

    try:
        result = sp.run(sp_cmd, cwd=cwd, capture_output=True, text=True, check=False)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        logger.debug("Cleanup complete with return code {0}".format(result.returncode))
    except Exception as e:
        logger.error("Failed to clean up Docker Compose: {0}".format(e))


def add_ckan_requirements(project_dir, ckan_version):
    ckan_requirements = CKAN_GH_RAW_URL_PREFIX + ckan_version + "/requirements.txt"

    sp_cmd = ["uv", "--directory", project_dir, "add", "--group", "ckan", "-r", ckan_requirements]
    add_ckan_requirements = sp.run(sp_cmd, capture_output=True, check=True)
    logger.debug(add_ckan_requirements.stderr.decode("utf-8"))

    logger.info("\N{CHECK MARK} Add CKAN requirements to project")


def add_ckan_dev_requirements(project_dir, ckan_version):
    ckan_dev_requirements = CKAN_GH_RAW_URL_PREFIX + ckan_version + "/dev-requirements.txt"

    sp_cmd = ["uv", "--directory", project_dir, "add", "--group", "ckan-dev", "-r", ckan_dev_requirements]
    add_ckan_dev_requirements = sp.run(sp_cmd, capture_output=True, check=True)
    logger.debug(add_ckan_dev_requirements.stderr.decode("utf-8"))

    logger.info("\N{CHECK MARK} Add CKAN dev requirements to project")


def create_virtual_env(project_dir):
    # Shallow clone CKAN source code in projects virtual env and install it editable
    sp_cmd = ["uv", "--directory", project_dir, "venv"]
    create_venv = sp.run(sp_cmd, capture_output=True, check=True)
    logger.debug(create_venv.stderr.decode("utf-8"))

    logger.info("\N{CHECK MARK} Add virtual environment to project")


def setup_ckan_src(project_dir, ckan_version):
    # Shallow clone CKAN source code in projects virtual env and install it editable
    ckan_tag = "ckan-" + ckan_version
    clone_target_dir = project_dir + "/src/ckan"

    sp_cmd = ["git", "clone", "--depth", "1", "--branch", ckan_tag, CKAN_GIT_URL, clone_target_dir]
    shallow_clone_ckan = sp.run(sp_cmd, capture_output=True, check=True)
    logger.debug(shallow_clone_ckan.stderr.decode("utf-8"))

    sp_cmd = ["uv", "--directory", project_dir, "add", "--group", "ckan", "--editable", clone_target_dir]
    install_ckan = sp.run(sp_cmd, capture_output=True, check=True)
    logger.debug(install_ckan.stderr.decode("utf-8"))

    logger.info("\N{CHECK MARK} Add CKAN to project")


def sync_project(project_dir):
    # Sync ckan-pilot project
    sp_cmd = ["uv", "--directory", project_dir, "sync", "--all-groups"]
    sync_all = sp.run(sp_cmd, capture_output=True, check=True)
    logger.debug(sync_all.stderr.decode("utf-8"))

    logger.info("\N{CHECK MARK} Sync project")
