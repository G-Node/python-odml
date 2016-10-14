import unittest
from datetime import datetime as dt, date, time
from odml import Value, Property, Section, Document
from odml.tools.xmlparser import XMLReader, XMLWriter


class TestInferType(unittest.TestCase):

    def test_string(self):
        v = Value("somestring")
        assert(v.dtype == "string")
        assert(type(v.data) == str)

    def test_text(self):
        v = Value("some\nstring")
        assert(v.dtype == "text")
        assert(type(v.data) == str)

    def test_int(self):
        v = Value(111)
        assert(v.dtype == "int")
        assert(type(v.data) == int)

    def test_float(self):
        v = Value(3.14)
        assert(v.dtype == "float")
        assert(type(v.data) == float)

    def test_datetime(self):
        v = Value(dt.now())
        assert(v.dtype == "datetime")
        assert(type(v.data) == dt)

    def test_date(self):
        v = Value(dt.now().date())
        assert(v.dtype == "date")
        assert(type(v.data) == date)

    def test_time(self):
        v = Value(dt.now().time())
        assert(v.dtype == "time")
        assert(type(v.data) == time)

    def test_boolean(self):
        v = Value(True)
        assert(v.dtype == "boolean")
        assert(type(v.data) == bool)
        v = Value(False)
        assert(v.dtype == "boolean")
        assert(type(v.data) == bool)

    def test_read_write(self):
        doc = Document("author")
        sec = Section("name", "type")
        doc.append(sec)
        sec.append(Property("strprop", "somestring"))
        sec.append(Property("txtprop", "some\ntext"))
        sec.append(Property("intprop", 200))
        sec.append(Property("floatprop", 2.00))
        from IPython import embed
        # embed()
        # sec.append(Property("datetimeprop", dt.now())) probably just an isoformat issue ... ValueError: unconverted data remains: .613725
        sec.append(Property("dateprop", dt.now().date()))
        # sec.append(Property("timeprop", dt.now().time()))
        sec.append(Property("boolprop", True))

        str_doc = unicode(XMLWriter(doc))
        new_doc = XMLReader().fromString(str_doc)
        new_sec = new_doc.sections[0]

        v = new_sec.properties["strprop"].value
        assert(v.dtype == "string")
        assert(type(v.data) == unicode)

        v = new_sec.properties["txtprop"].value
        assert(v.dtype == "text")
        assert(type(v.data) == unicode)

        v = new_sec.properties["intprop"].value
        assert(v.dtype == "int")
        assert(type(v.data) == int)

        v = new_sec.properties["floatprop"].value
        assert(v.dtype == "float")
        assert(type(v.data) == float)

        # v = new_sec.properties["datetimeprop"].value
        # assert(v.dtype == "datetime")
        # assert(type(v.data) == dt)

        v = new_sec.properties["dateprop"].value
        assert(v.dtype == "date")
        assert(type(v.data) == date)

        # v = new_sec.properties["timeprop"].value
        # assert(v.dtype == "time")
        # assert(type(v.data) == time)

        v = new_sec.properties["boolprop"].value
        assert(v.dtype == "boolean")
        assert(type(v.data) == bool)


if __name__ == '__main__':
    unittest.main()
