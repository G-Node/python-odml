import datetime
import unittest

from rdflib import Literal
import odml.format as format

from odml import Property, Section, Document
from odml.tools.rdf_converter import RDFWriter, RDFReader
from odml.tools.parser_utils import ParserException

odmlns = format.Format.namespace()


class TestRDFReader(unittest.TestCase):

    def setUp(self):
        doc = Document()
        sec = Section(name="sec1", type="test", parent=doc)
        Section(name="sec2", type="test", parent=sec)
        Property(name="prop1", values=[1.3], parent=sec)

        self.doc = doc
