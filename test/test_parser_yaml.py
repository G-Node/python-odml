"""
This module supplies basic tests for the odml.dict_parser.DictReader
reading from yaml files.
"""

import os
import tempfile
import unittest
import yaml

from odml.tools import dict_parser
from odml.tools.parser_utils import ParserException, InvalidVersionException


class TestYAMLParser(unittest.TestCase):

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.basepath = os.path.join(dir_path, "resources")

        self.yaml_reader = dict_parser.DictReader()

        dir_name = "odml_%s" % os.path.basename(os.path.splitext(__file__)[0])
        tmp_dir_path = os.path.join(tempfile.gettempdir(), dir_name)

        if not os.path.exists(tmp_dir_path):
            os.mkdir(tmp_dir_path)

        self.tmp_dir_path = tmp_dir_path

    def _prepare_doc(self, file_name, file_content):
        file_path = os.path.join(self.tmp_dir_path, file_name)

        with open(file_path, "w") as dump_file:
            dump_file.write(file_content)

        with open(file_path) as raw_data:
            parsed_doc = yaml.safe_load(raw_data)

        return parsed_doc

    def test_missing_root(self):
        filename = "missing_root.yaml"
        message = "Missing root element"

        with open(os.path.join(self.basepath, filename)) as raw_data:
            parsed_doc = yaml.safe_load(raw_data)

        with self.assertRaises(ParserException) as exc:
            _ = self.yaml_reader.to_odml(parsed_doc)

        self.assertIn(message, str(exc.exception))

    def test_missing_version(self):
        filename = "missing_version.yaml"
        message = "Could not find odml-version"

        with open(os.path.join(self.basepath, filename)) as raw_data:
            parsed_doc = yaml.safe_load(raw_data)

        with self.assertRaises(ParserException) as exc:
            _ = self.yaml_reader.to_odml(parsed_doc)

        self.assertIn(message, str(exc.exception))

    def test_invalid_version(self):
        filename = "invalid_version.yaml"

        with open(os.path.join(self.basepath, filename)) as raw_data:
            parsed_doc = yaml.safe_load(raw_data)

        with self.assertRaises(InvalidVersionException):
            _ = self.yaml_reader.to_odml(parsed_doc)
