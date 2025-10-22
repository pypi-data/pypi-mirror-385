import unittest

from click.testing import CliRunner

from ckan_pilot.root import cli


class TestVersionCommand(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_version(self):
        result = self.runner.invoke(cli, ["version"])
        self.assertIn("ckan-pilot", result.output)
        self.assertEqual(result.exit_code, 0)
