import unittest
import os
from odml.tools import dict_parser
from odml.tools.parser_utils import ParserException


class TestJSONParser(unittest.TestCase):

    def setUp(self):
        self.basepath = 'test/resources/'

        self.json_reader = dict_parser.DictReader()
