"""
This file tests proper creation, saving and loading
of odML Properties with all supported odML parsers.
"""

import os
import shutil
import tempfile
import unittest

import odml


class TestPropertyIntegration(unittest.TestCase):

    def setUp(self):
        # Set up test environment
        self.tmp_dir = tempfile.mkdtemp(suffix=".odml")

        self.json_file = os.path.join(self.tmp_dir, "test.json")
        self.xml_file = os.path.join(self.tmp_dir, "test.xml")
        self.yaml_file = os.path.join(self.tmp_dir, "test.yaml")

        # Set up odML document stub
        doc = odml.Document()
        _ = odml.Section(name="properties", type="test", parent=doc)
        self.doc = doc

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def save_load(self):
        """
        Helper method to save and load the current state of the document
        with all supported parsers.
        :return: jdoc ... document loaded from JSON file
                 xdoc ... document loaded from XML file
                 ydoc ... document loaded from YAML file
        """
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        return jdoc, xdoc, ydoc

    def test_id(self):
        # Test correct save and load of generated id.
        prop_name = "empty_id"
        prop = odml.Property(name=prop_name, parent=self.doc.sections[0])

        jdoc, xdoc, ydoc = self.save_load()

        self.assertEqual(jdoc.sections[0].properties[prop_name].id, prop.id)
        self.assertEqual(xdoc.sections[0].properties[prop_name].id, prop.id)
        self.assertEqual(ydoc.sections[0].properties[prop_name].id, prop.id)

        # Test correct save and load of assigned id.
        prop_name = "assigned_id"
        assigned_id = "79b613eb-a256-46bf-84f6-207df465b8f7"
        _ = odml.Property(name=prop_name, id=assigned_id,
                          parent=self.doc.sections[0])

        jdoc, xdoc, ydoc = self.save_load()

        self.assertEqual(jdoc.sections[0].properties[prop_name].id, assigned_id)
        self.assertEqual(xdoc.sections[0].properties[prop_name].id, assigned_id)
        self.assertEqual(ydoc.sections[0].properties[prop_name].id, assigned_id)
