import os
import tempfile
import unittest
from unittest import mock
from unittest.mock import mock_open, patch

from ckan_pilot.helpers import config


class TestConfigHelpers(unittest.TestCase):
    def test_transform_key(self):
        self.assertEqual(config.transform_key("ckanext.my.extension"), "CKANEXT__MY__EXTENSION")
        self.assertEqual(config.transform_key("ckan.my.setting"), "CKAN__MY__SETTING")
        self.assertEqual(config.transform_key("other.key"), "CKAN___OTHER__KEY")
        self.assertEqual(config.transform_key("CKANEXT.test.key"), "CKANEXT__TEST__KEY")
        self.assertEqual(config.transform_key("CKAN.setting"), "CKAN__SETTING")

    def write_temp_ini_file(self, dir_path, filename, content):
        path = os.path.join(dir_path, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_parse_ini_files_basic_and_comments(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = """
### CORE-CKAN ###
# This is a comment
#ckan.my.setting = value1
ckan.my.setting2 = value2
# DESCRIPTION: should be ignored
# EXAMPLE: should be ignored
# DEFAULT: should be ignored
unknown.line = somevalue
""".strip()
            self.write_temp_ini_file(tmpdir, "test.ini", content)

            sections, order = config.parse_ini_files(tmpdir)

            self.assertEqual(order[0], "### CORE-CKAN ###")
            core_lines = sections["### CORE-CKAN ###"]

            self.assertTrue(any("# This is a comment" in line for line in core_lines))
            self.assertTrue(any(line.startswith("CKAN__MY__SETTING=") for line in core_lines))
            self.assertTrue(any(line.startswith("CKAN__MY__SETTING2=") for line in core_lines))

            for prefix in ("# DESCRIPTION:", "# EXAMPLE:", "# DEFAULT:"):
                self.assertFalse(any(line.strip().startswith(prefix) for line in core_lines))

            self.assertTrue(any(line.startswith("CKAN___UNKNOWN__LINE=") for line in core_lines))

    def test_parse_ini_files_unknown_section_and_default_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = """
### UNKNOWN-SECTION ###
key = val
""".strip()
            self.write_temp_ini_file(tmpdir, "test.ini", content)

            sections, order = config.parse_ini_files(tmpdir)
            self.assertIn("", sections)
            lines = sections[""]
            self.assertTrue(any("### UNKNOWN-SECTION ###" in line for line in lines))
            self.assertTrue(any(line.startswith("CKAN___KEY=") for line in lines))

    def test_parse_ini_files_ignores_non_ini_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.write_temp_ini_file(tmpdir, "ignore.txt", "some content")
            sections, order = config.parse_ini_files(tmpdir)
            self.assertEqual(sections, {})
            self.assertEqual(order, [])

    def test_write_env_file_writes_sections_and_comments(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sections = {
                "### CORE-CKAN ###": ["key1=value1\n", "# Comment line\n", "key2=value2\n", "\n", "#Another comment\n"],
                "### OTHER-SECTION ###": ["key3=value3\n", "#Other comment\n"],
                "": ["key4=value4\n"],
            }
            order = ["### CORE-CKAN ###", "### OTHER-SECTION ###", ""]

            output_file = os.path.join(tmpdir, "output.env")
            config.write_env_file(sections, order, output_file)

            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertTrue(content.startswith("key1=value1"))
            self.assertIn("# Comment line", content)
            self.assertIn("key3=value3", content)
            self.assertIn("key4=value4", content)

    def test_write_env_file_core_section_absent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sections = {
                "### OTHER-SECTION ###": ["key=value\n"],
            }
            order = ["### OTHER-SECTION ###"]

            output_file = os.path.join(tmpdir, "output.env")
            config.write_env_file(sections, order, output_file)

            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("key=value", content)

    def test_write_env_file_raises_and_logs(self):
        with tempfile.TemporaryDirectory() as tmpdir, mock.patch("ckan_pilot.helpers.config.logger") as mock_logger:
            sections = {"### CORE-CKAN ###": ["key=value\n"]}
            order = ["### CORE-CKAN ###"]

            # Create a directory with the output file name to force write error
            output_dir = os.path.join(tmpdir, "output.env")
            os.mkdir(output_dir)

            with self.assertRaises(IsADirectoryError):
                config.write_env_file(sections, order, output_dir)

            self.assertTrue(
                any("Error writing output file" in record[0][0] for record in mock_logger.error.call_args_list)
            )

    def test_combine_ini_files_to_env(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            ini_content = """
### CORE-CKAN ###
key=value
""".strip()
            self.write_temp_ini_file(tmpdir, "file.ini", ini_content)

            output_file = os.path.join(tmpdir, "out.env")
            config.combine_ini_files_to_env(tmpdir, output_file)

            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("CKAN___KEY=value", content)

    def test_parse_ini_files_commented_and_uncommented_keys(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_cases = [
                ("#ckanext.some.key = val", "CKANEXT__SOME__KEY"),
                ("ckan.some.key = val", "CKAN__SOME__KEY"),
                ("other.key = val", "CKAN___OTHER__KEY"),
            ]
            for line, expected_key in test_cases:
                content = f"""
### CORE-CKAN ###
{line}
""".strip()
                self.write_temp_ini_file(tmpdir, "test.ini", content)

                sections, order = config.parse_ini_files(tmpdir)
                core_lines = sections["### CORE-CKAN ###"]
                self.assertTrue(any(line.startswith(expected_key + "=") for line in core_lines))

    def test_write_env_file_error(self):
        sections = {"### CORE-CKAN ###": ["key=value\n"]}
        section_order = ["### CORE-CKAN ###"]
        with patch("builtins.open", mock_open()) as mocked_open:
            mocked_open.side_effect = IOError("Test error")
            with self.assertRaises(IOError):
                config.write_env_file(sections, section_order, "/invalid/path.env")

    def test_parse_ini_files_lines_before_any_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = """
    # DESCRIPTION: some description that should be skipped
    key = value
    """.strip()
            self.write_temp_ini_file(tmpdir, "before_section.ini", content)

            sections, order = config.parse_ini_files(tmpdir)

            self.assertIn("", sections)
            expected_line = "CKAN___KEY=value\n"
            self.assertIn(expected_line, sections[""])

    def test_extract_env_variables_existing_key(self):
        content = "CKAN__PLUGINS=some_value\nOTHER=val\n"
        with tempfile.NamedTemporaryFile("w+", delete=True) as tf:
            tf.write(content)
            tf.flush()

            result = config.extract_env_variables(tf.name, ["CKAN__PLUGINS"])
            self.assertEqual(result, {"CKAN__PLUGINS": "some_value"})

    def test_extract_env_variables_key_not_found(self):
        content = "OTHER=val\n"
        with tempfile.NamedTemporaryFile("w+", delete=True) as tf:
            tf.write(content)
            tf.flush()

            result = config.extract_env_variables(tf.name, ["CKAN__PLUGINS"])
            self.assertEqual(result, {})

    def test_extract_env_variables_file_not_exist(self):
        result = config.extract_env_variables("/non/existent/path.env", ["CKAN__PLUGINS"])
        self.assertEqual(result, {})

    @patch("ckan_pilot.helpers.config.parse_ini_files")
    @patch("ckan_pilot.helpers.config.extract_env_variables")
    @patch("ckan_pilot.helpers.config.write_env_file")
    def test_combine_ini_files_to_env_preserves_plugins(self, mock_write_env, mock_extract_env, mock_parse_ini):
        # Setup mocks
        mock_parse_ini.return_value = (
            {
                "### CORE-CKAN ###": ["SOME_KEY=val\n", "CKAN__PLUGINS=old_plugins\n", "ANOTHER=val2\n"],
                "### OTHER ###": ["KEY=val\n"],
            },
            ["### CORE-CKAN ###", "### OTHER ###"],
        )

        mock_extract_env.return_value = {"CKAN__PLUGINS": "preserved_plugins"}

        input_dir = "/fake/input"
        output_file = "/fake/output.env"

        preserved_keys = ["CKAN__PLUGINS"]

        config.combine_ini_files_to_env(input_dir, output_file, preserved_keys)

        # Confirm parse_ini_files was called correctly
        mock_parse_ini.assert_called_once_with(input_dir)

        # Confirm extract_env_variables called with correct args
        mock_extract_env.assert_called_once_with(output_file, preserved_keys)

        # Confirm write_env_file called with modified sections
        called_sections = mock_write_env.call_args[0][0]
        called_order = mock_write_env.call_args[0][1]
        called_output_file = mock_write_env.call_args[0][2]

        self.assertIn("### CORE-CKAN ###", called_sections)
        core_lines = called_sections["### CORE-CKAN ###"]

        # Confirm old CKAN__PLUGINS line was replaced
        self.assertFalse(
            any(
                line.strip().startswith("CKAN__PLUGINS=") and line.strip() != "CKAN__PLUGINS=preserved_plugins"
                for line in core_lines
            )
        )

        # Confirm new CKAN__PLUGINS line is present
        self.assertTrue(any(line.strip() == "CKAN__PLUGINS=preserved_plugins" for line in core_lines))

        self.assertEqual(called_order[0], "### CORE-CKAN ###")
        self.assertEqual(called_output_file, output_file)

    @patch("ckan_pilot.helpers.config.parse_ini_files")
    @patch("ckan_pilot.helpers.config.extract_env_variables")
    @patch("ckan_pilot.helpers.config.write_env_file")
    def test_combine_ini_files_to_env_no_plugins(self, mock_write_env, mock_extract_env, mock_parse_ini):
        # Setup mocks - no plugins found in output_file
        mock_parse_ini.return_value = {"### CORE-CKAN ###": ["KEY=val\n"]}, ["### CORE-CKAN ###"]
        mock_extract_env.return_value = None

        input_dir = "/fake/input"
        output_file = "/fake/output.env"

        config.combine_ini_files_to_env(input_dir, output_file)

        # Confirm write_env_file called with original sections (no changes)
        called_sections = mock_write_env.call_args[0][0]
        self.assertEqual(called_sections, {"### CORE-CKAN ###": ["KEY=val\n"]})

        # Confirm write_env_file called once
        mock_write_env.assert_called_once()
