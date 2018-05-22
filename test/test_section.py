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

        # Test setting attributes to None when '' is passed.
        sec.reference = ""
        self.assertIsNone(sec.reference)
        sec.definition = ""
        self.assertIsNone(sec.definition)

    def test_name(self):
        # Test id is used when name is not provided
        s = Section()
        self.assertIsNotNone(s.name)
        self.assertEqual(s.name, s.id)

        # Test name is properly set on init
        name = "rumpelstilzchen"
        s = Section(name)
        self.assertEqual(s.name, name)

        name = "rumpelstilzchen"
        s = Section(name=name)
        self.assertEqual(s.name, name)

        # Test name can be properly set on single and connected Sections
        sec = Section()
        self.assertNotEqual(sec.name, "sec")
        sec.name = "sec"
        self.assertEqual(sec.name, "sec")

        subsec_a = Section(parent=sec)
        self.assertNotEqual(subsec_a.name, "subsec_a")
        subsec_a.name = "subsec_a"
        self.assertEqual(subsec_a.name, "subsec_a")

        # Test subsection name can be changed with siblings
        subsec_b = Section(name="subsec_b", parent=sec)
        self.assertEqual(subsec_b.name, "subsec_b")
        subsec_b.name = "subsec"
        self.assertEqual(subsec_b.name, "subsec")

        # Test subsection name set will fail on existing sibling with same name
        with self.assertRaises(KeyError):
            subsec_b.name = "subsec_a"
        self.assertEqual(subsec_b.name, "subsec")

        # Test section name set will fail on existing same name document sibling
        doc = Document()
        sec_a = Section(name="a", parent=doc)
        sec_b = Section(name="b", parent=doc)
        with self.assertRaises(KeyError):
            sec_b.name = "a"

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

    def test_children(self):
        sec = Section(name="sec")

        # Test set sections
        subsec = Section(name="subsec", parent=sec)
        newsec = Section(name="newsec")

        self.assertEqual(subsec.parent, sec)
        self.assertEqual(sec.sections[0], subsec)
        self.assertEqual(len(sec.sections), 1)
        self.assertIsNone(newsec.parent)

        sec.sections[0] = newsec
        self.assertEqual(newsec.parent, sec)
        self.assertEqual(sec.sections[0], newsec)
        self.assertEqual(len(sec.sections), 1)
        self.assertIsNone(subsec.parent)

        # Test parent cleanup
        root = Section(name="root")
        sec.parent = root
        subsec.parent = newsec

        self.assertEqual(len(newsec.sections), 1)
        self.assertEqual(newsec.sections[0], subsec)
        self.assertEqual(subsec.parent, newsec)
        self.assertEqual(len(root.sections), 1)
        self.assertEqual(root.sections[0], sec)

        subsec.parent = root
        self.assertEqual(len(newsec.sections), 0)
        self.assertEqual(subsec.parent, root)
        self.assertEqual(len(root.sections), 2)
        self.assertEqual(root.sections[1], subsec)

        # Test set section fails
        with self.assertRaises(ValueError):
            sec.sections[0] = Document()
        with self.assertRaises(ValueError):
            sec.sections[0] = Property("fail")
        with self.assertRaises(ValueError):
            sec.sections[0] = "subsec"

        # Test set properties
        prop = Property(name="prop", parent=sec)
        newprop = Property(name="newprop")

        self.assertEqual(prop.parent, sec)
        self.assertEqual(sec.properties[0], prop)
        self.assertEqual(len(sec.properties), 1)
        self.assertIsNone(newprop.parent)

        sec.properties[0] = newprop
        self.assertEqual(newprop.parent, sec)
        self.assertEqual(sec.properties[0], newprop)
        self.assertEqual(len(sec.properties), 1)
        self.assertIsNone(prop.parent)

        # Test set property fails
        with self.assertRaises(ValueError):
            sec.properties[0] = Document()
        with self.assertRaises(ValueError):
            sec.properties[0] = newsec
        with self.assertRaises(ValueError):
            sec.properties[0] = "prop"

    def test_id(self):
        s = Section(name="S")
        self.assertIsNotNone(s.id)

        s = Section("S", oid="79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertEqual(s.id, "79b613eb-a256-46bf-84f6-207df465b8f7")

        s = Section("S", oid="id")
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

        # Test fail on Section list or tuple append
        with self.assertRaises(ValueError):
            main.append([Section(name="sec2"), Section(name="sec3")])
        with self.assertRaises(ValueError):
            main.append((Section(name="sec2"), Section(name="sec3")))
        self.assertEqual(len(main.sections), 1)

        # Test append Property
        prop = Property(name="prop")
        main.append(prop)
        self.assertEqual(len(main.properties), 1)
        self.assertEqual(prop.parent, main)

        # Test fail on Property list or tuple append
        with self.assertRaises(ValueError):
            main.append([Property(name="prop2"), Property(name="prop3")])
        with self.assertRaises(ValueError):
            main.append((Property(name="prop2"), Property(name="prop3")))
        self.assertEqual(len(main.properties), 1)

        # Test fail on unsupported value
        with self.assertRaises(ValueError):
            main.append(Document())
        with self.assertRaises(ValueError):
            main.append("Section")

        # Test fail on same name entities
        with self.assertRaises(KeyError):
            main.append(Section(name="sec1"))
        self.assertEqual(len(main.sections), 1)

        with self.assertRaises(KeyError):
            main.append(Property(name="prop"))
        self.assertEqual(len(main.properties), 1)

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

    def test_insert(self):
        sec = Section(name="root")

        _ = Section(name="subsec_one", parent=sec)
        _ = Section(name="subsec_two", parent=sec)
        subsec = Section(name="subsec_three")

        self.assertNotEqual(sec.sections[1].name, subsec.name)
        sec.insert(1, subsec)
        self.assertEqual(len(sec.sections), 3)
        self.assertEqual(sec.sections[1].name, subsec.name)
        self.assertEqual(subsec.parent.name, sec.name)

        _ = Property(name="prop_one", parent=sec)
        _ = Property(name="prop_two", parent=sec)
        prop = Property(name="prop_three")

        self.assertNotEqual(sec.properties[1].name, prop.name)
        sec.insert(1, prop)
        self.assertEqual(len(sec.properties), 3)
        self.assertEqual(sec.properties[1].name, prop.name)
        self.assertEqual(prop.parent.name, sec.name)

        # Test invalid object
        with self.assertRaises(ValueError):
            sec.insert(1, Document())
        with self.assertRaises(ValueError):
            sec.insert(1, "some info")
        self.assertEqual(len(sec), 6)

        # Test same name entries
        with self.assertRaises(ValueError):
            sec.insert(0, subsec)
        with self.assertRaises(ValueError):
            sec.insert(0, prop)
        self.assertEqual(len(sec), 6)

    def test_contains(self):
        sec = Section(name="root")

        subsec = Section(name="subsec", type="test")
        prop = Property(name="prop")

        # Test not contains on empty child-lists.
        self.assertIsNone(sec.contains(subsec))
        self.assertIsNone(sec.contains(prop))

        # Test contains of Section and Property
        subsec.parent = sec
        simisec = Section(name="subsec", type="test")
        self.assertEqual(sec.contains(simisec).name, subsec.name)

        prop.parent = sec
        simiprop = Property(name="prop")
        self.assertEqual(sec.contains(simiprop).name, prop.name)

        # Test not contains on mismatching Section name/type and Property name
        self.assertIsNone(sec.contains(Section(name="subsec", type="typetest")))
        self.assertIsNone(sec.contains(Section(name="typesec", type="test")))
        self.assertIsNone(sec.contains(Property(name="prop_two")))

        # Test fail on non-Section/Property objects
        with self.assertRaises(ValueError):
            sec.contains(Document())

        with self.assertRaises(ValueError):
            sec.contains("some info")

    def test_merge_check(self):
        # -- Root level Section checks

        # Test empty Section check
        source = Section(name="source")
        destination = Section(name="destination")

        destination.merge_check(source, True)

        # Test definition check
        source = Section(name="source", definition="def")
        destination = Section(name="destination", definition="def")

        destination.merge_check(source, True)
        source.definition = "other def"
        with self.assertRaises(ValueError):
            destination.merge_check(source, True)

        # Test reference check
        source = Section(name="source", reference="ref")
        destination = Section(name="destination", reference="ref")

        destination.merge_check(source, True)
        source.reference = "other ref"
        with self.assertRaises(ValueError):
            destination.merge_check(source, True)

        # -- First child level Section checks
        source = Section(name="source")
        destination = Section(name="destination")

        s_sec_one = Section(name="lvl", type="one",
                            reference="ref", definition="def", parent=source)
        s_sec_two = Section(name="unrelated", type="one",
                            reference="one", definition="one", parent=source)

        d_sec_one = Section(name="lvl", type="one",
                            reference="ref", definition="def", parent=destination)
        d_sec_two = Section(name="unrelated", type="two",
                            reference="two", definition="two", parent=destination)

        # Test Section child level definition check
        destination.merge_check(source, True)
        s_sec_one.definition = "other def"
        with self.assertRaises(ValueError):
            destination.merge_check(source, True)

        # Test Section child level reference check
        s_sec_one.definition = "def"
        s_sec_one.reference = "other ref"
        with self.assertRaises(ValueError):
            destination.merge_check(source, True)

        # -- Second child level Section checks
        source = Section(name="source")
        destination = Section(name="destination")

        s_sec_one = Section(name="lvl", type="one",
                            reference="ref", definition="def", parent=source)
        s_subsec_one = Section(name="lvl", type="two",
                               reference="ref2", definition="def2", parent=s_sec_one)
        s_sec_two = Section(name="unrelated", type="one",
                            reference="one", definition="one", parent=source)
        s_subsec_two = Section(name="lvl", type="two",
                               reference="none1", definition="none1", parent=s_sec_two)

        d_sec_one = Section(name="lvl", type="one",
                            reference="ref", definition="def", parent=destination)
        d_subsec_one = Section(name="lvl", type="two",
                               reference="ref2", definition="def2", parent=d_sec_one)
        d_sec_two = Section(name="unrelated", type="two",
                            reference="two", definition="two", parent=destination)
        d_subsec_two = Section(name="lvl", type="two",
                               reference="none2", definition="none2", parent=d_sec_two)

        # Test Section 2nd child level definition check
        # Check no definition/reference ValueError between s_subsec_two and d_subsec_one
        # since their parents will not be merged.
        destination.merge_check(source, True)

        # Raise a definition ValueError between s_subsec_one and d_subsec_one
        # since their parents will be merged.
        s_subsec_one.definition = "other def"
        with self.assertRaises(ValueError):
            destination.merge_check(source, True)

        # Test Section 2nd child level reference check
        s_subsec_one.definition = "def2"

        # Raise a reference ValueError between s_subsec_one and d_subsec_one
        # since their parents will be merged.
        s_subsec_one.reference = "other ref"
        with self.assertRaises(ValueError):
            destination.merge_check(source, True)

        # -- Root level Property checks
        # All Property checks will only test unit failure in the Section merge context.
        # Other failures are covered by the specific Property merge check tests.
        source = Section(name="source")
        destination = Section(name="destination")

        s_prop = Property(name="prop", parent=source)
        d_prop = Property(name="prop", parent=destination)

        destination.merge_check(source, True)
        s_prop.unit = "Hz"
        d_prop.unit = "s"
        with self.assertRaises(ValueError):
            destination.merge_check(source, True)

        # -- First child level Property checks
        source = Section(name="source")
        destination = Section(name="destination")

        s_prop_one = Property(name="lvl one", unit="Hz", parent=source)
        s_prop_two = Property(name="unrelated one", unit="one", parent=source)

        d_prop_one = Property(name="lvl one", unit="Hz", parent=destination)
        d_prop_two = Property(name="unrelated two", unit="two", parent=destination)

        # Test Property child level check
        destination.merge_check(source, True)

        # Test raise ValueError between s_prop_one and d_prop_one
        s_prop_one.unit = "other unit"
        with self.assertRaises(ValueError):
            destination.merge_check(source, True)

        # -- Second child level Property checks
        source = Section(name="source")
        destination = Section(name="destination")

        s_sec_one = Section(name="lvl", type="one", parent=source)
        s_subprop_one = Property(name="lvl one", unit="Hz", parent=s_sec_one)

        s_sec_two = Section(name="unrelated", type="one", parent=source)
        s_subprop_two = Property(name="unrelated one", unit="one", parent=s_sec_two)

        d_sec_one = Section(name="lvl", type="one", parent=destination)
        d_subprop_one = Property(name="lvl one", unit="Hz", parent=d_sec_one)

        d_sec_two = Section(name="unrelated", type="two", parent=destination)
        d_subprop_two = Property(name="unrelated one", unit="two", parent=d_sec_two)

        # Test Property 2nd child level definition check
        # Check no unit ValueError between s_subprop_two and d_subprop_one
        # since their parents will not be merged.
        destination.merge_check(source, True)

        # Raise a unit ValueError between s_subprop_one and d_subprop_one
        # since their parents will be merged.
        s_subprop_one.unit = "other unit"
        with self.assertRaises(ValueError):
            destination.merge_check(source, True)

    def test_merge(self):
        # -- Root level Section merge tests
        source = Section(name="source", definition="def", reference="ref")
        destination = Section(name="destination")

        destination.merge(source)
        self.assertEqual(destination.definition, source.definition)
        self.assertEqual(destination.reference, source.reference)

        # -- First child level Section merge tests
        s_sec_one = Section(name="lvl", type="one", definition="def", parent=source)
        s_sec_two = Section(name="other", type="one", parent=source)
        d_sec_one = Section(name="lvl", type="one", parent=destination)

        self.assertEqual(len(destination), 1)
        self.assertIsNone(destination.sections["lvl"].definition)
        self.assertIsNone(destination.sections["lvl"].reference)

        destination.merge(source)
        self.assertEqual(len(destination), 2)
        self.assertEqual(destination.sections["lvl"].definition, s_sec_one.definition)
        self.assertEqual(destination.sections["lvl"].reference, s_sec_one.reference)
        self.assertEqual(destination.sections["other"], s_sec_two)

        # -- Root level Property merge tests
        source = Section(name="source")
        destination = Section(name="destination")

        s_prop_one = Property(name="prop_one", unit="Hz", parent=source)
        s_prop_two = Property(name="prop_two", parent=source)
        d_prop_one = Property(name="prop_one", parent=destination)

        self.assertEqual(len(destination.properties), 1)
        self.assertIsNone(destination.properties["prop_one"].unit)

        destination.merge(source)
        self.assertEqual(len(destination.properties), 2)
        self.assertEqual(destination.properties["prop_one"].unit, s_prop_one.unit)
        self.assertEqual(destination.properties["prop_two"], s_prop_two)

        # -- First child level Property merge tests
        source = Section(name="source")
        destination = Section(name="destination")

        s_sec_one = Section(name="lvl", type="one", definition="def", parent=source)
        s_prop_one = Property(name="prop_one", unit="Hz", parent=s_sec_one)
        s_prop_two = Property(name="prop_two", parent=s_sec_one)

        d_sec_one = Section(name="lvl", type="one", parent=destination)
        d_prop_one = Property(name="prop_one", parent=d_sec_one)

        self.assertEqual(len(destination.properties), 0)
        self.assertEqual(len(destination.sections["lvl"].properties), 1)
        self.assertIsNone(destination.sections["lvl"].properties["prop_one"].unit)

        destination.merge(source)
        self.assertEqual(len(destination.properties), 0)
        self.assertEqual(len(destination.sections["lvl"].properties), 2)
        self.assertEqual(destination.sections["lvl"].properties["prop_one"].unit,
                         s_prop_one.unit)
        self.assertEqual(destination.sections["lvl"].properties["prop_two"],
                         s_prop_two)

        # -- Test nothing merged on second child level ValueError
        source = Section(name="source", definition="def", reference="ref")
        destination = Section(name="destination")

        s_sec_one = Section(name="lvl", type="one", definition="def", parent=source)
        s_sec_two = Section(name="other", type="one", parent=source)
        d_sec_one = Section(name="lvl", type="one", parent=destination)

        s_subprop_one = Property(name="prop", value=[1, 2, 3], parent=s_sec_one)
        d_subprop_one = Property(name="prop", value=["four", "five"], parent=d_sec_one)

        self.assertEqual(len(destination.sections), 1)
        self.assertEqual(len(destination.sections["lvl"].properties), 1)
        self.assertIsNone(destination.definition)
        self.assertIsNone(destination.sections["lvl"].definition)
        self.assertEqual(destination.sections["lvl"].properties[0].value,
                         d_subprop_one.value)

        with self.assertRaises(ValueError):
            destination.merge(source)

        self.assertEqual(len(destination.sections), 1)
        self.assertEqual(len(destination.sections["lvl"].properties), 1)
        self.assertIsNone(destination.definition)
        self.assertIsNone(destination.sections["lvl"].definition)
        self.assertEqual(destination.sections["lvl"].properties[0].value,
                         d_subprop_one.value)

    def test_link(self):
        pass

    def test_include(self):
        pass

    def test_repository(self):
        pass

    def test_unmerge(self):
        pass
