import unittest
import os
from odml.tools import xmlparser
from odml.tools.parser_utils import ParserException


class TestParser(unittest.TestCase):

    def setUp(self):
        self.basepath = 'test/resources/'

        self.xml_reader = xmlparser.XMLReader()
