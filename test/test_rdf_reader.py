import datetime
import unittest

from rdflib import Literal

from odml import Property, Section, Document
from odml.format import Format
from odml.tools.rdf_converter import RDFWriter, RDFReader, rdflib_version_major
from odml.tools.parser_utils import ParserException

ODMLNS = Format.namespace()


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
        rdf_writer = RDFWriter(self.doc).get_rdf_str()
        rdf_reader = RDFReader().from_string(rdf_writer, "turtle")
        self.assertEqual(len(rdf_reader[0].sections), 1)
        self.assertEqual(len(rdf_reader[0].sections[0].sections), 1)
        self.assertEqual(len(rdf_reader[0].sections[0].properties), 1)

        rdf_writer = RDFWriter(self.doc).get_rdf_str("xml")
        rdf_reader = RDFReader().from_string(rdf_writer, "xml")
        self.assertEqual(len(rdf_reader[0].sections), 1)
        self.assertEqual(len(rdf_reader[0].sections[0].sections), 1)
        self.assertEqual(len(rdf_reader[0].sections[0].properties), 1)

        rdf_writer = RDFWriter(self.doc).get_rdf_str("n3")
        rdf_reader = RDFReader().from_string(rdf_writer, "n3")
        self.assertEqual(len(rdf_reader[0].sections), 1)
        self.assertEqual(len(rdf_reader[0].sections[0].sections), 1)
        self.assertEqual(len(rdf_reader[0].sections[0].properties), 1)

    def test_doc(self):
        """
        Test if a document and its attributes get converted correctly from rdf to odml.
        """
        doc = Document()
        doc.author = "D. N. Adams"
        doc.version = 42
        doc.date = datetime.date(1979, 10, 12)

        rdf_writer = RDFWriter(doc).get_rdf_str()
        rdf_reader = RDFReader().from_string(rdf_writer, "turtle")

        self.assertEqual(rdf_reader[0].author, "D. N. Adams")
        self.assertEqual(rdf_reader[0].version, "42")
        self.assertEqual(rdf_reader[0].date, datetime.date(1979, 10, 12))

    def test_section(self):
        """
        Test if a section and its attributes get converted correctly from rdf to odml.
        """
        doc = Document()
        sec1 = Section(name="sec1", type="test", parent=doc, definition="Interesting stuff.",
                       reference="The Journal")
        Section(name="sec2", type="test", parent=sec1)

        rdf_writer = RDFWriter(doc).get_rdf_str()
        rdf_reader = RDFReader().from_string(rdf_writer, "turtle")

        self.assertEqual(rdf_reader[0].sections[0].name, "sec1")
        self.assertEqual(rdf_reader[0].sections[0].type, "test")
        self.assertEqual(rdf_reader[0].sections[0].id, sec1.id)
        self.assertEqual(rdf_reader[0].sections[0].definition, "Interesting stuff.")
        self.assertEqual(rdf_reader[0].sections[0].reference, "The Journal")
        self.assertEqual(rdf_reader[0].sections[0].parent, rdf_reader[0])
        self.assertEqual(len(rdf_reader[0].sections[0].sections), 1)

    def test_property(self):
        """
        Test if a property and its attributes get converted correctly from rdf to odml.
        """
        doc = Document()
        sec1 = Section(name="sec1", type="test", parent=doc)
        prop2 = Property(name="numbers", definition="any number", dtype="float", parent=sec1,
                         values=[1, 3.4, 67.8, -12], unit="meter", uncertainty=0.8,
                         value_origin="force", reference="Experiment 1")

        rdf_writer = RDFWriter(doc).get_rdf_str()
        rdf_reader = RDFReader().from_string(rdf_writer, "turtle")

        prop = rdf_reader[0].sections[0].properties["numbers"]

        self.assertEqual(prop.name, "numbers")
        self.assertEqual(prop.dtype, "float")
        self.assertEqual(prop.id, prop2.id)
        self.assertEqual(prop.parent, rdf_reader[0].sections[0])
        self.assertEqual(len(prop.values), 4)
        self.assertEqual(prop.values, [1, 3.4, 67.8, -12])
        self.assertEqual(prop.definition, "any number")
        self.assertEqual(prop.unit, "meter")
        self.assertEqual(prop.uncertainty, "0.8")
        self.assertEqual(prop.value_origin, "force")
        self.assertEqual(prop.reference, "Experiment 1")

    def test_mandatory_attrs_section(self):
        """
        Test if ParserError is thrown if mandatory attributes are missing for section.
        """
        rdf_writer = RDFWriter([self.doc])
        rdf_writer.convert_to_rdf()
        for rdf_sec in rdf_writer.graph.subjects(predicate=ODMLNS.hasName, object=Literal("sec1")):
            rdf_writer.graph.remove((rdf_sec, ODMLNS.hasName, Literal("sec1")))

        # support both >=6.0.0 and <6.0.0 versions of rdflib for the time being
        if rdflib_version_major() < 6:
            new_graph = rdf_writer.graph.serialize(format="turtle").decode("utf-8")
        else:
            new_graph = rdf_writer.graph.serialize(format="turtle")

        with self.assertRaises(ParserException):
            RDFReader().from_string(new_graph, "turtle")

    def test_mandatory_attrs_property(self):
        """
        Test if ParserError is thrown if mandatory attributes are missing for section.
        """
        rdf_writer = RDFWriter([self.doc])
        rdf_writer.convert_to_rdf()
        for rdf_sec in rdf_writer.graph.subjects(predicate=ODMLNS.hasName, object=Literal("prop1")):
            rdf_writer.graph.remove((rdf_sec, ODMLNS.hasName, Literal("prop1")))

        # support both >=6.0.0 and <6.0.0 versions of rdflib for the time being
        if rdflib_version_major() < 6:
            new_graph = rdf_writer.graph.serialize(format="turtle").decode("utf-8")
        else:
            new_graph = rdf_writer.graph.serialize(format="turtle")

        with self.assertRaises(ParserException):
            RDFReader().from_string(new_graph, "turtle")
