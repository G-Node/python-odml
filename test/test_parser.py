import unittest
import os
from odml.tools import odmlparser


class TestParser(unittest.TestCase):

    def setUp(self):
        self.basepath = 'doc/example_odMLs/'
        self.basefile = 'doc/example_odMLs/THGTTG.odml'

        self.xml_file = 'doc/example_odMLs/THGTTG_xml.odml'
        self.yaml_file = 'doc/example_odMLs/THGTTG_yaml.odml'
        self.json_file = 'doc/example_odMLs/THGTTG_json.odml'

        self.xml_reader = odmlparser.ODMLReader(parser='XML')
        self.yaml_reader = odmlparser.ODMLReader(parser='YAML')
        self.json_reader = odmlparser.ODMLReader(parser='JSON')

        self.xml_writer = odmlparser.ODMLWriter(parser='XML')
        self.yaml_writer = odmlparser.ODMLWriter(parser='YAML')
        self.json_writer = odmlparser.ODMLWriter(parser='JSON')

        self.odml_doc = self.xml_reader.fromFile(self.basefile)


    def tearDown(self):
        if os.path.exists(self.xml_file):
            os.remove(self.xml_file)

        if os.path.exists(self.yaml_file):    
            os.remove(self.yaml_file)

        # if os.path.exists(self.json_file):
        #     os.remove(self.json_file)


    def test_xml(self):

        self.xml_writer.write_file(self.odml_doc, self.xml_file)
        xml_doc = self.xml_reader.fromFile(open(self.xml_file))

        self.assertEqual(xml_doc, self.odml_doc)

    def test_yaml(self):

        self.yaml_writer.write_file(self.odml_doc, self.yaml_file)
        yaml_doc = self.yaml_reader.fromFile(open(self.yaml_file))

        self.assertEqual(yaml_doc, self.odml_doc)


    def test_json(self):

        self.json_writer.write_file(self.odml_doc, self.json_file)
        json_doc = self.json_reader.fromFile(open(self.json_file))

        self.assertEqual(json_doc, self.odml_doc)


    def test_json_yaml_xml(self):

        self.json_writer.write_file(self.odml_doc, self.json_file)
        json_doc = self.json_reader.fromFile(open(self.json_file))
        
        self.yaml_writer.write_file(json_doc, self.yaml_file)
        yaml_doc = self.yaml_reader.fromFile(open(self.yaml_file))

        self.xml_writer.write_file(yaml_doc, self.xml_file)
        xml_doc = self.xml_reader.fromFile(open(self.xml_file))

        self.assertEqual(json_doc, self.odml_doc)
        self.assertEqual(json_doc, yaml_doc)
        self.assertEqual(json_doc, xml_doc)
        
        self.assertEqual(yaml_doc, self.odml_doc)
        self.assertEqual(yaml_doc, xml_doc)
        self.assertEqual(yaml_doc, json_doc)

        self.assertEqual(xml_doc, self.odml_doc)
        self.assertEqual(xml_doc, json_doc)
        self.assertEqual(xml_doc, yaml_doc)
