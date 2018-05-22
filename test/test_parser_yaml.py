import os
import unittest
import yaml

from odml.tools import dict_parser
from odml.tools.parser_utils import ParserException, InvalidVersionException


class TestYAMLParser(unittest.TestCase):

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.basepath = os.path.join(dir_path, "resources")

        self.yaml_reader = dict_parser.DictReader()

    def test_missing_root(self):
        filename = "missing_root.yaml"
        message = "Missing root element"

        with open(os.path.join(self.basepath, filename)) as raw_data:
            parsed_doc = yaml.load(raw_data)

        with self.assertRaises(ParserException) as exc:
            _ = self.yaml_reader.to_odml(parsed_doc)

        self.assertIn(message, str(exc.exception))

    def test_missing_version(self):
        filename = "missing_version.yaml"
        message = "Could not find odml-version"

        with open(os.path.join(self.basepath, filename)) as raw_data:
            parsed_doc = yaml.load(raw_data)

        with self.assertRaises(ParserException) as exc:
            _ = self.yaml_reader.to_odml(parsed_doc)

        self.assertIn(message, str(exc.exception))

    def test_invalid_version(self):
        filename = "invalid_version.yaml"

        with open(os.path.join(self.basepath, filename)) as raw_data:
            parsed_doc = yaml.load(raw_data)

        with self.assertRaises(InvalidVersionException):
            _ = self.yaml_reader.to_odml(parsed_doc)
