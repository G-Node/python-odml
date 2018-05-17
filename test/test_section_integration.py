"""
This file tests proper creation, saving and loading
of odML Sections with all supported odML parsers.
"""

import os
import shutil
import tempfile
import unittest

import odml


class TestSectionIntegration(unittest.TestCase):

    def setUp(self):
        # Set up test environment
        self.tmp_dir = tempfile.mkdtemp(suffix=".odml")

        self.json_file = os.path.join(self.tmp_dir, "test.json")
        self.xml_file = os.path.join(self.tmp_dir, "test.xml")
        self.yaml_file = os.path.join(self.tmp_dir, "test.yaml")

        # Set up odML document stub
        doc = odml.Document()
        self.doc = doc

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def save_load(self):
        """
        Helper method to save and load the current state of the document
        with all supported parsers.
        :return: jdoc ... document loaded from JSON file
                 xdoc ... document loaded from XML file
                 ydoc ... document loaded from YAML file
        """
        odml.save(self.doc, self.json_file, "JSON")
        jdoc = odml.load(self.json_file, "JSON")

        odml.save(self.doc, self.xml_file)
        xdoc = odml.load(self.xml_file)

        odml.save(self.doc, self.yaml_file, "YAML")
        ydoc = odml.load(self.yaml_file, "YAML")

        return jdoc, xdoc, ydoc

    def test_id(self):
        # Test correct save and load of generated id.
        sec_name = "empty_id"
        sec = odml.Section(name=sec_name, parent=self.doc)

        jdoc, xdoc, ydoc = self.save_load()

        self.assertEqual(jdoc.sections[sec_name].oid, sec.oid)
        self.assertEqual(xdoc.sections[sec_name].oid, sec.oid)
        self.assertEqual(ydoc.sections[sec_name].oid, sec.oid)

        # Test correct save and load of assigned id.
        sec_name = "assigned_id"
        assigned_id = "79b613eb-a256-46bf-84f6-207df465b8f7"
        _ = odml.Section(name=sec_name, oid=assigned_id, parent=self.doc)

        jdoc, xdoc, ydoc = self.save_load()

        self.assertEqual(jdoc.sections[sec_name].oid, assigned_id)
        self.assertEqual(xdoc.sections[sec_name].oid, assigned_id)
        self.assertEqual(ydoc.sections[sec_name].oid, assigned_id)

    def test_simple_attributes(self):
        """
        This test checks correct writing and loading of 'simple'
        Section format attributes meaning all attributes that
        do not require any special handling when they are set.
        """
        s_name = "section"
        s_type = "mellow"
        s_repo = "unresolvable"
        s_ref = "4 8 15 16 23 42"
        s_def = "undefined"

        _ = odml.Section(name=s_name, type=s_type, repository=s_repo,
                         reference=s_ref, definition=s_def, parent=self.doc)

        jdoc, xdoc, ydoc = self.save_load()

        # Test correct JSON save and load.
        jsec = jdoc.sections[s_name]
        self.assertEqual(jsec.name, s_name)
        self.assertEqual(jsec.type, s_type)
        self.assertEqual(jsec.repository, s_repo)
        self.assertEqual(jsec.reference, s_ref)
        self.assertEqual(jsec.definition, s_def)

        # Test correct XML save and load.
        xsec = xdoc.sections[s_name]
        self.assertEqual(xsec.name, s_name)
        self.assertEqual(xsec.type, s_type)
        self.assertEqual(xsec.repository, s_repo)
        self.assertEqual(xsec.reference, s_ref)
        self.assertEqual(xsec.definition, s_def)

        # Test correct YAML save and load.
        ysec = ydoc.sections[s_name]
        self.assertEqual(ysec.name, s_name)
        self.assertEqual(ysec.type, s_type)
        self.assertEqual(ysec.repository, s_repo)
        self.assertEqual(ysec.reference, s_ref)
        self.assertEqual(ysec.definition, s_def)

    def test_children(self):
        """
        This test checks correct writing and loading of Section and Property
        children of a Section.
        """
        root = odml.Section(name="root", parent=self.doc)

        # Lvl 1 child Sections
        sec_lvl_11 = odml.Section(name="sec_11", parent=root)
        _ = odml.Section(name="sec_12", parent=root)

        # Lvl 1 child Properties
        _ = odml.Property(name="prop_11", parent=root)
        _ = odml.Property(name="prop_12", parent=root)

        # Lvl 2 child Sections
        sec_lvl_21 = odml.Section(name="sec_21", parent=sec_lvl_11)
        _ = odml.Section(name="sec_22", parent=sec_lvl_11)
        _ = odml.Section(name="sec_23", parent=sec_lvl_11)

        # Lvl 2 child Properties
        _ = odml.Property(name="prop_21", parent=sec_lvl_11)
        _ = odml.Property(name="prop_22", parent=sec_lvl_11)
        _ = odml.Property(name="prop_23", parent=sec_lvl_11)

        # Lvl 3 child Sections
        _ = odml.Section(name="sec_31", parent=sec_lvl_21)
        _ = odml.Section(name="sec_32", parent=sec_lvl_21)
        _ = odml.Section(name="sec_33", parent=sec_lvl_21)
        _ = odml.Section(name="sec_34", parent=sec_lvl_21)

        # Lvl 3 child Properties
        _ = odml.Property(name="prop_31", parent=sec_lvl_21)
        _ = odml.Property(name="prop_32", parent=sec_lvl_21)
        _ = odml.Property(name="prop_33", parent=sec_lvl_21)
        _ = odml.Property(name="prop_34", parent=sec_lvl_21)

        jdoc, xdoc, ydoc = self.save_load()

        # Test correct JSON save and load.
        jsec = jdoc.sections[root.name]
        self.assertEqual(len(jsec.sections), 2)
        self.assertEqual(len(jsec.properties), 2)

        jsec_lvl_1 = jsec[sec_lvl_11.name]
        self.assertEqual(len(jsec_lvl_1.sections), 3)
        self.assertEqual(len(jsec_lvl_1.properties), 3)

        jsec_lvl_2 = jsec_lvl_1[sec_lvl_21.name]
        self.assertEqual(len(jsec_lvl_2.sections), 4)
        self.assertEqual(len(jsec_lvl_2.properties), 4)

        # Test correct XML save and load.
        xsec = xdoc.sections[root.name]
        self.assertEqual(len(xsec.sections), 2)
        self.assertEqual(len(xsec.properties), 2)

        xsec_lvl_1 = xsec[sec_lvl_11.name]
        self.assertEqual(len(xsec_lvl_1.sections), 3)
        self.assertEqual(len(xsec_lvl_1.properties), 3)

        xsec_lvl_2 = xsec_lvl_1[sec_lvl_21.name]
        self.assertEqual(len(xsec_lvl_2.sections), 4)
        self.assertEqual(len(xsec_lvl_2.properties), 4)

        # Test correct YAML save and load.
        ysec = ydoc.sections[root.name]
        self.assertEqual(len(ysec.sections), 2)
        self.assertEqual(len(ysec.properties), 2)

        ysec_lvl_1 = ysec[sec_lvl_11.name]
        self.assertEqual(len(ysec_lvl_1.sections), 3)
        self.assertEqual(len(ysec_lvl_1.properties), 3)

        ysec_lvl_2 = ysec_lvl_1[sec_lvl_21.name]
        self.assertEqual(len(ysec_lvl_2.sections), 4)
        self.assertEqual(len(ysec_lvl_2.properties), 4)

    def test_link(self):
        pass

    def test_include(self):
        pass
