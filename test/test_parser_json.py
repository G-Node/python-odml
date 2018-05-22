import json
import os
import unittest

from odml.tools import dict_parser
from odml.tools.parser_utils import ParserException, InvalidVersionException


class TestJSONParser(unittest.TestCase):

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.basepath = os.path.join(dir_path, "resources")

        self.json_reader = dict_parser.DictReader()

    def test_missing_root(self):
        filename = "missing_root.json"
        message = "Missing root element"

        with open(os.path.join(self.basepath, filename)) as json_data:
            parsed_doc = json.load(json_data)

        with self.assertRaises(ParserException) as exc:
            _ = self.json_reader.to_odml(parsed_doc)

        self.assertIn(message, str(exc.exception))

    def test_missing_version(self):
        filename = "missing_version.json"
        message = "Could not find odml-version"

        with open(os.path.join(self.basepath, filename)) as json_data:
            parsed_doc = json.load(json_data)

        with self.assertRaises(ParserException) as exc:
            _ = self.json_reader.to_odml(parsed_doc)

        self.assertIn(message, str(exc.exception))

    def test_invalid_version(self):
        filename = "invalid_version.json"

        with open(os.path.join(self.basepath, filename)) as json_data:
            parsed_doc = json.load(json_data)

        with self.assertRaises(InvalidVersionException):
            _ = self.json_reader.to_odml(parsed_doc)
