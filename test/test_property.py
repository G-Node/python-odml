import unittest
from odml import Property, Section, Document
from odml.section import BaseSection


class TestProperty(unittest.TestCase):

    def setUp(self):
        pass

    def test_value(self):
        p = Property("property", 100)
        self.assertEqual(p.value[0], 100)

    def test_name(self):
        pass

    def test_parent(self):
        p = Property("property_section", parent=Section("S"))
        self.assertIsInstance(p.parent, BaseSection)
        self.assertEqual(len(p.parent._props), 1)
        with self.assertRaises(ValueError):
            Property("property_prop", parent=Property("P"))
        with self.assertRaises(ValueError):
            Property("property_doc", parent=Document())

    def test_dtype(self):
        pass

    def test_path(self):
        pass



