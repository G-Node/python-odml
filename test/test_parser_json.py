"""
This module supplies basic tests for the odml.dict_parser.DictReader
reading from json files.
"""

import json
import os
import shutil
import unittest

from odml.tools import dict_parser
from odml.tools.parser_utils import ParserException, InvalidVersionException
from .util import create_test_dir, TEST_RESOURCES_DIR as RES_DIR


_INVALID_ATTRIBUTE_HANDLING_DOC = """
{
  "Document": {
    "id": "6af2a3ec-9f3a-42d6-a59d-95f3ccbaa383",
    "%s": "i_do_not_exist_on_doc_level",
    "sections": [
      {
        "id": "51f3c79c-a7d7-471e-be16-e085caa851fb",
        "%s": "i_do_not_exist_on_sec_level",
        "type": "test",
        "name": "sec",
        "sections": [],
        "properties": [
          {
            "id": "c5aed35a-d9ff-437d-82d6-68f0cda8ea94",
            "%s": "i_do_not_exist_on_prop_level",
            "name": "prop",
            "value": [
              1,
              2,
              3
            ],
            "type": "int"
          }
        ]
      }
    ]
  },
  "odml-version": "1.1"
}
""".strip()

_SEC_CREATION_ERROR_DOC = """
{
  "Document": {
    "id": "6af2a3ec-9f3a-42d6-a59d-95f3ccbaa383",
    "sections": [
      {
        "id": "1113c79c-a7d7-471e-be16-e085caa851fb",
        "name": "sec",
        "type": "test",
        "sections": [
          {
            "id": "1213c79c-a7d7-471e-be16-e085caa851fb",
            "name": "%s",
            "type": "test"
          },
          {
            "id": [
              "I-am-so-kaputt"
            ],
            "name": "%s",
            "type": "test"
          }
        ]
      }
    ]
  },
  "odml-version": "1.1"
}
""".strip()

_PROP_CREATION_ERROR_DOC = """
{
  "Document": {
    "id": "6af2a3ec-9f3a-42d6-a59d-95f3ccbaa383",
    "sections": [
      {
        "id": "51f3c79c-a7d7-471e-be16-e085caa851fb",
        "type": "test",
        "name": "sec",
        "properties": [
          {
            "id": "121ed35a-d9ff-437d-82d6-68f0cda8ea94",
            "name": "valid_prop"
          },
          {
            "id": "122ed35a-d9ff-437d-82d6-68f0cda8ea94",
            "name": "invalid_prop",
            "value": [
              "a",
              "b"
            ],
            "type": "int"
          }
        ]
      }
    ]
  },
  "odml-version": "1.1"
}
""".strip()


class TestJSONParser(unittest.TestCase):

    def setUp(self):
        self.base_path = RES_DIR
        self.json_reader = dict_parser.DictReader(show_warnings=False)
        self.tmp_dir_path = create_test_dir(__file__)

    def tearDown(self):
        if self.tmp_dir_path and os.path.exists(self.tmp_dir_path):
            shutil.rmtree(self.tmp_dir_path)

    def _prepare_doc(self, file_name, file_content):
        file_path = os.path.join(self.tmp_dir_path, file_name)

        with open(file_path, "w") as dump_file:
            dump_file.write(file_content)

        with open(file_path) as raw_data:
            parsed_doc = json.load(raw_data)

        return parsed_doc

    def test_missing_root(self):
        filename = "missing_root.json"
        message = "Missing root element"

        with open(os.path.join(self.base_path, filename)) as json_data:
            parsed_doc = json.load(json_data)

        with self.assertRaises(ParserException) as exc:
            _ = self.json_reader.to_odml(parsed_doc)

        self.assertIn(message, str(exc.exception))

    def test_missing_version(self):
        filename = "missing_version.json"
        message = "Could not find odml-version"

        with open(os.path.join(self.base_path, filename)) as json_data:
            parsed_doc = json.load(json_data)

        with self.assertRaises(ParserException) as exc:
            _ = self.json_reader.to_odml(parsed_doc)

        self.assertIn(message, str(exc.exception))

    def test_invalid_version(self):
        filename = "invalid_version.json"

        with open(os.path.join(self.base_path, filename)) as json_data:
            parsed_doc = json.load(json_data)

        with self.assertRaises(InvalidVersionException):
            _ = self.json_reader.to_odml(parsed_doc)

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
            _ = self.json_reader.to_odml(parsed_doc)
        self.assertIn(exc_msg, str(exc.exception))

        # Test success on ignore_error parse
        self.json_reader.ignore_errors = True
        doc = self.json_reader.to_odml(parsed_doc)

        self.assertEqual(len(doc.sections), 1)
        self.assertEqual(len(doc.sections["sec"].properties), 1)

        self.assertEqual(len(self.json_reader.warnings), 3)
        for msg in self.json_reader.warnings:
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
            _ = self.json_reader.to_odml(parsed_doc)
        self.assertIn(exc_msg, str(exc.exception))

        # Test success on ignore_error parse
        self.json_reader.ignore_errors = True
        doc = self.json_reader.to_odml(parsed_doc)

        self.assertEqual(len(doc.sections["sec"].sections), 1)
        self.assertIn(valid, doc.sections["sec"].sections)
        self.assertNotIn(invalid, doc.sections["sec"].sections)

        self.assertEqual(len(self.json_reader.warnings), 1)
        for msg in self.json_reader.warnings:
            self.assertIn("Error", msg)
            self.assertIn(exc_msg, msg)

    def test_prop_creation_error(self):
        filename = "broken_property.yaml"

        parsed_doc = self._prepare_doc(filename, _PROP_CREATION_ERROR_DOC)

        # Test ParserException on default parse
        exc_msg = "Property not created"
        with self.assertRaises(ParserException) as exc:
            _ = self.json_reader.to_odml(parsed_doc)
        self.assertIn(exc_msg, str(exc.exception))

        # Test success on ignore_error parse
        self.json_reader.ignore_errors = True
        doc = self.json_reader.to_odml(parsed_doc)

        self.assertEqual(len(doc.sections["sec"].properties), 1)
        self.assertIn("valid_prop", doc.sections["sec"].properties)
        self.assertNotIn("invalid_prop", doc.sections["sec"].properties)

        self.assertEqual(len(self.json_reader.warnings), 1)
        for msg in self.json_reader.warnings:
            self.assertIn("Error", msg)
            self.assertIn(exc_msg, msg)
