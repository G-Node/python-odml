import datetime
import os
import unittest
from os.path import dirname, abspath

import yaml
from rdflib import URIRef, Literal
from rdflib.namespace import XSD, RDF

import odml
import odml.format as format
from odml.tools.rdf_converter import RDFWriter
from test.test_samplefile import SampleFileCreator
from test.test_samplefile import parse

odmlns = format.Format.namespace()


class TestRDFWriter(unittest.TestCase):

    def setUp(self):
        doc = SampleFileCreator().create_document()
        doc1 = SampleFileCreator().create_document()
        self.doc = doc
        self.doc1 = doc1

    def test_convert_to_rdf(self):
        w = RDFWriter([self.doc, self.doc1])
        w.convert_to_rdf()
        doc_subjects = w.g.subjects(predicate=RDF.type, object=URIRef(odmlns.Document))
        self.assertEqual(len(list(doc_subjects)), 2)

    def test_adding_doc_to_the_hub(self):
        w = RDFWriter([self.doc])
        w.convert_to_rdf()
        hub_hasDocument = w.g.objects(subject=w.hub_root, predicate=odmlns.hasDocument)
        self.assertEqual(len(list(hub_hasDocument)), 1)

    def test_adding_repository(self):
        w = RDFWriter([self.doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.objects(subject=w.hub_root, predicate=odmlns.hasTerminology))), 0)
        self.assertEqual(len(list(w.g.objects(subject=URIRef(odmlns + w.docs[0].id), predicate=odmlns.hasTerminology))), 0)

        url = "terminology_url"
        self.doc.repository = url
        w = RDFWriter([self.doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subjects(predicate=RDF.type, object=URIRef(url)))), 1)
        self.assertEqual(len(list(w.g.objects(subject=w.hub_root, predicate=odmlns.hasTerminology))), 1)
        self.assertEqual(len(list(w.g.objects(subject=URIRef(odmlns + w.docs[0].id), predicate=odmlns.hasTerminology))), 1)

    def test_adding_sections(self):
        doc = odml.Document()
        w = RDFWriter([doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subject_objects(predicate=odmlns.hasSection))), 0)

        w = RDFWriter([self.doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subject_objects(predicate=odmlns.hasSection))), 9)

        w = RDFWriter([self.doc, self.doc1])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subject_objects(predicate=odmlns.hasSection))), 18)

    def test_adding_properties(self):
        doc = parse("""
            s1[t1]
            - s11[t1]
            s2[t2]
            """)
        w = RDFWriter([doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subject_objects(predicate=odmlns.hasProperty))), 0)

        w = RDFWriter([self.doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subject_objects(predicate=odmlns.hasProperty))), 12)

        w = RDFWriter([self.doc, self.doc1])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subject_objects(predicate=odmlns.hasProperty))), 24)

    def test_adding_values(self):
        doc = parse("""
            s1[t1]
            """)

        w = RDFWriter([doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subject_objects(predicate=RDF.li))), 0)

        doc = parse("""
            s1[t1]
            - p1
            """)

        w = RDFWriter([doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subjects(predicate=RDF.li, object=Literal("val")))), 1)

        doc.sections[0].properties[0].append("val2")
        w = RDFWriter([doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subject_objects(predicate=RDF.li))), 2)
        self.assertEqual(len(list(w.g.subjects(predicate=RDF.li, object=Literal("val")))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=RDF.li, object=Literal("val2")))), 1)

        doc = parse("""
             s1[t1]
             - p1
             s2[t2]
             - p1
             - p2
             """)

        w = RDFWriter([doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subjects(predicate=RDF.li, object=Literal("val")))), 3)

    def test_section_subclass(self):
        p = os.path.join(dirname(dirname(abspath(__file__))), 'doc', 'section_subclasses.yaml')
        with open(p, "r") as f:
            subclass = yaml.load(f)

        doc = odml.Document()
        subclass_key = next(iter(subclass))
        s = odml.Section("S", type=subclass_key)
        doc.append(s)
        w = RDFWriter(doc)
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subjects(predicate=RDF.type, object=URIRef(odmlns[subclass[subclass_key]])))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=RDF.type, object=URIRef(odmlns.Section)))), 0)

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
        p_uncertainty = "un"
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

        w = RDFWriter([doc])
        w.convert_to_rdf()
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasDocVersion, object=Literal(version)))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasDate, object=Literal(date, datatype=XSD.date)))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasAuthor, object=Literal(author)))), 1)

        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasName, object=Literal("s1")))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasType, object=Literal("t1")))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasDefinition, object=Literal(s_def)))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasReference, object=Literal(s_ref)))), 1)

        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasName, object=Literal(p_name)))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasUnit, object=Literal(p_unit)))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasDefinition, object=Literal(p_def)))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasUncertainty, object=Literal(p_uncertainty)))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasDtype, object=Literal(p_dtype)))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasValueOrigin, object=Literal(p_value_origin)))), 1)
        self.assertEqual(len(list(w.g.subjects(predicate=odmlns.hasReference, object=Literal(p_ref)))), 1)
