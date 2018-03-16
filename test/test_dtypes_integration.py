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
            shutil.rmtree(self.tmp_dir)

    def test_time(self):
        pass

    def test_date(self):
        pass

    def test_datetime(self):
        pass

    def test_int(self):
        pass

    def test_float(self):
        pass

    def test_str(self):
        pass

    def test_bool(self):
        pass

    def test_tuple(self):
        pass
