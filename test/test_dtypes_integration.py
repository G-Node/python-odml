"""
This file tests proper creation, saving and loading
of all supported odML datatypes with all supported
odML parsers.
"""

import os
import shutil
import tempfile
import unittest

import odml


class TestTypesIntegration(unittest.TestCase):

    def setUp(self):
        # Set up test environment
        self.tmp_dir = tempfile.mkdtemp(suffix=".odml")

        self.json_file = os.path.join(self.tmp_dir, "test.json")
        self.xml_file = os.path.join(self.tmp_dir, "test.xml")
        self.yaml_file = os.path.join(self.tmp_dir, "test.yaml")

        # Set up odML document stub
        doc = odml.Document()
        _ = odml.Section(name="dtypes", type="test", parent=doc)
        self.doc = doc

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            #shutil.rmtree(self.tmp_dir)
            pass

    def test_time(self):
        pass

    def test_date(self):
        pass

    def test_datetime(self):
        pass

    def test_int(self):
        val_in = [1, 2, 3, "4"]
        val_odml = [1, 2, 3, 4]
        parent_sec = self.doc.sections[0]
        _ = odml.Property(name="int test", dtype="int", value=val_in, parent=parent_sec)

        # Test correct json save and load.
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        self.assertEqual(self.doc, jdoc)
        self.assertEqual(jdoc.sections[0].properties[0].dtype, odml.dtypes.DType.int)
        self.assertEqual(jdoc.sections[0].properties[0].value, val_odml)

        # Test correct xml save and load.
        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        self.assertEqual(self.doc, xdoc)
        self.assertEqual(xdoc.sections[0].properties[0].dtype, odml.dtypes.DType.int)
        self.assertEqual(xdoc.sections[0].properties[0].value, val_odml)

        # Test correct yaml save and load.
        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        self.assertEqual(self.doc, ydoc)
        self.assertEqual(ydoc.sections[0].properties[0].dtype, odml.dtypes.DType.int)
        self.assertEqual(ydoc.sections[0].properties[0].value, val_odml)

    def test_float(self):
        pass

    def test_str(self):
        pass

    def test_bool(self):
        pass

    def test_tuple(self):
        pass
