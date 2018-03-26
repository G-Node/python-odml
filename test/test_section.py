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
        s.parent = None
        self.assertIsNone(s.parent)
        s.parent = Document()
        self.assertIsInstance(s.parent, BaseDocument)
        self.assertIsInstance(s.parent._sections[0], BaseSection)

        """ Test if child is removed from _sections of a parent after assigning
            a new parent to the child """
        p = s.parent
        s.parent = Section("S")
        self.assertEqual(len(p._sections), 0)

        s = Section("section_doc", parent=Document())
        self.assertIsInstance(s.parent, BaseDocument)
        self.assertEqual(len(s.parent._sections), 1)
        p = s.parent
        s.parent = None
        self.assertEqual(len(p._sections), 0)
        self.assertEqual(s.parent, None)

        s = Section("section_sec", parent=Section("S"))
        self.assertIsInstance(s.parent, BaseSection)
        self.assertEqual(len(s.parent._sections), 1)
        p = s.parent
        s.parent = None
        self.assertEqual(len(p._sections), 0)
        self.assertEqual(s.parent, None)

        with self.assertRaises(ValueError):
            Section("section_property", parent=Property("P"))

    def test_dtype(self):
        pass

    def test_path(self):
        pass

    def test_id(self):
        s = Section(name="S")
        self.assertIsNotNone(s.id)

        s = Section("S", id="79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertEqual(s.id, "79b613eb-a256-46bf-84f6-207df465b8f7")

        s = Section("S", id="id")
        self.assertNotEqual(s.id, "id")

        # Make sure id cannot be reset programmatically.
        with self.assertRaises(AttributeError):
            s.id = "someId"

    def test_new_id(self):
        sec = Section(name="sec")
        old_id = sec.id

        # Test assign new generated id.
        sec.new_id()
        self.assertNotEqual(old_id, sec.id)

        # Test assign new custom id.
        old_id = sec.id
        sec.new_id("79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertNotEqual(old_id, sec.id)
        self.assertEqual("79b613eb-a256-46bf-84f6-207df465b8f7", sec.id)

        # Test invalid custom id exception.
        with self.assertRaises(ValueError):
            sec.new_id("crash and burn")

    def test_clone(self):
        # Check parent removal in clone.
        psec = Section(name="parent")
        sec = Section(name="original", parent=psec)
        clone_sec = sec.clone()
        self.assertEqual(sec.parent, psec)
        self.assertIsNone(clone_sec.parent)

        # Check new id in clone.
        sec = Section(name="original")
        clone_sec = sec.clone()
        self.assertEqual(sec, clone_sec)
        self.assertNotEqual(sec.id, clone_sec.id)

        # Check child Sections and Properties are cloned and have new ids.
        Section(name="sec_one", parent=sec)
        Section(name="sec_two", parent=sec)
        Property(name="prop_one", parent=sec)
        Property(name="prop_two", parent=sec)

        clone_sec = sec.clone()

        # Check sections
        self.assertListEqual(sec.sections, clone_sec.sections)
        self.assertEqual(sec.sections["sec_one"], clone_sec.sections["sec_one"])
        self.assertNotEqual(sec.sections["sec_one"].id, clone_sec.sections["sec_one"].id)

        # Check properties
        self.assertListEqual(sec.properties, clone_sec.properties)
        self.assertEqual(sec.properties["prop_one"], clone_sec.properties["prop_one"])
        self.assertNotEqual(sec.properties["prop_one"].id,
                            clone_sec.properties["prop_one"].id)

        # Check child Sections and Properties are not cloned.
        clone_sec = sec.clone(children=False)

        self.assertListEqual(clone_sec.sections, [])
        self.assertListEqual(clone_sec.properties, [])
