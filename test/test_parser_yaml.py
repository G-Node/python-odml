"""
This module supplies basic tests for the odml.dict_parser.DictReader
reading from yaml files.
"""

import os
import shutil
import unittest
import yaml

from odml.tools import dict_parser
from odml.tools.parser_utils import ParserException, InvalidVersionException
from .util import create_test_dir, TEST_RESOURCES_DIR as RES_DIR


_INVALID_ATTRIBUTE_HANDLING_DOC = """
Document:
  id: 82408bdb-1d9d-4fa9-b4dd-ad78831c797c
  %s: i_do_not_exist_on_doc_level
  sections:
  - id: d4f3120a-c02f-4102-a9fe-2e8b77d1d0d2
    name: sec
    %s: i_do_not_exist_on_sec_level
    properties:
    - id: 18ad5176-2b46-4a08-9b85-eafd6b14fab7
      name: prop
      value: []
      %s: i_do_not_exist_on_prop_level
    sections: []
    type: test
odml-version: '1.1'
""".strip()

_SEC_CREATION_ERROR_DOC = """
Document:
  id: 82408bdb-1d9d-4fa9-b4dd-ad78831c797c
  sections:
  - id: 1111a20a-c02f-4102-a9fe-2e8b77d1d0d2
    name: sec
    sections:
    - id: 1121a20a-c02f-4102-a9fe-2e8b77d1d0d2
      name: %s
      type: test
    - id: [I-am-so-kaputt]
      name: %s
    type: test
odml-version: '1.1'
""".strip()

_PROP_CREATION_ERROR_DOC = """
Document:
  id: 82408bdb-1d9d-4fa9-b4dd-ad78831c797c
  sections:
  - id: 1111a20a-c02f-4102-a9fe-2e8b77d1d0d2
    name: sec
    properties:
    - id: 1121a20a-c02f-4102-a9fe-2e8b77d1d0d2
      name: valid_prop
    - id: 1121a20a-c02f-4102-a9fe-2e8b77d1d0d2
      name: invalid_prop
      type: int
      values:
      - 'a'
      - 'b'
    type: test
odml-version: '1.1'
""".strip()


class TestYAMLParser(unittest.TestCase):

    def setUp(self):
        self.base_path = RES_DIR
        self.yaml_reader = dict_parser.DictReader(show_warnings=False)
        self.tmp_dir_path = create_test_dir(__file__)

    def tearDown(self):
        if self.tmp_dir_path and os.path.exists(self.tmp_dir_path):
            shutil.rmtree(self.tmp_dir_path)

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

        with open(os.path.join(self.base_path, filename)) as raw_data:
            parsed_doc = yaml.safe_load(raw_data)

        with self.assertRaises(ParserException) as exc:
            _ = self.yaml_reader.to_odml(parsed_doc)

        self.assertIn(message, str(exc.exception))

    def test_missing_version(self):
        filename = "missing_version.yaml"
        message = "Could not find odml-version"

        with open(os.path.join(self.base_path, filename)) as raw_data:
            parsed_doc = yaml.safe_load(raw_data)

        with self.assertRaises(ParserException) as exc:
            _ = self.yaml_reader.to_odml(parsed_doc)

        self.assertIn(message, str(exc.exception))

    def test_invalid_version(self):
        filename = "invalid_version.yaml"

        with open(os.path.join(self.base_path, filename)) as raw_data:
            parsed_doc = yaml.safe_load(raw_data)

        with self.assertRaises(InvalidVersionException):
            _ = self.yaml_reader.to_odml(parsed_doc)

    def test_invalid_attribute_handling(self):
        filename = "invalid_attributes.yaml"

        inv_doc_attr = "invalid_doc_attr"
        inv_sec_attr = "invalid_sec_attr"
        inv_prop_attr = "invalid_prop_attr"

        file_content = _INVALID_ATTRIBUTE_HANDLING_DOC % (inv_doc_attr, inv_sec_attr, inv_prop_attr)

        parsed_doc = self._prepare_doc(filename, file_content)

        # Test ParserException on default parse
        exc_msg = "Invalid element"
        with self.assertRaises(ParserException) as exc:
            _ = self.yaml_reader.to_odml(parsed_doc)
        self.assertIn(exc_msg, str(exc.exception))

        # Test success on ignore_error parse
        self.yaml_reader.ignore_errors = True
        doc = self.yaml_reader.to_odml(parsed_doc)

        self.assertEqual(len(doc.sections), 1)
        self.assertEqual(len(doc.sections["sec"].properties), 1)

        self.assertEqual(len(self.yaml_reader.warnings), 3)
        for msg in self.yaml_reader.warnings:
            self.assertIn("Error", msg)
            self.assertTrue(inv_doc_attr in msg or inv_sec_attr in msg or inv_prop_attr in msg)

    def test_sec_creation_error(self):
        filename = "broken_section.yaml"

        valid = "valid_sec"
        invalid = "invalid_sec"

        file_content = _SEC_CREATION_ERROR_DOC % (valid, invalid)

        parsed_doc = self._prepare_doc(filename, file_content)

        # Test ParserException on default parse
        exc_msg = "Section not created"
        with self.assertRaises(ParserException) as exc:
            _ = self.yaml_reader.to_odml(parsed_doc)
        self.assertIn(exc_msg, str(exc.exception))

        # Test success on ignore_error parse
        self.yaml_reader.ignore_errors = True
        doc = self.yaml_reader.to_odml(parsed_doc)

        self.assertEqual(len(doc.sections["sec"].sections), 1)
        self.assertIn(valid, doc.sections["sec"].sections)
        self.assertNotIn(invalid, doc.sections["sec"].sections)

        self.assertEqual(len(self.yaml_reader.warnings), 1)
        for msg in self.yaml_reader.warnings:
            self.assertIn("Error", msg)
            self.assertIn(exc_msg, msg)

    def test_prop_creation_error(self):
        filename = "broken_property.yaml"

        parsed_doc = self._prepare_doc(filename, _PROP_CREATION_ERROR_DOC)

        # Test ParserException on default parse
        exc_msg = "Property not created"
        with self.assertRaises(ParserException) as exc:
            _ = self.yaml_reader.to_odml(parsed_doc)
        self.assertIn(exc_msg, str(exc.exception))

        # Test success on ignore_error parse
        self.yaml_reader.ignore_errors = True
        doc = self.yaml_reader.to_odml(parsed_doc)

        self.assertEqual(len(doc.sections["sec"].properties), 1)
        self.assertIn("valid_prop", doc.sections["sec"].properties)
        self.assertNotIn("invalid_prop", doc.sections["sec"].properties)

        self.assertEqual(len(self.yaml_reader.warnings), 1)
        for msg in self.yaml_reader.warnings:
            self.assertIn("Error", msg)
            self.assertIn(exc_msg, msg)
