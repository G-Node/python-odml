import unittest
import os
from odml.tools import xmlparser
from odml.tools.parser_utils import ParserException


class TestXMLParser(unittest.TestCase):

    def setUp(self):
        self.basepath = 'test/resources/'

        self.xml_reader = xmlparser.XMLReader()

    def test_invalid_root(self):
        filename = "invalid_root.xml"

        with self.assertRaises(ParserException):
            _ = self.xml_reader.from_file(os.path.join(self.basepath, filename))

    def test_missing_version(self):
        filename = "missing_version.xml"

        with self.assertRaises(ParserException):
            _ = self.xml_reader.from_file(os.path.join(self.basepath, filename))

    def test_invalid_version(self):
        filename = "invalid_version.xml"

        with self.assertRaises(ParserException):
            _ = self.xml_reader.from_file(os.path.join(self.basepath, filename))
