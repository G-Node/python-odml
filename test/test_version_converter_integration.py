"""
This file tests proper conversion of complex v1.0 odML files
to v1.1 with all supported file formats.
"""

import os
import shutil
import tempfile
import unittest

from odml import load
from odml.tools.version_converter import VersionConverter as VC


class TestVersionConverterIntegration(unittest.TestCase):
    def setUp(self):
        # Set up test environment
        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.jsonfile = os.path.join(dir_path, "resources", "version_conversion_int.json")
        self.xmlfile = os.path.join(dir_path, "resources", "version_conversion_int.xml")
        self.yamlfile = os.path.join(dir_path, "resources", "version_conversion_int.yaml")

        self.tmp_dir = tempfile.mkdtemp(suffix=".odml")
        self.outfile = os.path.join(self.tmp_dir, "version_conversion.xml")

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_convert_xml(self):
        VC(self.xmlfile).write_to_file(self.outfile)
        self.assertTrue(os.path.exists(self.outfile))

        self.check_result()

    def test_convert_yaml(self):
        with self.assertRaises(Exception):
            VC(self.yamlfile).write_to_file(self.outfile)

        VC(self.yamlfile).write_to_file(self.outfile, "YAML")
        self.assertTrue(os.path.exists(self.outfile))

        self.check_result()

    def test_convert_json(self):
        with self.assertRaises(Exception):
            VC(self.jsonfile).write_to_file(self.outfile)

        VC(self.jsonfile).write_to_file(self.outfile, "JSON")
        self.assertTrue(os.path.exists(self.outfile))

        self.check_result()

    def check_result(self):
        doc = load(self.outfile)

        # Test document attribute export
        self.assertEqual(doc.author, "author")
        self.assertEqual(doc.version, "v1.13")
        repo = "http://portal.g-node.org/odml/terminologies/v1.1/terminologies.xml"
        self.assertEqual(doc.repository, repo)
        self.assertEqual(len(doc.sections), 3)

        sec = doc.sections["sec_one"]
        self.assertEqual(sec.definition, "def s1")
        self.assertEqual(sec.reference, "ref s1")
        self.assertEqual(sec.type, "mainsec")
        self.assertEqual(len(sec.sections), 1)
        self.assertEqual(len(sec.properties), 3)

        prop = sec.properties["prop_one"]
        self.assertEqual(prop.definition, "def prop1")
        self.assertEqual(prop.dependency, "dep p1")
        self.assertEqual(prop.dependency_value, "dep val p1")
        self.assertEqual(prop.reference, "ref val 1")
        self.assertEqual(prop.uncertainty, "11")
        self.assertEqual(prop.unit, "arbitrary")
        self.assertEqual(prop.value_origin, "filename val 1")
        self.assertEqual(prop.dtype, "string")
        self.assertEqual(len(prop.value), 3)

        prop = sec.properties["prop_two"]
        self.assertEqual(len(prop.value), 8)

        prop = sec.properties["prop_three"]
        self.assertEqual(len(prop.value), 0)
