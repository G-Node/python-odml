import unittest
from odml import Property, Section, Document
from odml.doc import BaseDocument
from odml.section import BaseSection


class TestSection(unittest.TestCase):
    def setUp(self):
        pass

    def test_value(self):
        pass

    def test_name(self):
        pass

    def test_parent(self):
        s = Section("Section")
        self.assertIsNone(s.parent)

        s = Section("section_doc", parent=Document())
        self.assertIsInstance(s.parent, BaseDocument)
        self.assertEqual(len(s.parent._sections), 1)

        s = Section("section_sec", parent=Section("S"))
        self.assertIsInstance(s.parent, BaseSection)
        self.assertEqual(len(s.parent._sections), 1)

        with self.assertRaises(ValueError):
            Section("section_property", parent=Property("P"))

    def test_dtype(self):
        pass

    def test_path(self):
        pass
