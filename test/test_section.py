import unittest

from odml import Property, Section, Document
from odml.doc import BaseDocument
from odml.section import BaseSection


class TestSection(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple_attributes(self):
        sec_name = "sec name"
        sec_type = "sec type"
        sec_def = "an odml test section"
        sec_ref = "from over there"

        sec = Section(name=sec_name, type=sec_type, definition=sec_def, reference=sec_ref)

        self.assertEqual(sec.name, sec_name)
        self.assertEqual(sec.type, sec_type)
        self.assertEqual(sec.definition, sec_def)
        self.assertEqual(sec.reference, sec_ref)

        # Test setting attributes
        sec.name = "%s_edit" % sec_name
        self.assertEqual(sec.name, "%s_edit" % sec_name)
        sec.type = "%s_edit" % sec_type
        self.assertEqual(sec.type, "%s_edit" % sec_type)
        sec.definition = "%s_edit" % sec_def
        self.assertEqual(sec.definition, "%s_edit" % sec_def)
        sec.reference = "%s_edit" % sec_ref
        self.assertEqual(sec.reference, "%s_edit" % sec_ref)

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

    def test_path(self):
        sec = Section(name="center")
        self.assertEqual(sec.get_path(), "/")

        subsec = Section(name="leaf", parent=sec)
        self.assertEqual(subsec.get_path(), "/leaf")

        doc = Document()
        sec.parent = doc
        self.assertEqual(sec.get_path(), "/center")
        self.assertEqual(subsec.get_path(), "/center/leaf")

        top = Section(name="top", parent=doc)
        sec.parent = top
        self.assertEqual(sec.get_path(), "/top/center")
        self.assertEqual(subsec.get_path(), "/top/center/leaf")

        subsec.parent = None
        self.assertEqual(subsec.get_path(), "/")

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

    def test_reorder(self):
        # Test reorder of document sections
        doc = Document()
        sec_one = Section(name="sec_one", parent=doc)
        sec_two = Section(name="sec_two", parent=doc)
        sec_three = Section(name="sec_three", parent=doc)

        self.assertEqual(doc.sections[0].name, sec_one.name)
        self.assertEqual(doc.sections[2].name, sec_three.name)
        sec_three.reorder(0)

        self.assertEqual(doc.sections[0].name, sec_three.name)
        self.assertEqual(doc.sections[2].name, sec_two.name)

        # Test reorder of document sections
        sec = Section(name="main")
        sec_one = Section(name="sec_one", parent=sec)
        sec_two = Section(name="sec_two", parent=sec)
        sec_three = Section(name="sec_three", parent=sec)

        self.assertEqual(sec.sections[0].name, sec_one.name)
        self.assertEqual(sec.sections[2].name, sec_three.name)
        sec_three.reorder(0)

        self.assertEqual(sec.sections[0].name, sec_three.name)
        self.assertEqual(sec.sections[2].name, sec_two.name)

        # Test Exception on unconnected section
        with self.assertRaises(ValueError):
            sec.reorder(0)

    def test_append(self):
        main = Section(name="main")
        self.assertListEqual(main.sections, [])
        self.assertListEqual(main.properties, [])

        # Test append Section
        sec = Section(name="sec1")
        main.append(sec)
        self.assertEqual(len(main.sections), 1)
        self.assertEqual(sec.parent, main)

        # Test fail on Section list append
        with self.assertRaises(ValueError):
            main.append([Section(name="sec2"), Section(name="sec3")])

        # Test append Property
        prop = Property(name="prop")
        main.append(prop)
        self.assertEqual(len(main.properties), 1)
        self.assertEqual(prop.parent, main)

        # Test fail on Property list append
        with self.assertRaises(ValueError):
            main.append([Property(name="prop2"), Property(name="prop3")])

        # Test fail on unsupported value
        with self.assertRaises(ValueError):
            main.append(Document())
        with self.assertRaises(ValueError):
            main.append("Section")

        # Test fail on same name entities
        with self.assertRaises(KeyError):
            main.append(Section(name="sec1"))
        with self.assertRaises(KeyError):
            main.append(Property(name="prop"))

    def test_extend(self):
        sec = Section(name="main")
        self.assertListEqual(sec.sections, [])
        self.assertListEqual(sec.properties, [])

        # Test extend with Section list
        sec.extend([Section(name="sec1"), Section(name="sec2")])
        self.assertEqual(len(sec), 2)
        self.assertEqual(len(sec.sections), 2)
        self.assertEqual(sec.sections[0].name, "sec1")

        # Test extend with Property list
        sec.extend((Property(name="prop1"), Property(name="prop2")))
        self.assertEqual(len(sec), 4)
        self.assertEqual(len(sec.properties), 2)
        self.assertEqual(sec.properties[0].name, "prop1")

        # Test extend with mixed list
        sec.extend([Section(name="sec3"), Property(name="prop3")])
        self.assertEqual(len(sec), 6)
        self.assertEqual(len(sec.sections), 3)
        self.assertEqual(len(sec.properties), 3)

        # Test fail on non iterable
        with self.assertRaises(TypeError):
            sec.extend(1)

        # Test fail on non Section/Property list entry
        with self.assertRaises(ValueError):
            sec.extend([Property(name="prop4"), 5])

        # Test fail on same name entities
        with self.assertRaises(KeyError):
            sec.extend([Property(name="new"), Property(name="prop3")])
        self.assertEqual(len(sec.properties), 3)

        with self.assertRaises(KeyError):
            sec.extend([Section(name="new"), Section(name="sec3")])
        self.assertEqual(len(sec.sections), 3)

    def test_remove(self):
        sec = Section(name="remsec")

        ssec_one = Section(name="subsec_one", parent=sec)
        ssec_two = Section(name="subsec_two", parent=sec)
        self.assertEqual(len(sec.sections), 2)
        self.assertIsNotNone(ssec_one.parent)

        sec.remove(ssec_one)
        self.assertEqual(len(sec.sections), 1)
        self.assertEqual(sec.sections[0].name, ssec_two.name)
        self.assertIsNone(ssec_one.parent)

        with self.assertRaises(ValueError):
            sec.remove(ssec_one)
        self.assertEqual(len(sec.sections), 1)

        prop_one = Property(name="prop_one", parent=sec)
        prop_two = Property(name="prop_two", parent=sec)
        self.assertEqual(len(sec.properties), 2)
        self.assertIsNotNone(prop_one.parent)

        sec.remove(prop_one)
        self.assertEqual(len(sec.properties), 1)
        self.assertEqual(sec.properties[0].name, prop_two.name)
        self.assertIsNone(prop_one.parent)

        with self.assertRaises(ValueError):
            sec.remove(prop_one)
        self.assertEqual(len(sec.properties), 1)

        with self.assertRaises(ValueError):
            sec.remove("prop_two")
