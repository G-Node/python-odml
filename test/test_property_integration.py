"""
This file tests proper creation, saving and loading
of odML Properties with all supported odML parsers.
"""

import os
import shutil
import unittest

import odml

from .util import create_test_dir


class TestPropertyIntegration(unittest.TestCase):

    def setUp(self):
        # Set up test environment
        self.tmp_dir = create_test_dir(__file__)

        self.json_file = os.path.join(self.tmp_dir, "test.json")
        self.xml_file = os.path.join(self.tmp_dir, "test.xml")
        self.yaml_file = os.path.join(self.tmp_dir, "test.yaml")

        # Set up odML document stub
        doc = odml.Document()
        _ = odml.Section(name="properties", type="test", parent=doc)
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
        prop_name = "empty_id"
        prop = odml.Property(name=prop_name, parent=self.doc.sections[0])

        jdoc, xdoc, ydoc = self.save_load()

        self.assertEqual(jdoc.sections[0].properties[prop_name].id, prop.id)
        self.assertEqual(xdoc.sections[0].properties[prop_name].id, prop.id)
        self.assertEqual(ydoc.sections[0].properties[prop_name].id, prop.id)

        # Test correct save and load of assigned id.
        prop_name = "assigned_id"
        assigned_id = "79b613eb-a256-46bf-84f6-207df465b8f7"
        _ = odml.Property(name=prop_name, oid=assigned_id,
                          parent=self.doc.sections[0])

        jdoc, xdoc, ydoc = self.save_load()

        self.assertEqual(jdoc.sections[0].properties[prop_name].id, assigned_id)
        self.assertEqual(xdoc.sections[0].properties[prop_name].id, assigned_id)
        self.assertEqual(ydoc.sections[0].properties[prop_name].id, assigned_id)

    def test_simple_attributes(self):
        """
        This test checks correct writing and loading of 'simple'
        Property format attributes meaning all attributes that
        do not require any special handling when they are set.

        Note: the xml reader and writer converts all attribute values
        to string whereas json and yaml retain other types like int or
        float identity. Since this is currently not relevant, all
        attributes are tested as string values.
        """
        p_name = "propertyName"
        p_origin = "from over there"
        p_unit = "pears"
        p_uncertainty = "+-12"
        p_ref = "4 8 15 16 23"
        p_def = "an odml test property"
        p_dep = "yes"
        p_dep_val = "42"

        _ = odml.Property(name=p_name, value_origin=p_origin, unit=p_unit,
                          uncertainty=p_uncertainty, reference=p_ref, definition=p_def,
                          dependency=p_dep, dependency_value=p_dep_val,
                          parent=self.doc.sections[0])

        jdoc, xdoc, ydoc = self.save_load()

        # Test correct JSON save and load.
        jprop = jdoc.sections[0].properties[p_name]
        self.assertEqual(jprop.name, p_name)
        self.assertEqual(jprop.value_origin, p_origin)
        self.assertEqual(jprop.unit, p_unit)
        self.assertEqual(jprop.uncertainty, p_uncertainty)
        self.assertEqual(jprop.reference, p_ref)
        self.assertEqual(jprop.definition, p_def)
        self.assertEqual(jprop.dependency, p_dep)
        self.assertEqual(jprop.dependency_value, p_dep_val)

        # Test correct XML save and load.
        xprop = xdoc.sections[0].properties[p_name]
        self.assertEqual(xprop.name, p_name)
        self.assertEqual(xprop.value_origin, p_origin)
        self.assertEqual(xprop.unit, p_unit)
        self.assertEqual(xprop.uncertainty, p_uncertainty)
        self.assertEqual(xprop.reference, p_ref)
        self.assertEqual(xprop.definition, p_def)
        self.assertEqual(xprop.dependency, p_dep)
        self.assertEqual(xprop.dependency_value, p_dep_val)

        # Test correct YAML save and load.
        yprop = ydoc.sections[0].properties[p_name]
        self.assertEqual(yprop.name, p_name)
        self.assertEqual(yprop.value_origin, p_origin)
        self.assertEqual(yprop.unit, p_unit)
        self.assertEqual(yprop.uncertainty, p_uncertainty)
        self.assertEqual(yprop.reference, p_ref)
        self.assertEqual(yprop.definition, p_def)
        self.assertEqual(yprop.dependency, p_dep)
        self.assertEqual(yprop.dependency_value, p_dep_val)

    def test_cardinality(self):
        """
        Test saving and loading of property values cardinality variants to
        and from all supported file formats.
        """
        doc = odml.Document()
        sec = odml.Section(name="sec", type="sometype", parent=doc)

        prop_empty = "prop_cardinality_empty"
        prop_max = "prop_cardinality_max"
        prop_max_card = (None, 10)
        prop_min = "prop_cardinality_min"
        prop_min_card = (2, None)
        prop_full = "prop_full"
        prop_full_card = (1, 5)

        _ = odml.Property(name=prop_empty, parent=sec)
        _ = odml.Property(name=prop_max, val_cardinality=prop_max_card, parent=sec)
        _ = odml.Property(name=prop_min, val_cardinality=prop_min_card, parent=sec)
        _ = odml.Property(name=prop_full, val_cardinality=prop_full_card, parent=sec)

        # Test saving to and loading from an XML file
        odml.save(doc, self.xml_file)
        xml_doc = odml.load(self.xml_file)
        xml_prop = xml_doc.sections["sec"].properties[prop_empty]
        self.assertIsNone(xml_prop.val_cardinality)

        xml_prop = xml_doc.sections["sec"].properties[prop_max]
        self.assertEqual(xml_prop.val_cardinality, prop_max_card)

        xml_prop = xml_doc.sections["sec"].properties[prop_min]
        self.assertEqual(xml_prop.val_cardinality, prop_min_card)

        xml_prop = xml_doc.sections["sec"].properties[prop_full]
        self.assertEqual(xml_prop.val_cardinality, prop_full_card)

        # Test saving to and loading from a JSON file
        odml.save(doc, self.json_file, "JSON")
        json_doc = odml.load(self.json_file, "JSON")

        json_prop = json_doc.sections["sec"].properties[prop_empty]
        self.assertIsNone(json_prop.val_cardinality)

        json_prop = json_doc.sections["sec"].properties[prop_max]
        self.assertEqual(json_prop.val_cardinality, prop_max_card)

        json_prop = json_doc.sections["sec"].properties[prop_min]
        self.assertEqual(json_prop.val_cardinality, prop_min_card)

        json_prop = json_doc.sections["sec"].properties[prop_full]
        self.assertEqual(json_prop.val_cardinality, prop_full_card)

        # Test saving to and loading from a YAML file
        odml.save(doc, self.yaml_file, "YAML")
        yaml_doc = odml.load(self.yaml_file, "YAML")

        yaml_prop = yaml_doc.sections["sec"].properties[prop_empty]
        self.assertIsNone(yaml_prop.val_cardinality)

        yaml_prop = yaml_doc.sections["sec"].properties[prop_max]
        self.assertEqual(yaml_prop.val_cardinality, prop_max_card)

        yaml_prop = yaml_doc.sections["sec"].properties[prop_min]
        self.assertEqual(yaml_prop.val_cardinality, prop_min_card)

        yaml_prop = yaml_doc.sections["sec"].properties[prop_full]
        self.assertEqual(yaml_prop.val_cardinality, prop_full_card)
