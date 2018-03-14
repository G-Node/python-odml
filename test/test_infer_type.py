import unittest
import sys
from datetime import datetime as dt, date, time
from odml import Property, Section, Document
from odml.tools.xmlparser import XMLReader, XMLWriter


class TestInferType(unittest.TestCase):

    def test_string(self):
        p = Property("test", value="somestring")
        assert(p.dtype == "string")
        if sys.version_info < (3, 0):
            assert isinstance(p.value[0], unicode)
        else:
            assert isinstance(p.value[0], str)

    def test_text(self):
        p = Property("test", value="some\nstring")
        assert(p.dtype == "text")
        if sys.version_info < (3, 0):
            assert isinstance(p.value[0], unicode)
        else:
            assert isinstance(p.value[0], str)

    def test_int(self):
        p = Property("test", value=111)
        assert(p.dtype == "int")
        assert isinstance(p.value[0], int)

    def test_float(self):
        p = Property("test", value=3.14)
        assert(p.dtype == "float")
        assert isinstance(p.value[0], float)

    def test_datetime(self):
        p = Property("test", value=dt.now())
        assert(p.dtype == "datetime")
        assert isinstance(p.value[0], dt)

    def test_date(self):
        p = Property("test", dt.now().date())
        assert(p.dtype == "date")
        assert isinstance(p.value[0], date)

    def test_time(self):
        p = Property("test", value=dt.now().time())
        assert(p.dtype == "time")
        assert isinstance(p.value[0], time)

    def test_boolean(self):
        p = Property("test", True)
        assert(p.dtype == "boolean")
        assert isinstance(p.value[0], bool)

        p = Property("test", False)
        assert(p.dtype == "boolean")
        assert isinstance(p.value[0], bool)

    def test_read_write(self):
        doc = Document("author")
        sec = Section("name", "type")
        doc.append(sec)
        sec.append(Property("strprop", "somestring"))
        sec.append(Property("txtprop", "some\ntext"))
        sec.append(Property("intprop", 200))
        sec.append(Property("floatprop", 2.00))
        sec.append(Property("datetimeprop", dt.now()))
        sec.append(Property("dateprop", dt.now().date()))
        sec.append(Property("timeprop", dt.now().time()))
        sec.append(Property("boolprop", True))
        if sys.version_info < (3, 0):
            str_doc = unicode(XMLWriter(doc))
        else:
            str_doc = str(XMLWriter(doc))
        new_doc = XMLReader().from_string(str_doc)
        new_sec = new_doc.sections[0]

        p = new_sec.properties["strprop"]
        assert(p.dtype == "string")
        if sys.version_info < (3, 0):
            assert isinstance(p.value[0], unicode)
        else:
            assert isinstance(p.value[0], str)

        p = new_sec.properties["txtprop"]
        assert(p.dtype == "text")
        if sys.version_info < (3, 0):
            assert isinstance(p.value[0], unicode)
        else:
            assert isinstance(p.value[0], str)

        p = new_sec.properties["intprop"]
        assert(p.dtype == "int")
        assert isinstance(p.value[0], int)

        p = new_sec.properties["floatprop"]
        assert(p.dtype == "float")
        assert isinstance(p.value[0], float)

        p = new_sec.properties["datetimeprop"]
        assert(p.dtype == "datetime")
        assert isinstance(p.value[0], dt)

        p = new_sec.properties["dateprop"]
        assert(p.dtype == "date")
        assert isinstance(p.value[0], date)

        p = new_sec.properties["timeprop"]
        assert(p.dtype == "time")
        assert isinstance(p.value[0], time)

        p = new_sec.properties["boolprop"]
        assert(p.dtype == "boolean")
        assert isinstance(p.value[0], bool)
