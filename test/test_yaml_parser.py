import os
import unittest
import yaml

from odml.tools import dict_parser
from odml.tools.parser_utils import ParserException


class TestYAMLParser(unittest.TestCase):

    def setUp(self):
        self.basepath = 'test/resources/'

        self.yaml_reader = dict_parser.DictReader()
