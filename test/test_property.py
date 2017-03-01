import unittest
import sys
from datetime import datetime as dt, date, time
from odml import Property, Section, Document
from odml.tools.xmlparser import XMLReader, XMLWriter
from IPython import embed


class TestProperty(unittest.TestCase):

    def setUp(self):
        pass

    def test_value(self):
        p = Property("property", 100)
        assert(p.value[0] == 100)

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
