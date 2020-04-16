import unittest

from datetime import datetime as dt, date, time

from odml import Property, Section, Document
from odml.tools.xmlparser import XMLReader, XMLWriter

try:
    unicode = unicode
except NameError:
    unicode = str


class TestInferType(unittest.TestCase):

    def test_string(self):
        prop = Property("test", value="some_string")
        self.assertEqual(prop.dtype, "string")
        self.assertIsInstance(prop.values[0], unicode)

    def test_text(self):
        prop = Property("test", value="some\nstring")
        self.assertEqual(prop.dtype, "text")
        self.assertIsInstance(prop.values[0], unicode)

    def test_int(self):
        prop = Property("test", value=111)
        self.assertEqual(prop.dtype, "int")
        self.assertIsInstance(prop.values[0], int)

    def test_float(self):
        prop = Property("test", value=3.14)
        self.assertEqual(prop.dtype, "float")
        self.assertIsInstance(prop.values[0], float)

    def test_datetime(self):
        prop = Property("test", value=dt.now())
        self.assertEqual(prop.dtype, "datetime")
        self.assertIsInstance(prop.values[0], dt)

    def test_date(self):
        prop = Property("test", dt.now().date())
        self.assertEqual(prop.dtype, "date")
        self.assertIsInstance(prop.values[0], date)

    def test_time(self):
        prop = Property("test", value=dt.now().time())
        self.assertEqual(prop.dtype, "time")
        self.assertIsInstance(prop.values[0], time)

    def test_boolean(self):
        prop = Property("test", True)
        self.assertEqual(prop.dtype, "boolean")
        self.assertIsInstance(prop.values[0], bool)

        prop = Property("test", False)
        self.assertEqual(prop.dtype, "boolean")
        self.assertIsInstance(prop.values[0], bool)

    def test_read_write(self):
        doc = Document("author")
        sec = Section("name", "type", parent=doc)

        sec.append(Property("strprop", "somestring"))
        sec.append(Property("txtprop", "some\ntext"))
        sec.append(Property("intprop", 200))
        sec.append(Property("floatprop", 2.00))
        sec.append(Property("datetimeprop", dt.now()))
        sec.append(Property("dateprop", dt.now().date()))
        sec.append(Property("timeprop", dt.now().time()))
        sec.append(Property("boolprop", True))

        str_doc = unicode(XMLWriter(doc))

        new_doc = XMLReader().from_string(str_doc)
        new_sec = new_doc.sections[0]

        prop = new_sec.properties["strprop"]
        self.assertEqual(prop.dtype, "string")
        self.assertIsInstance(prop.values[0], unicode)

        prop = new_sec.properties["txtprop"]
        self.assertEqual(prop.dtype, "text")
        self.assertIsInstance(prop.values[0], unicode)

        prop = new_sec.properties["intprop"]
        self.assertEqual(prop.dtype, "int")
        self.assertIsInstance(prop.values[0], int)

        prop = new_sec.properties["floatprop"]
        self.assertEqual(prop.dtype, "float")
        self.assertIsInstance(prop.values[0], float)

        prop = new_sec.properties["datetimeprop"]
        self.assertEqual(prop.dtype, "datetime")
        self.assertIsInstance(prop.values[0], dt)

        prop = new_sec.properties["dateprop"]
        self.assertEqual(prop.dtype, "date")
        self.assertIsInstance(prop.values[0], date)

        prop = new_sec.properties["timeprop"]
        self.assertEqual(prop.dtype, "time")
        self.assertIsInstance(prop.values[0], time)

        prop = new_sec.properties["boolprop"]
        self.assertEqual(prop.dtype, "boolean")
        self.assertIsInstance(prop.values[0], bool)
