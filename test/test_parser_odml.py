"""
This file tests proper saving and loading of odML Documents
with all supported odML parsers via the tools.odmlparser classes.
"""

import os
import shutil
import tempfile
import unittest

from odml.tools import odmlparser


class TestOdmlParser(unittest.TestCase):

    def setUp(self):
        # Set up test environment
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.basefile = os.path.join(dir_path, "resources", "example.odml")

        self.tmp_dir = tempfile.mkdtemp(suffix=".odml")

        self.json_file = os.path.join(self.tmp_dir, "test.json")
        self.xml_file = os.path.join(self.tmp_dir, "test.xml")
        self.yaml_file = os.path.join(self.tmp_dir, "test.yaml")
        self.rdf_file = os.path.join(self.tmp_dir, "test.ttl")

        self.xml_reader = odmlparser.ODMLReader(parser='XML')
        self.yaml_reader = odmlparser.ODMLReader(parser='YAML')
        self.json_reader = odmlparser.ODMLReader(parser='JSON')
        self.rdf_reader = odmlparser.ODMLReader(parser='RDF')

        self.xml_writer = odmlparser.ODMLWriter(parser='XML')
        self.yaml_writer = odmlparser.ODMLWriter(parser='YAML')
        self.json_writer = odmlparser.ODMLWriter(parser='JSON')
        self.rdf_writer = odmlparser.ODMLWriter(parser='RDF')

        self.odml_doc = self.xml_reader.from_file(self.basefile)

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_json_yaml_xml(self):
        self.json_writer.write_file(self.odml_doc, self.json_file)
        json_doc = self.json_reader.from_file(self.json_file)

        self.yaml_writer.write_file(json_doc, self.yaml_file)
        yaml_doc = self.yaml_reader.from_file(self.yaml_file)

        self.xml_writer.write_file(yaml_doc, self.xml_file)
        xml_doc = self.xml_reader.from_file(self.xml_file)

        self.assertEqual(json_doc, self.odml_doc)
        self.assertEqual(json_doc, yaml_doc)
        self.assertEqual(json_doc, xml_doc)

        self.assertEqual(yaml_doc, self.odml_doc)
        self.assertEqual(yaml_doc, xml_doc)
        self.assertEqual(yaml_doc, json_doc)

        self.assertEqual(xml_doc, self.odml_doc)
        self.assertEqual(xml_doc, json_doc)
        self.assertEqual(xml_doc, yaml_doc)

    def test_xml_file(self):
        self.xml_writer.write_file(self.odml_doc, self.xml_file)
        xml_doc = self.xml_reader.from_file(self.xml_file)

        self.assertEqual(xml_doc, self.odml_doc)

    def test_yaml_file(self):
        self.yaml_writer.write_file(self.odml_doc, self.yaml_file)
        yaml_doc = self.yaml_reader.from_file(self.yaml_file)

        self.assertEqual(yaml_doc, self.odml_doc)

    def test_json_file(self):
        self.json_writer.write_file(self.odml_doc, self.json_file)
        json_doc = self.json_reader.from_file(self.json_file)

        self.assertEqual(json_doc, self.odml_doc)

    def test_rdf_file(self):
        self.rdf_writer.write_file(self.odml_doc, self.rdf_file)
        rdf_doc = self.rdf_reader.from_file(self.rdf_file, "turtle")

        # RDF does not preserve the order of sections,
        # need to check the attributes by hand.
        self.assertEqual(len(rdf_doc), 1)
        self.assertEqual(rdf_doc[0].author, self.odml_doc.author)
        self.assertEqual(rdf_doc[0].version, self.odml_doc.version)
        self.assertEqual(rdf_doc[0].date, self.odml_doc.date)
        self.assertIn(self.odml_doc.sections[0].name, rdf_doc[0].sections)
        self.assertIn(self.odml_doc.sections[1].name, rdf_doc[0].sections)

        # Check error on missing document format
        with self.assertRaises(ValueError):
            self.rdf_reader.from_file(self.rdf_file)

    def test_xml_string(self):
        # Read from string
        author = "HPL"
        date = "1890-08-20"
        sec_name = "section name"
        sec_type = "section type"
        doc = """
                 <odML version="1.1">
                    <author>%s</author>
                    <date>%s</date>
                    <section>
                        <name>%s</name>
                        <type>%s</type>
                    </section>
                 </odML>
               """ % (author, date, sec_name, sec_type)

        xml_doc = self.xml_reader.from_string(doc)

        self.assertEqual(xml_doc.author, author)
        self.assertEqual(str(xml_doc.date), date)
        self.assertEqual(len(xml_doc.sections), 1)
        self.assertEqual(xml_doc.sections[0].name, sec_name)

    def test_json_string(self):
        author = "HPL"
        date = "1890-08-20"
        sec_name = "section name"
        sec_type = "section type"
        doc = """
                {
                    "odml-version": "1.1",
                    "Document": {
                        "author": "%s",
                        "date": "%s",
                        "sections": [{
                            "name": "%s",
                            "type": "%s"
                        }]
                    }
                }
                """ % (author, date, sec_name, sec_type)

        json_doc = self.json_reader.from_string(doc)

        self.assertEqual(json_doc.author, author)
        self.assertEqual(str(json_doc.date), date)
        self.assertEqual(len(json_doc.sections), 1)
        self.assertEqual(json_doc.sections[0].name, sec_name)

        # Test empty return on broken json document
        self.assertIsNone(self.json_reader.from_string("{"))

    def test_yaml_string(self):
        author = "HPL"
        date = "1890-08-20"
        sec_name = "section name"
        sec_type = "section type"
        yaml_doc = """
                odml-version: '1.1'
                Document:
                    author: %s
                    date: %s
                    sections:
                    - name: %s
                      type: %s
                """ % (author, date, sec_name, sec_type)

        ydoc = self.yaml_reader.from_string(yaml_doc)

        self.assertEqual(ydoc.author, author)
        self.assertEqual(str(ydoc.date), date)
        self.assertEqual(len(ydoc.sections), 1)
        self.assertEqual(ydoc.sections[0].name, sec_name)

    def test_rdf_string(self):
        author = "HPL"
        date = "1890-08-20"
        sec_name = "section name"
        sec_type = "section type"
        rdf_doc = u"""
        @prefix odml: <https://g-node.org/projects/odml-rdf#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix xml: <http://www.w3.org/XML/1998/namespace> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
        
        odml:Hub odml:hasDocument <https://g-node.org/projects/odml-rdf#1c9ca24a-1d2c-40b6-a096-5a48efbd77d0> .
        
        <https://g-node.org/projects/odml-rdf#1c9ca24a-1d2c-40b6-a096-5a48efbd77d0> a odml:Document ;
            odml:hasAuthor "%s" ;
            odml:hasDate "%s"^^xsd:date ;
            odml:hasSection <https://g-node.org/projects/odml-rdf#2abc6711-34e1-4102-8e3a-297fa4a3d19a> .
        
        <https://g-node.org/projects/odml-rdf#2abc6711-34e1-4102-8e3a-297fa4a3d19a> a odml:Section ;
            odml:hasName "%s" ;
            odml:hasType "%s" .
        """ % (author, date, sec_name, sec_type)

        rdoc = self.rdf_reader.from_string(rdf_doc, "turtle")

        self.assertEqual(rdoc[0].author, author)
        self.assertEqual(str(rdoc[0].date), date)
        self.assertEqual(len(rdoc[0].sections), 1)
        self.assertEqual(rdoc[0].sections[0].name, sec_name)

        with self.assertRaises(ValueError):
            self.rdf_reader.from_string(rdf_doc)
