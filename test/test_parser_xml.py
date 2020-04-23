import os
import unittest

from odml.tools import xmlparser
from odml.tools.parser_utils import ParserException, InvalidVersionException
from .util import TEST_RESOURCES_DIR as RES_DIR


class TestXMLParser(unittest.TestCase):

    def setUp(self):
        self.base_path = RES_DIR

        self.xml_reader = xmlparser.XMLReader()
        self.xml_reader_ignore = xmlparser.XMLReader(ignore_errors=True)

    def test_invalid_root(self):
        filename = "invalid_root.xml"
        message = "Expecting <odML>"

        with self.assertRaises(ParserException) as exc:
            _ = self.xml_reader.from_file(os.path.join(self.base_path, filename))

        self.assertIn(message, str(exc.exception))

    def test_missing_version(self):
        filename = "missing_version.xml"
        message = "Could not find format version attribute"

        with self.assertRaises(ParserException) as exc:
            _ = self.xml_reader.from_file(os.path.join(self.base_path, filename))

        self.assertIn(message, str(exc.exception))

    def test_invalid_version(self):
        filename = "invalid_version.xml"

        with self.assertRaises(InvalidVersionException):
            _ = self.xml_reader.from_file(os.path.join(self.base_path, filename))

    def test_ignore_errors(self):
        filename = "ignore_errors.xml"

        with self.assertRaises(ParserException):
            _ = self.xml_reader.from_file(os.path.join(self.base_path, filename))

        doc = self.xml_reader_ignore.from_file(os.path.join(self.base_path, filename))
        doc.pprint()
