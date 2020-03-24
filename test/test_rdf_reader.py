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

    def test_rdf_formats(self):
        """
        Test if document gets correctly converted to odml for turtle, xml and n3.
        """
        w = RDFWriter(self.doc).get_rdf_str()
        r = RDFReader().from_string(w, "turtle")
        self.assertEqual(len(r[0].sections), 1)
        self.assertEqual(len(r[0].sections[0].sections), 1)
        self.assertEqual(len(r[0].sections[0].properties), 1)

        w = RDFWriter(self.doc).get_rdf_str("xml")
        r = RDFReader().from_string(w, "xml")
        self.assertEqual(len(r[0].sections), 1)
        self.assertEqual(len(r[0].sections[0].sections), 1)
        self.assertEqual(len(r[0].sections[0].properties), 1)

        w = RDFWriter(self.doc).get_rdf_str("n3")
        r = RDFReader().from_string(w, "n3")
        self.assertEqual(len(r[0].sections), 1)
        self.assertEqual(len(r[0].sections[0].sections), 1)
        self.assertEqual(len(r[0].sections[0].properties), 1)
