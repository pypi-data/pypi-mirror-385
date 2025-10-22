import os
import re

from ckan_pilot.root import logger


def transform_key(key: str) -> str:
    """
    Transform an INI-style config key into an environment variable style key.

    The transformation rules are:
    - Keys starting with 'ckanext.' become 'CKANEXT__' plus the uppercase remainder,
      with '.' replaced by '__'.
    - Keys starting with 'ckan.' become 'CKAN__' plus the uppercase remainder,
      with '.' replaced by '__'.
    - All other keys become 'CKAN___' plus the uppercase key,
      with '.' replaced by '__'.

    Args:
        key (str): The original configuration key.

    Returns:
        str: The transformed environment variable style key.
    """
    key_lower = key.lower()
    if key_lower.startswith("ckanext."):
        return "CKANEXT__" + key[8:].upper().replace(".", "__")
    elif key_lower.startswith("ckan."):
        return "CKAN__" + key[5:].upper().replace(".", "__")
    else:
        return "CKAN___" + key.upper().replace(".", "__")


def parse_ini_files(input_dir):  # noqa: PLR0912 PLR0915
    """
    Parse all `.ini` files in a directory, extracting settings grouped by sections.

    Sections are recognized by header lines matching `### SECTION ###`.
    Known sections (e.g. "### CORE-CKAN ###") are prioritized and preserved in order.
    Settings lines can be commented or uncommented. Comments like
    `# DESCRIPTION:`, `# EXAMPLE:`, and `# DEFAULT:` are ignored.
    Settings keys are transformed using `transform_key`.

    Args:
        input_dir (str): Path to the directory containing `.ini` files.

    Returns:
        tuple: (sections, section_order)
            - sections (dict): Mapping section header -> list of processed lines.
            - section_order (list): Ordered list of section headers as encountered.
    """
    setting_line_commented_regex = re.compile(r"^#\s*([A-Za-z0-9_.-]+)\s*=(.*)$")
    setting_line_uncommented_regex = re.compile(r"^([A-Za-z0-9_.-]+)\s*=(.*)$")
    section_header_regex = re.compile(r"^(###\s*[^#]+###)$")
    ignore_comment_prefixes = ("# DESCRIPTION:", "# EXAMPLE:", "# DEFAULT:")

    known_sections = {"### CORE-CKAN ###"}

    sections = {}
    section_order = []
    current_section = None

    for filename in sorted(os.listdir(input_dir)):
        if not filename.endswith(".ini"):
            continue
        filepath = os.path.join(input_dir, filename)
        with open(filepath, "r", encoding="utf-8") as infile:
            for line in infile:
                stripped_line = line.rstrip("\r\n")  # Remove newline chars only
                stripped = stripped_line.strip()

                section_match = section_header_regex.match(stripped)
                if section_match:
                    section_candidate = section_match.group(1)
                    if section_candidate in known_sections:
                        current_section = section_candidate
                        if current_section not in sections:
                            sections[current_section] = []
                            section_order.append(current_section)
                        sections[current_section].append(stripped_line + "\n")
                        continue
                    else:
                        # Treat unknown ### ... ### lines as normal lines inside current_section
                        pass

                if current_section is None:
                    if stripped == "" or any(stripped.startswith(prefix) for prefix in ignore_comment_prefixes):
                        continue
                    current_section = ""
                    if current_section not in sections:
                        sections[current_section] = []
                        section_order.append(current_section)

                if any(stripped.startswith(prefix) for prefix in ignore_comment_prefixes):
                    continue

                if stripped.startswith("#") and not setting_line_commented_regex.match(stripped):
                    sections[current_section].append(stripped_line + "\n")
                    continue

                match_commented = setting_line_commented_regex.match(stripped)
                if match_commented:
                    key = match_commented.group(1).strip()
                    val = match_commented.group(2).strip()
                    new_key = transform_key(key)
                    new_line = f"{new_key}={val}\n"
                    sections[current_section].append(new_line)
                    continue

                match_uncommented = setting_line_uncommented_regex.match(stripped)
                if match_uncommented:
                    key = match_uncommented.group(1).strip()
                    val = match_uncommented.group(2).strip()
                    new_key = transform_key(key)
                    new_line = f"{new_key}={val}\n"
                    sections[current_section].append(new_line)
                    continue

                sections[current_section].append(stripped_line + "\n")

    return sections, section_order


def write_env_file(sections, section_order, output_file):
    """
    Write combined environment variable settings to a `.env` file.

    The '### CORE-CKAN ###' section, if present, is always written first.
    Other sections are written preserving the original order.
    Blank lines are added before comment lines except at the file start.
    Unnamed (empty) sections are written last.

    Args:
        sections (dict): Mapping of section headers to lists of config lines.
        section_order (list): List defining the order of sections.
        output_file (str): Path to the output `.env` file to write.
    """
    core_section = None
    for sec in section_order:
        if sec.strip("# ").upper() == "CORE-CKAN":
            core_section = sec
            break

    try:
        with open(output_file, "w", encoding="utf-8") as outfile:
            first_line_written = False  # Track if anything has been written yet

            def write_section(lines):
                nonlocal first_line_written
                for line in lines:
                    stripped = line.strip()
                    if stripped == "":
                        continue

                    if stripped.startswith("#"):
                        # Add blank line before comment except if it's first line in the file
                        if first_line_written:
                            outfile.write("\n")
                        outfile.write(line.rstrip("\r\n") + "\n")
                        outfile.write("\n")
                    else:
                        outfile.write(line.rstrip("\r\n") + "\n")

                    first_line_written = True

            # Write CORE-CKAN first
            if core_section:
                logger.debug("Writing CORE-CKAN section first")
                write_section(sections[core_section])

            other_sections = [sec for sec in section_order if sec not in (core_section, "")]

            if core_section and other_sections:
                outfile.write("\n")

            for i, sec in enumerate(other_sections):
                logger.debug("Writing section: %s", sec)
                write_section(sections[sec])
                if i < len(other_sections) - 1:
                    outfile.write("\n")

            if "" in sections:
                if core_section or other_sections:
                    outfile.write("\n")
                logger.debug("Writing unnamed section")
                write_section(sections[""])

        logger.info("Output written to: %s", output_file)

    except Exception as e:
        logger.error("Error writing output file %s: %s", output_file, e)
        raise


def extract_env_variables(filepath, keys):
    """
    Extract specific environment variables from a file.

    Args:
        filepath (str): Path to the `.env` file.
        keys (list of str): Environment variable keys to extract.

    Returns:
        dict: A dictionary of {key: value} for found variables.
    """
    result = {}
    if not os.path.exists(filepath):
        return result

    keys_set = set(keys)

    with open(filepath, "r") as f:
        for line in f:
            stripped = line.strip()
            if "=" in stripped:
                k, v = stripped.split("=", 1)
                if k in keys_set:
                    result[k] = v
    return result


def combine_ini_files_to_env(input_dir, output_file, preserved_keys=None):
    """
    Combines .ini files into a single .env file, preserving specified keys.

    Args:
        input_dir (str): Directory containing .ini files.
        output_file (str): Output .env file path.
        preserved_keys (list of str): Environment variable keys to preserve.
    """
    logger.debug("Starting combination of ini files from %s into %s", input_dir, output_file)

    sections, section_order = parse_ini_files(input_dir)

    preserved_keys = preserved_keys or []
    preserved_values = extract_env_variables(output_file, preserved_keys)

    if preserved_values:
        logger.debug("Preserved variables: %s", preserved_values)
        if "### CORE-CKAN ###" not in section_order:
            section_order.insert(0, "### CORE-CKAN ###")
            sections.setdefault("### CORE-CKAN ###", [])

        core_section = sections.get("### CORE-CKAN ###", [])

        for key, value in preserved_values.items():
            # Remove existing key
            core_section = [line for line in core_section if not line.strip().startswith(f"{key}=")]
            # Append new preserved line
            core_section.append(f"{key}={value}\n")

        sections["### CORE-CKAN ###"] = core_section

    write_env_file(sections, section_order, output_file)
