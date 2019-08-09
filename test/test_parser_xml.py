import os
import unittest

from odml.tools import xmlparser
from odml.tools.parser_utils import ParserException, InvalidVersionException


class TestXMLParser(unittest.TestCase):

    def setUp(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.basepath = os.path.join(dir_path, "resources")

        self.xml_reader = xmlparser.XMLReader()
        self.xml_reader_ignore = xmlparser.XMLReader(ignore_errors=True)

    def test_invalid_root(self):
        filename = "invalid_root.xml"
        message = "Expecting <odML>"

        with self.assertRaises(ParserException) as exc:
            _ = self.xml_reader.from_file(os.path.join(self.basepath, filename))

        self.assertIn(message, str(exc.exception))

    def test_missing_version(self):
        filename = "missing_version.xml"
        message = "Could not find format version attribute"

        with self.assertRaises(ParserException) as exc:
            _ = self.xml_reader.from_file(os.path.join(self.basepath, filename))

        self.assertIn(message, str(exc.exception))

    def test_invalid_version(self):
        filename = "invalid_version.xml"

        with self.assertRaises(InvalidVersionException):
            _ = self.xml_reader.from_file(os.path.join(self.basepath, filename))

    def test_ignore_errors(self):
        filename = "ignore_errors.xml"

        doc = self.xml_reader_ignore.from_file(os.path.join(self.basepath, filename))
        doc.pprint()
