"""
This file tests proper creation, saving and loading
of all supported odML datatypes with all supported
odML parsers.
"""

import datetime as dt
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
        time_string = '12:34:56'
        time = dt.time(12, 34, 56)
        val_in = time_string
        vals_in = [None, "", time_string, time]
        parent_sec = self.doc.sections[0]
        _ = odml.Property(name="time test single", dtype="time",
                          value=val_in, parent=parent_sec)
        _ = odml.Property(name="time test", dtype="time",
                          value=vals_in, parent=parent_sec)

        # Test correct json save and load.
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        self.assertEqual(jdoc.sections[0].properties[0].dtype, odml.dtypes.DType.time)
        self.assertIsInstance(jdoc.sections[0].properties[0].value[0], dt.time)
        self.assertEqual(jdoc.sections[0].properties[1].dtype, odml.dtypes.DType.time)
        for val in jdoc.sections[0].properties[1].value:
            self.assertIsInstance(val, dt.time)
        self.assertEqual(jdoc.sections[0].properties[1].value[2], time)
        self.assertEqual(jdoc.sections[0].properties[1].value[3], time)
        self.assertEqual(self.doc, jdoc)

        # Test correct xml save and load.
        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        self.assertEqual(xdoc.sections[0].properties[0].dtype, odml.dtypes.DType.time)
        self.assertIsInstance(xdoc.sections[0].properties[0].value[0], dt.time)
        self.assertEqual(xdoc.sections[0].properties[1].dtype, odml.dtypes.DType.time)
        for val in xdoc.sections[0].properties[1].value:
            self.assertIsInstance(val, dt.time)
        self.assertEqual(xdoc.sections[0].properties[1].value[2], time)
        self.assertEqual(xdoc.sections[0].properties[1].value[2], time)
        self.assertEqual(self.doc, xdoc)

        # Test correct yaml save and load.
        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        self.assertEqual(ydoc.sections[0].properties[0].dtype, odml.dtypes.DType.time)
        self.assertIsInstance(ydoc.sections[0].properties[0].value[0], dt.time)
        self.assertEqual(ydoc.sections[0].properties[1].dtype, odml.dtypes.DType.time)
        for val in ydoc.sections[0].properties[1].value:
            self.assertIsInstance(val, dt.time)
        self.assertEqual(ydoc.sections[0].properties[1].value[2], time)
        self.assertEqual(ydoc.sections[0].properties[1].value[2], time)
        self.assertEqual(self.doc, ydoc)

    def test_date(self):
        date_string = '2018-08-31'
        date = dt.date(2018, 8, 31)
        val_in = date_string
        vals_in = [None, "", date_string, date]
        parent_sec = self.doc.sections[0]
        _ = odml.Property(name="date test single", dtype="date",
                          value=val_in, parent=parent_sec)
        _ = odml.Property(name="date test", dtype="date",
                          value=vals_in, parent=parent_sec)

        # Test correct json save and load.
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        self.assertEqual(jdoc.sections[0].properties[0].dtype, odml.dtypes.DType.date)
        self.assertIsInstance(jdoc.sections[0].properties[0].value[0], dt.date)
        self.assertEqual(jdoc.sections[0].properties[1].dtype, odml.dtypes.DType.date)
        for val in jdoc.sections[0].properties[1].value:
            self.assertIsInstance(val, dt.date)
        self.assertEqual(jdoc.sections[0].properties[1].value[2], date)
        self.assertEqual(jdoc.sections[0].properties[1].value[3], date)
        self.assertEqual(self.doc, jdoc)

        # Test correct xml save and load.
        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        self.assertEqual(xdoc.sections[0].properties[0].dtype, odml.dtypes.DType.date)
        self.assertIsInstance(xdoc.sections[0].properties[0].value[0], dt.date)
        self.assertEqual(xdoc.sections[0].properties[1].dtype, odml.dtypes.DType.date)
        for val in xdoc.sections[0].properties[1].value:
            self.assertIsInstance(val, dt.date)
        self.assertEqual(xdoc.sections[0].properties[1].value[2], date)
        self.assertEqual(xdoc.sections[0].properties[1].value[2], date)
        self.assertEqual(self.doc, xdoc)

        # Test correct yaml save and load.
        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        self.assertEqual(ydoc.sections[0].properties[0].dtype, odml.dtypes.DType.date)
        self.assertIsInstance(ydoc.sections[0].properties[0].value[0], dt.date)
        self.assertEqual(ydoc.sections[0].properties[1].dtype, odml.dtypes.DType.date)
        for val in ydoc.sections[0].properties[1].value:
            self.assertIsInstance(val, dt.date)
        self.assertEqual(ydoc.sections[0].properties[1].value[2], date)
        self.assertEqual(ydoc.sections[0].properties[1].value[2], date)
        self.assertEqual(self.doc, ydoc)

    def test_datetime(self):
        datetime_string = '2018-08-31 12:59:59'
        date_time = dt.datetime(2018, 8, 31, 12, 59, 59)
        val_in = datetime_string
        vals_in = [None, "", datetime_string, date_time]
        parent_sec = self.doc.sections[0]
        _ = odml.Property(name="datetime test single", dtype="datetime",
                          value=val_in, parent=parent_sec)
        _ = odml.Property(name="datetime test", dtype="datetime",
                          value=vals_in, parent=parent_sec)

        # Test correct json save and load.
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        self.assertEqual(jdoc.sections[0].properties[0].dtype, odml.dtypes.DType.datetime)
        self.assertIsInstance(jdoc.sections[0].properties[0].value[0], dt.datetime)
        self.assertEqual(jdoc.sections[0].properties[1].dtype, odml.dtypes.DType.datetime)
        for val in jdoc.sections[0].properties[1].value:
            self.assertIsInstance(val, dt.datetime)
        self.assertEqual(jdoc.sections[0].properties[1].value[2], date_time)
        self.assertEqual(jdoc.sections[0].properties[1].value[3], date_time)
        self.assertEqual(self.doc, jdoc)

        # Test correct xml save and load.
        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        self.assertEqual(xdoc.sections[0].properties[0].dtype, odml.dtypes.DType.datetime)
        self.assertIsInstance(xdoc.sections[0].properties[0].value[0], dt.datetime)
        self.assertEqual(xdoc.sections[0].properties[1].dtype, odml.dtypes.DType.datetime)
        for val in xdoc.sections[0].properties[1].value:
            self.assertIsInstance(val, dt.datetime)
        self.assertEqual(xdoc.sections[0].properties[1].value[2], date_time)
        self.assertEqual(xdoc.sections[0].properties[1].value[2], date_time)
        self.assertEqual(self.doc, xdoc)

        # Test correct yaml save and load.
        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        self.assertEqual(ydoc.sections[0].properties[0].dtype, odml.dtypes.DType.datetime)
        self.assertIsInstance(ydoc.sections[0].properties[0].value[0], dt.datetime)
        self.assertEqual(ydoc.sections[0].properties[1].dtype, odml.dtypes.DType.datetime)
        for val in ydoc.sections[0].properties[1].value:
            self.assertIsInstance(val, dt.datetime)
        self.assertEqual(ydoc.sections[0].properties[1].value[2], date_time)
        self.assertEqual(ydoc.sections[0].properties[1].value[2], date_time)
        self.assertEqual(self.doc, ydoc)

    def test_int(self):
        val_in = [1, 2, 3, "4"]
        val_odml = [1, 2, 3, 4]
        parent_sec = self.doc.sections[0]
        _ = odml.Property(name="int test", dtype="int", value=val_in, parent=parent_sec)

        # Test correct json save and load.
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        self.assertEqual(jdoc.sections[0].properties[0].dtype, odml.dtypes.DType.int)
        self.assertEqual(jdoc.sections[0].properties[0].value, val_odml)
        self.assertEqual(self.doc, jdoc)

        # Test correct xml save and load.
        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        self.assertEqual(xdoc.sections[0].properties[0].dtype, odml.dtypes.DType.int)
        self.assertEqual(xdoc.sections[0].properties[0].value, val_odml)
        self.assertEqual(self.doc, xdoc)

        # Test correct yaml save and load.
        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        self.assertEqual(ydoc.sections[0].properties[0].dtype, odml.dtypes.DType.int)
        self.assertEqual(ydoc.sections[0].properties[0].value, val_odml)
        self.assertEqual(self.doc, ydoc)

    def test_float(self):
        val_in = [1, 2.2, 3.3, "4"]
        val_odml = [1.0, 2.2, 3.3, 4.0]
        parent_sec = self.doc.sections[0]
        _ = odml.Property(name="float test", dtype="float",
                          value=val_in, parent=parent_sec)

        # Test correct json save and load.
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        self.assertEqual(jdoc.sections[0].properties[0].dtype, odml.dtypes.DType.float)
        self.assertEqual(jdoc.sections[0].properties[0].value, val_odml)
        self.assertEqual(self.doc, jdoc)

        # Test correct xml save and load.
        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        self.assertEqual(xdoc.sections[0].properties[0].dtype, odml.dtypes.DType.float)
        self.assertEqual(xdoc.sections[0].properties[0].value, val_odml)
        self.assertEqual(self.doc, xdoc)

        # Test correct yaml save and load.
        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        self.assertEqual(ydoc.sections[0].properties[0].dtype, odml.dtypes.DType.float)
        self.assertEqual(ydoc.sections[0].properties[0].value, val_odml)
        self.assertEqual(self.doc, ydoc)

    def test_str(self):
        val_in = "single value"
        vals_in = [None, "", [], {}, 1, True, "text"]
        vals_odml = ["", "", "", "", "1", "True", "text"]
        parent_sec = self.doc.sections[0]
        _ = odml.Property(name="string test single", dtype="string",
                          value=val_in, parent=parent_sec)
        _ = odml.Property(name="string test", dtype="string",
                          value=vals_in, parent=parent_sec)

        # Test correct json save and load.
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        self.assertEqual(jdoc.sections[0].properties[0].dtype, odml.dtypes.DType.string)
        self.assertEqual(jdoc.sections[0].properties[0].value, [val_in])
        self.assertEqual(jdoc.sections[0].properties[1].dtype, odml.dtypes.DType.string)
        self.assertEqual(jdoc.sections[0].properties[1].value, vals_odml)
        self.assertEqual(self.doc, jdoc)

        # Test correct xml save and load.
        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        self.assertEqual(xdoc.sections[0].properties[0].dtype, odml.dtypes.DType.string)
        self.assertEqual(xdoc.sections[0].properties[0].value, [val_in])
        self.assertEqual(xdoc.sections[0].properties[1].dtype, odml.dtypes.DType.string)
        self.assertEqual(xdoc.sections[0].properties[1].value, vals_odml)
        self.assertEqual(self.doc, xdoc)

        # Test correct yaml save and load.
        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        self.assertEqual(ydoc.sections[0].properties[0].dtype, odml.dtypes.DType.string)
        self.assertEqual(ydoc.sections[0].properties[0].value, [val_in])
        self.assertEqual(ydoc.sections[0].properties[1].dtype, odml.dtypes.DType.string)
        self.assertEqual(ydoc.sections[0].properties[1].value, vals_odml)
        self.assertEqual(self.doc, ydoc)

    def test_bool(self):
        val_in = True
        vals_in = [None, "", [], {}, False, True, "TRUE"]
        vals_odml = [False, False, False, False, False, True, True]
        parent_sec = self.doc.sections[0]
        _ = odml.Property(name="bool test single", dtype="boolean",
                          value=val_in, parent=parent_sec)
        _ = odml.Property(name="bool test", dtype="boolean",
                          value=vals_in, parent=parent_sec)

        # Test correct json save and load.
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        self.assertEqual(jdoc.sections[0].properties[0].dtype, odml.dtypes.DType.boolean)
        self.assertEqual(jdoc.sections[0].properties[0].value, [val_in])
        self.assertEqual(jdoc.sections[0].properties[1].dtype, odml.dtypes.DType.boolean)
        self.assertEqual(jdoc.sections[0].properties[1].value, vals_odml)
        self.assertEqual(self.doc, jdoc)

        # Test correct xml save and load.
        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        self.assertEqual(xdoc.sections[0].properties[0].dtype, odml.dtypes.DType.boolean)
        self.assertEqual(xdoc.sections[0].properties[0].value, [val_in])
        self.assertEqual(xdoc.sections[0].properties[1].dtype, odml.dtypes.DType.boolean)
        self.assertEqual(xdoc.sections[0].properties[1].value, vals_odml)
        self.assertEqual(self.doc, xdoc)

        # Test correct yaml save and load.
        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        self.assertEqual(ydoc.sections[0].properties[0].dtype, odml.dtypes.DType.boolean)
        self.assertEqual(ydoc.sections[0].properties[0].value, [val_in])
        self.assertEqual(ydoc.sections[0].properties[1].dtype, odml.dtypes.DType.boolean)
        self.assertEqual(ydoc.sections[0].properties[1].value, vals_odml)
        self.assertEqual(self.doc, ydoc)

    def test_tuple(self):
        val_type = "3-tuple"
        val_in = "(1; 1; 1)"
        val_odml = ["1", "1", "1"]

        parent_sec = self.doc.sections[0]
        _ = odml.Property(name="tuple test single", dtype=val_type,
                          value=val_in, parent=parent_sec)

        # Test correct json save and load.
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        self.assertEqual(jdoc.sections[0].properties[0].dtype, val_type)
        self.assertEqual(jdoc.sections[0].properties[0].value, [val_odml])
        self.assertEqual(self.doc, jdoc)

        # Test correct xml save and load.
        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        self.assertEqual(xdoc.sections[0].properties[0].dtype, val_type)
        self.assertEqual(xdoc.sections[0].properties[0].value, [val_odml])
        self.assertEqual(self.doc, xdoc)

        # Test correct yaml save and load.
        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        self.assertEqual(ydoc.sections[0].properties[0].dtype, val_type)
        self.assertEqual(ydoc.sections[0].properties[0].value, [val_odml])
        self.assertEqual(self.doc, ydoc)
