import datetime
import os
import unittest

import yaml

from owlrl import DeductiveClosure, RDFS_Semantics

from rdflib import URIRef, Literal
from rdflib.namespace import Namespace, RDF, RDFS, XSD
from rdflib.plugins.sparql import prepareQuery

import odml

from odml.format import Format
from odml.tools.rdf_converter import ODML_NS, RDFWriter

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

    def test_rdf_subclassing_switch(self):
        """
        Test the RDF section subclassing switch.
        """
        # Section type term defined in odml/resources/section_subclasses.yaml that will
        # be converted to an RDF Section Subclass of Class "Cell".
        sub_class_term = "cell"

        # Create minimal document
        doc = odml.Document()
        _ = odml.Section(name="test_subclassing", type=sub_class_term, parent=doc)

        # Test default subclassing
        rdf_writer = RDFWriter([doc])
        result = rdf_writer.get_rdf_str()
        self.assertIn("odml:Cell", result)

        # Test inactivation of subclassing feature
        rdf_writer = RDFWriter([doc], rdf_subclassing=False)
        result = rdf_writer.get_rdf_str()
        self.assertNotIn("odml:Cell", result)

    def test_rdf_custom_subclasses(self):
        """
        Test collection of the odml RDF subclassing feature.
        Tests that the resulting output RDF document contains any required
        additional RDF subclasses.
        """
        sub_class_term = "cell"

        # Create minimal document
        doc = odml.Document()
        _ = odml.Section(name="test_subclassing", type=sub_class_term, parent=doc)

        # Test None dict
        rdf_writer = RDFWriter([doc], custom_subclasses=None)
        self.assertIn("odml:Cell", rdf_writer.get_rdf_str())

        # Test invalid dict
        rdf_writer = RDFWriter([doc], custom_subclasses=["invalid"])
        self.assertIn("odml:Cell", rdf_writer.get_rdf_str())

        # Test value whitespace
        invalid_dict = {"type_1": "Class 1", "type_2": "Class 2"}
        with self.assertRaises(ValueError):
            _ = RDFWriter([doc], custom_subclasses=invalid_dict)

        # Test custom subclassing
        type_custom_class = "species"
        custom_class_dict = {type_custom_class: "Species"}

        doc = odml.Document()
        _ = odml.Section(name="test_subclassing", type="cell", parent=doc)
        _ = odml.Section(name="test_custom_subclassing", type=type_custom_class, parent=doc)

        rdf_writer = RDFWriter([doc], custom_subclasses=custom_class_dict)
        self.assertIn("odml:Cell", rdf_writer.get_rdf_str())
        self.assertIn("odml:Species", rdf_writer.get_rdf_str())

        # Test custom subclassing overwrite
        sub_class_type = "cell"
        custom_class_dict = {sub_class_type: "Neuron"}

        doc = odml.Document()
        _ = odml.Section(name="test_subclassing", type=sub_class_type, parent=doc)

        with self.assertWarns(UserWarning):
            rdf_writer = RDFWriter([doc], custom_subclasses=custom_class_dict)
            self.assertNotIn("odml:Cell", rdf_writer.get_rdf_str())
            self.assertIn("odml:Neuron", rdf_writer.get_rdf_str())

    def test_rdf_subclassing_definitions(self):
        """
        Test that RDF Subclass definitions are written to the resulting graph.
        """
        # -- Test default subclassing
        doc = odml.Document()
        _ = odml.Section(name="test_subclassing", type="cell", parent=doc)

        rdf_writer = RDFWriter([doc])
        curr_str = " ".join(rdf_writer.get_rdf_str().split())
        self.assertIn("odml:Cell a rdfs:Class ; rdfs:subClassOf odml:Section", curr_str)
        self.assertIn("odml:Section a rdfs:Class", curr_str)

        # -- Test multiple entries; a definition should only occur once in an RDF document
        doc = odml.Document()
        sec = odml.Section(name="test_subclassing", type="cell", parent=doc)
        sub_sec = odml.Section(name="test_subclassing", type="cell", parent=sec)
        _ = odml.Section(name="test_subclassing", type="cell", parent=sub_sec)

        rdf_writer = RDFWriter([doc])
        curr_str = " ".join(rdf_writer.get_rdf_str().split())
        self.assertIn("odml:Cell a rdfs:Class ; rdfs:subClassOf odml:Section", curr_str)
        self.assertIs(curr_str.count("odml:Cell a rdfs:Class ; rdfs:subClassOf odml:Section"), 1)
        self.assertIn("odml:Section a rdfs:Class", curr_str)
        self.assertIs(curr_str.count("odml:Section a rdfs:Class"), 1)

        # -- Test custom subclassing
        type_custom_class = "species"
        custom_class_dict = {type_custom_class: "Species"}

        doc = odml.Document()
        _ = odml.Section(name="test_subclassing", type="cell", parent=doc)
        _ = odml.Section(name="test_custom_subclassing", type=type_custom_class, parent=doc)

        rdf_writer = RDFWriter([doc], custom_subclasses=custom_class_dict)
        curr_str = " ".join(rdf_writer.get_rdf_str().split())
        self.assertIn("odml:Cell a rdfs:Class ; rdfs:subClassOf odml:Section", curr_str)
        self.assertIn("odml:Species a rdfs:Class ; rdfs:subClassOf odml:Section", curr_str)
        self.assertIn("odml:Section a rdfs:Class", curr_str)

        # -- Test inactive subclassing
        doc = odml.Document()
        _ = odml.Section(name="test_subclassing", type="cell", parent=doc)

        rdf_writer = RDFWriter([doc], rdf_subclassing=False)
        curr_str = " ".join(rdf_writer.get_rdf_str().split())
        self.assertNotIn("odml:Section a rdfs:Class", curr_str)
        self.assertNotIn("odml:Cell a rdfs:Class ; rdfs:subClassOf odml:Section", curr_str)

    def test_rdf_subclassing_queries(self):
        """
        Test the proper implementation of the RDF subclassing feature. Tests ensure, that queries
        relying on RDF Subclasses return appropriate results.
        """
        namespace_map = {"odml": Namespace(ODML_NS), "rdf": RDF, "rdfs": RDFS}

        doc = odml.Document()
        _ = odml.Section(name="test_subclass", type="cell", parent=doc)
        _ = odml.Section(name="test_regular_class", type="regular", parent=doc)

        rdf_writer = RDFWriter([doc])
        _ = rdf_writer.get_rdf_str()

        use_graph = rdf_writer.graph
        DeductiveClosure(RDFS_Semantics).expand(use_graph)

        q_string = "SELECT * WHERE {?s rdf:type odml:Section .}"
        curr_query = prepareQuery(q_string, initNs=namespace_map)

        # Make sure the query finds two sections
        self.assertIs(len(use_graph.query(curr_query)), 2)

        # Make sure the query finds
        result_section = []
        for row in use_graph.query(curr_query):
            result_section.append(row.s)

        q_string = "SELECT * WHERE {?s rdf:type odml:Cell .}"
        curr_query = prepareQuery(q_string, initNs=namespace_map)

        self.assertIs(len(use_graph.query(curr_query)), 1)
        for row in use_graph.query(curr_query):
            self.assertIn(row.s, result_section)

        # -- Test custom subclassing queries
        type_custom_class = "species"
        type_overwrite_class = "cell"
        custom_class_dict = {type_custom_class: "Species", type_overwrite_class: "Neuron"}

        doc = odml.Document()
        sec = odml.Section(name="test_subclass", type="species", parent=doc)
        _ = odml.Section(name="test_subclass_overwrite", type="cell", parent=sec)
        _ = odml.Section(name="test_regular_class", type="regular", parent=sec)

        rdf_writer = RDFWriter([doc], custom_subclasses=custom_class_dict)
        _ = rdf_writer.get_rdf_str()

        use_graph = rdf_writer.graph
        DeductiveClosure(RDFS_Semantics).expand(use_graph)

        q_string = "SELECT * WHERE {?s rdf:type odml:Section .}"
        curr_query = prepareQuery(q_string, initNs=namespace_map)

        # Make sure the query finds three sections
        self.assertIs(len(use_graph.query(curr_query)), 3)

        # Make sure the query finds
        result_section = []
        for row in use_graph.query(curr_query):
            result_section.append(row.s)

        # Custom class 'Species' should be found.
        q_string = "SELECT * WHERE {?s rdf:type odml:Species .}"
        curr_query = prepareQuery(q_string, initNs=namespace_map)

        self.assertIs(len(use_graph.query(curr_query)), 1)
        for row in use_graph.query(curr_query):
            self.assertIn(row.s, result_section)

        # Custom class 'Neuron' should be found.
        q_string = "SELECT * WHERE {?s rdf:type odml:Neuron .}"
        curr_query = prepareQuery(q_string, initNs=namespace_map)

        self.assertIs(len(use_graph.query(curr_query)), 1)
        for row in use_graph.query(curr_query):
            self.assertIn(row.s, result_section)

        # Default class 'Cell' was replaced and should not return any result.
        q_string = "SELECT * WHERE {?s rdf:type odml:Cell .}"
        curr_query = prepareQuery(q_string, initNs=namespace_map)

        self.assertIs(len(use_graph.query(curr_query)), 0)

        # -- Test inactivated subclassing
        doc = odml.Document()
        _ = odml.Section(name="test_regular_class", type="regular", parent=doc)
        _ = odml.Section(name="test_subclass", type="cell", parent=doc)

        rdf_writer = RDFWriter([doc], rdf_subclassing=False)
        _ = rdf_writer.get_rdf_str()

        use_graph = rdf_writer.graph
        DeductiveClosure(RDFS_Semantics).expand(use_graph)

        q_string = "SELECT * WHERE {?s rdf:type odml:Section .}"
        curr_query = prepareQuery(q_string, initNs=namespace_map)

        self.assertIs(len(use_graph.query(curr_query)), 2)

        q_string = "SELECT * WHERE {?s rdf:type odml:Cell .}"
        curr_query = prepareQuery(q_string, initNs=namespace_map)

        self.assertIs(len(use_graph.query(curr_query)), 0)
