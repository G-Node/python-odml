import datetime
import os
import unittest

import yaml

from rdflib import URIRef, Literal
from rdflib.namespace import XSD, RDF

import odml

from odml.format import Format
from odml.tools.rdf_converter import RDFWriter

from .test_samplefile import SampleFileCreator
from .test_samplefile import parse

ODMLNS = Format.namespace()


class TestRDFWriter(unittest.TestCase):

    def setUp(self):
        doc = SampleFileCreator().create_document()
        doc1 = SampleFileCreator().create_document()
        self.doc = doc
        self.doc1 = doc1

    def test_convert_to_rdf(self):
        rdf_writer = RDFWriter([self.doc, self.doc1])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subjects(predicate=RDF.type,
                                          object=URIRef(ODMLNS.Document))
        self.assertEqual(len(list(check)), 2)

    def test_adding_doc_to_the_hub(self):
        rdf_writer = RDFWriter([self.doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.objects(subject=rdf_writer.hub_root,
                                         predicate=ODMLNS.hasDocument)
        self.assertEqual(len(list(check)), 1)

    def test_adding_repository(self):
        rdf_writer = RDFWriter([self.doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.objects(subject=rdf_writer.hub_root,
                                         predicate=ODMLNS.hasTerminology)
        self.assertEqual(len(list(check)), 0)

        check = rdf_writer.graph.objects(subject=URIRef(ODMLNS + rdf_writer.docs[0].id),
                                         predicate=ODMLNS.hasTerminology)
        self.assertEqual(len(list(check)), 0)

        url = "terminology_url"
        self.doc.repository = url
        rdf_writer = RDFWriter([self.doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subjects(predicate=RDF.type, object=URIRef(url))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.objects(subject=rdf_writer.hub_root,
                                         predicate=ODMLNS.hasTerminology)
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.objects(subject=URIRef(ODMLNS + rdf_writer.docs[0].id),
                                         predicate=ODMLNS.hasTerminology)
        self.assertEqual(len(list(check)), 1)

    def test_adding_sections(self):
        doc = odml.Document()
        rdf_writer = RDFWriter([doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subject_objects(predicate=ODMLNS.hasSection)
        self.assertEqual(len(list(check)), 0)

        rdf_writer = RDFWriter([self.doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subject_objects(predicate=ODMLNS.hasSection)
        self.assertEqual(len(list(check)), 9)

        rdf_writer = RDFWriter([self.doc, self.doc1])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subject_objects(predicate=ODMLNS.hasSection)
        self.assertEqual(len(list(check)), 18)

    def test_adding_properties(self):
        doc = parse("""
            s1[t1]
            - s11[t1]
            s2[t2]
            """)
        rdf_writer = RDFWriter([doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subject_objects(predicate=ODMLNS.hasProperty)
        self.assertEqual(len(list(check)), 0)

        rdf_writer = RDFWriter([self.doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subject_objects(predicate=ODMLNS.hasProperty)
        self.assertEqual(len(list(check)), 12)

        rdf_writer = RDFWriter([self.doc, self.doc1])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subject_objects(predicate=ODMLNS.hasProperty)
        self.assertEqual(len(list(check)), 24)

    def test_adding_values(self):
        doc = parse("""
            s1[t1]
            """)

        rdf_writer = RDFWriter([doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subject_objects(predicate=RDF.li)
        self.assertEqual(len(list(check)), 0)

        check = rdf_writer.graph.subject_objects(predicate=URIRef("%s_1" % str(RDF)))
        self.assertEqual(len(list(check)), 0)

        doc = parse("""
            s1[t1]
            - p1
            """)

        rdf_writer = RDFWriter([doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subjects(predicate=RDF.li, object=Literal("val"))
        self.assertEqual(len(list(check)), 0)

        check = rdf_writer.graph.subjects(predicate=URIRef("%s_1" % str(RDF)),
                                          object=Literal("val"))
        self.assertEqual(len(list(check)), 1)

        doc.sections[0].properties[0].append("val2")
        rdf_writer = RDFWriter([doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subject_objects(predicate=RDF.li)
        self.assertEqual(len(list(check)), 0)

        check = rdf_writer.graph.subjects(predicate=RDF.li, object=Literal("val"))
        self.assertEqual(len(list(check)), 0)

        check = rdf_writer.graph.subjects(predicate=RDF.li, object=Literal("val2"))
        self.assertEqual(len(list(check)), 0)

        check = rdf_writer.graph.subjects(predicate=URIRef("%s_1" % str(RDF)),
                                          object=Literal("val"))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=URIRef("%s_2" % str(RDF)),
                                          object=Literal("val2"))
        self.assertEqual(len(list(check)), 1)

        doc = parse("""
             s1[t1]
             - p1
             s2[t2]
             - p1
             - p2
             """)

        rdf_writer = RDFWriter([doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subjects(predicate=RDF.li, object=Literal("val"))
        self.assertEqual(len(list(check)), 0)

        check = rdf_writer.graph.subjects(predicate=URIRef("%s_1" % str(RDF)),
                                          object=Literal("val"))
        self.assertEqual(len(list(check)), 3)

    def test_section_subclass(self):
        file_path = os.path.join(odml.__path__[0], 'resources', 'section_subclasses.yaml')
        with open(file_path, "r") as subclass_file:
            subclass = yaml.safe_load(subclass_file)

        doc = odml.Document()
        subclass_key = next(iter(subclass))
        sec = odml.Section("S", type=subclass_key)
        doc.append(sec)

        rdf_writer = RDFWriter(doc)
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subjects(predicate=RDF.type,
                                          object=URIRef(ODMLNS[subclass[subclass_key]]))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=RDF.type, object=URIRef(ODMLNS.Section))
        self.assertEqual(len(list(check)), 0)

    def test_adding_other_entities_properties(self):
        doc = parse("""
            s1[t1]
            - p1
            """)

        version = "v1"
        date = datetime.date(1979, 10, 12)
        author = "nice person"
        s_def = "comment"
        s_ref = "reference"
        p_unit = "u1"
        p_name = "p1"
        p_def = "p comment"
        p_uncertainty = 13.0
        p_dtype = "string"
        p_value_origin = "value"
        p_ref = "p_ref"

        doc.version = version
        doc.date = date
        doc.author = author
        doc.sections[0].definition = s_def
        doc.sections[0].reference = s_ref
        doc.sections[0].properties[0].name = p_name
        doc.sections[0].properties[0].unit = p_unit
        doc.sections[0].properties[0].definition = p_def
        doc.sections[0].properties[0].uncertainty = p_uncertainty
        doc.sections[0].properties[0].dtype = p_dtype
        doc.sections[0].properties[0].value_origin = p_value_origin
        doc.sections[0].properties[0].reference = p_ref

        rdf_writer = RDFWriter([doc])
        rdf_writer.convert_to_rdf()

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasDocVersion, object=Literal(version))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasDate,
                                          object=Literal(date, datatype=XSD.date))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasAuthor, object=Literal(author))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasName, object=Literal("s1"))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasType, object=Literal("t1"))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasDefinition, object=Literal(s_def))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasReference, object=Literal(s_ref))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasName, object=Literal(p_name))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasUnit, object=Literal(p_unit))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasDefinition, object=Literal(p_def))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasUncertainty,
                                          object=Literal(p_uncertainty))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasDtype, object=Literal(p_dtype))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasValueOrigin,
                                          object=Literal(p_value_origin))
        self.assertEqual(len(list(check)), 1)

        check = rdf_writer.graph.subjects(predicate=ODMLNS.hasReference, object=Literal(p_ref))
        self.assertEqual(len(list(check)), 1)

    def test_get_rdf_string(self):
        rdf_writer = RDFWriter([self.doc1])
        rdf_writer.get_rdf_str()

        with self.assertRaises(ValueError):
            rdf_writer.get_rdf_str("abc")
