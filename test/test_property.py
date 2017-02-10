import unittest
import sys
from datetime import datetime as dt, date, time
from odml import Value, Property, Section, Document
from odml.tools.xmlparser import XMLReader, XMLWriter
from IPython import embed


class TestProperty(unittest.TestCase):

    def setUp(self):
        pass

    def test_value(self):

        v = Value("A value")
        p = Property("property", v)
        assert(p.value == v)

    def test_name(self):
        pass

    def test_parent(self):
        pass

    def test_dtype(self):
        pass

    def test_path(self):
        pass

if __name__ == "__main__":
    print("TestProperty")
    tp = TestProperty()
    tp.test_value()
