"""
This file tests proper creation, saving and loading
of odML Sections with all supported odML parsers.
"""

import os
import shutil
import tempfile
import unittest

import odml


class TestSectionIntegration(unittest.TestCase):

    def setUp(self):
        # Set up test environment
        self.tmp_dir = tempfile.mkdtemp(suffix=".odml")

        self.json_file = os.path.join(self.tmp_dir, "test.json")
        self.xml_file = os.path.join(self.tmp_dir, "test.xml")
        self.yaml_file = os.path.join(self.tmp_dir, "test.yaml")

        # Set up odML document stub
        doc = odml.Document()
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
