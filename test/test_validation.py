import os
import sys
import unittest

import odml
import odml.validation
import odml.terminology
from . import test_samplefile as samplefile
from .util import TEST_RESOURCES_DIR as RES_DIR

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

Validate = odml.validation.Validation


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()

    @staticmethod
    def filter_repository_errors(errors):
        find_msg = "A section should have an associated repository"
        return filter(lambda x: find_msg not in x.msg, errors)

    def assertError(self, res, err, filter_rep=True):
        """
        Passes only if err appears in res.errors
        """
        errs = res.errors
        if filter_rep:
            errs = self.filter_repository_errors(errs)
        for i in errs:
            if err in i.msg:
                return
        self.assertEqual(errs, err)

    def test_property_values_cardinality(self):
        doc = odml.Document()
        sec = odml.Section(name="sec", type="sec_type", parent=doc)

        # Test no caught warning on empty cardinality
        prop = odml.Property(name="prop_empty_cardinality", values=[1, 2, 3, 4], parent=sec)
        # Check that the current property is not in the list of validation warnings or errors
        for err in Validate(doc).errors:
            self.assertNotEqual(err.obj.id, prop.id)

        # Test no warning on valid cardinality
        prop = odml.Property(name="prop_valid_cardinality", values=[1, 2, 3, 4],
                             val_cardinality=(2, 10), parent=sec)
        for err in Validate(doc).errors:
            self.assertNotEqual(err.obj.id, prop.id)

        # Test maximum value cardinality validation
        test_val = [1, 2, 3]
        test_card = 2

        prop = odml.Property(name="prop_invalid_max_val", values=test_val,
                             val_cardinality=test_card, parent=sec)

        test_msg_base = "Property values cardinality violated"
        test_msg = "%s (maximum %s values, %s found)" % (test_msg_base, test_card, len(prop.values))
        for err in Validate(doc).errors:
            if err.obj.id == prop.id:
                self.assertFalse(err.is_error)
                self.assertIn(test_msg, err.msg)

        # Test minimum value cardinality validation
        test_val = "I am a nice text to test"
        test_card = (4, None)

        prop = odml.Property(name="prop_invalid_min_val", values=test_val,
                             val_cardinality=test_card, parent=sec)

        test_msg = "%s (minimum %s values, %s found)" % (test_msg_base, test_card[0],
                                                         len(prop.values))
        for err in Validate(doc).errors:
            if err.obj.id == prop.id:
                self.assertFalse(err.is_error)
                self.assertIn(test_msg, err.msg)

    def test_section_properties_cardinality(self):
        msg_base = "Section properties cardinality violated"

        doc = odml.Document()
        # Test no caught warning on empty cardinality
        sec = odml.Section(name="prop_empty_cardinality", type="test", parent=doc)
        # Check that the current section did not throw any properties cardinality warnings
        for err in Validate(doc).errors:
            if err.obj.id == sec.id:
                self.assertNotIn(msg_base, err.msg)

        # Test no warning on valid cardinality
        sec = odml.Section(name="prop_valid_cardinality", prop_cardinality=(1, 2), parent=doc)
        _ = odml.Property(parent=sec)
        for err in Validate(doc).errors:
            if err.obj.id == sec.id:
                self.assertNotIn(msg_base, err.msg)

        # Test maximum value cardinality validation
        test_range = 3
        test_card = 2
        sec = odml.Section(name="prop_invalid_max_val", prop_cardinality=test_card, parent=doc)
        for _ in range(test_range):
            _ = odml.Property(parent=sec)

        test_msg = "%s (maximum %s values, %s found)" % (msg_base, test_card, len(sec.properties))

        # Once ValidationErrors provide validation ids, the following can be simplified.
        found = False
        for err in Validate(doc).errors:
            if err.obj.id == sec.id and msg_base in err.msg:
                self.assertFalse(err.is_error)
                self.assertIn(test_msg, err.msg)
                found = True

        self.assertTrue(found)

        # Test minimum value cardinality validation
        test_card = (4, None)

        sec = odml.Section(name="prop_invalid_min_val", prop_cardinality=test_card, parent=sec)
        _ = odml.Property(parent=sec)

        test_msg = "%s (minimum %s values, %s found)" % (msg_base, test_card[0],
                                                         len(sec.properties))

        # Once ValidationErrors provide validation ids, the following can be simplified.
        found = False
        for err in Validate(doc).errors:
            if err.obj.id == sec.id and msg_base in err.msg:
                self.assertFalse(err.is_error)
                self.assertIn(test_msg, err.msg)
                found = True

        self.assertTrue(found)

    def test_section_sections_cardinality(self):
        msg_base = "Section sections cardinality violated"

        doc = odml.Document()
        # Test no caught warning on empty cardinality
        sec = odml.Section(name="sec_empty_cardinality", type="test", parent=doc)
        # Check that the current section did not throw any sections cardinality warnings
        for err in Validate(doc).errors:
            if err.obj.id == sec.id:
                self.assertNotIn(msg_base, err.msg)

        # Test no warning on valid cardinality
        sec = odml.Section(name="sec_valid_cardinality", sec_cardinality=(1, 2), parent=doc)
        _ = odml.Section(name="sub_sec_valid_cardinality", type="test", parent=sec)
        for err in Validate(doc).errors:
            if err.obj.id == sec.id:
                self.assertNotIn(msg_base, err.msg)

        # Test maximum value cardinality validation
        test_range = 3
        test_card = 2
        sec = odml.Section(name="sec_invalid_max_val", sec_cardinality=test_card, parent=doc)
        for i in range(test_range):
            sec_name = "sub_sec_invalid_max_val_%s" % i
            _ = odml.Section(name=sec_name, type="test", parent=sec)

        test_msg = "%s (maximum %s values, %s found)" % (msg_base, test_card, len(sec.sections))

        # Once ValidationErrors provide validation ids, the following can be simplified.
        found = False
        for err in Validate(doc).errors:
            if err.obj.id == sec.id and msg_base in err.msg:
                self.assertFalse(err.is_error)
                self.assertIn(test_msg, err.msg)
                found = True

        self.assertTrue(found)

        # Test minimum value cardinality validation
        test_card = (4, None)

        sec = odml.Section(name="sec_invalid_min_val", sec_cardinality=test_card, parent=sec)
        _ = odml.Section(name="sub_sec_invalid_min_val", type="test", parent=sec)

        test_msg = "%s (minimum %s values, %s found)" % (msg_base, test_card[0],
                                                         len(sec.sections))

        # Once ValidationErrors provide validation ids, the following can be simplified.
        found = False
        for err in Validate(doc).errors:
            if err.obj.id == sec.id and msg_base in err.msg:
                self.assertFalse(err.is_error)
                self.assertIn(test_msg, err.msg)
                found = True

        self.assertTrue(found)

    def test_uniques(self):
        self.assertRaises(KeyError, samplefile.parse, """
            s1[t1]
            s1[t1]
            """)

        self.assertRaises(KeyError, samplefile.parse, """
            s1[t1]
            - p1
            - p1
            """)

    def test_property_in_terminology(self):
        odml.validation.Validation.register_handler("property",
                                                    odml.validation.property_terminology_check)

        doc = samplefile.parse("""
            s1[t1]
            - P1
            """)
        odml.terminology.terminologies['term'] = samplefile.parse("""
            S1[T1]
            - P1
            """)
        doc.repository = 'term'
        res = Validate(doc)
        self.assertEqual(res.errors, [])

        doc = samplefile.parse("""
            s1[t1]
            - p1
            - P1
            """)
        doc.repository = 'term'
        res = Validate(doc)
        self.assertError(res, "Property 'p1' not found in terminology")

    def test_property_values(self):
        # different units
        doc = samplefile.parse("""s1[t1]""")
        prop = odml.Property(name="p1", value=[0, 1])
        doc["s1"].append(prop)

        # missing dependency
        prop.dependency = "p2"
        res = Validate(doc)
        self.assertError(res, "non-existent dependency object")

    def test_property_unique_ids(self):
        """
        Test if identical ids in properties raise a validation error
        """
        doc = odml.Document()
        sec_one = odml.Section("sec1", parent=doc)
        sec_two = odml.Section("sec2", parent=doc)
        prop = odml.Property("prop", parent=sec_one)

        cprop = prop.clone(keep_id=True)
        sec_two.append(cprop)

        res = Validate(doc)
        self.assertError(res, "Duplicate id in Property")

    def test_section_unique_ids(self):
        """
        Test if identical ids in sections raise a validation error.
        """
        doc = odml.Document()
        sec = odml.Section("sec", parent=doc)

        csec = sec.clone(keep_id=True)
        sec.append(csec)

        res = Validate(doc)
        self.assertError(res, "Duplicate id in Section")

    def test_section_name_readable(self):
        """
        Test if section name is not uuid and thus more readable.
        """
        doc = odml.Document()
        sec = odml.Section("sec", parent=doc)
        sec.name = sec.id
        res = Validate(doc)
        self.assertError(res, "Name not assigned")

    def test_property_name_readable(self):
        """
        Test if property name is not uuid and thus more readable.
        """
        doc = odml.Document()
        sec = odml.Section("sec", parent=doc)
        prop = odml.Property("prop", parent=sec)
        prop.name = prop.id
        res = Validate(doc)
        self.assertError(res, "Name not assigned")

    def test_standalone_section(self):
        """
        Test if standalone section does not return errors if required attributes are correct.
        If type is not specified, check error message.
        """

        sec_one = odml.Section("sec1")
        res = Validate(sec_one)
        self.assertError(res, "Section type not specified")

    def test_standalone_property(self):
        """
        Test if standalone property does not return errors if required attributes are correct.
        """

        prop = odml.Property()
        prop.type = ""

        errs = list(filter(lambda x: x.is_error, Validate(prop).errors))
        self.assertEqual(len(errs), 0)

    def test_section_init(self):
        """
        Test validation errors printed to stdout on section init.
        """
        check_msg = "Missing required attribute 'type'"

        val_errs = StringIO()
        old_stdout = sys.stdout
        sys.stdout = val_errs
        odml.Section(name="sec", type=None)
        sys.stdout = old_stdout

        self.assertIn(check_msg, val_errs.getvalue())

    def test_prop_string_values(self):
        """
        Test if property values set as dtype string but could be of different dtype
        raise validation warning.
        """

        val = ['-13', '101', '-11', 'hello']
        prop0 = odml.Property(name='words', dtype="string", values=val)
        self.assertEqual(len(Validate(prop0).errors), 0)

        msg_base = 'Dtype of property "%s" currently is "string", but might fit dtype "%s"!'

        val = ['-13', '101', '-11', '0', '-8']
        prop1 = odml.Property(name='members', dtype="string", values=val)
        self.assertError(Validate(prop1), msg_base % ("members", "int"))

        val = ['-4.8', '10.0', '-11.9', '-10.0', '18.0']
        prop2 = odml.Property(name='potential', dtype="string", values=val)
        self.assertError(Validate(prop2), msg_base % ("potential", "float"))

        val = ['1997-12-14', '00-12-14', '89-07-04']
        prop3 = odml.Property(name='dates', dtype="string", values=val)
        self.assertError(Validate(prop3), msg_base % ("dates", "date"))

        val = ['97-12-14 11:11:11', '97-12-14 12:12', '1997-12-14 03:03']
        prop4 = odml.Property(name='datetimes', dtype="string", values=val)
        self.assertError(Validate(prop4), msg_base % ("datetimes", "datetime"))

        val = ['11:11:11', '12:12:12', '03:03:03']
        prop5 = odml.Property(name='times', dtype="string", values=val)
        self.assertError(Validate(prop5), msg_base % ("times", "time"))

        val = ['False', True, 'TRUE', False, 't']
        prop6 = odml.Property(name='sent', dtype="string", values=val)
        self.assertError(Validate(prop6), msg_base % ("sent", "boolean"))

        val = ['line1\n line2', 'line3\n line4', '\nline5\nline6']
        prop7 = odml.Property(name='texts', dtype="string", values=val)
        self.assertError(Validate(prop7), msg_base % ("texts", "text"))

        val = ['(39.12; 67.19)', '(39.12; 67.19)', '(39.12; 67.18)']
        prop8 = odml.Property(name="Location", dtype='string', values=val)
        self.assertError(Validate(prop8), msg_base % ("Location", "2-tuple"))

        val = ['(39.12; 89; 67.19)', '(39.12; 78; 67.19)', '(39.12; 56; 67.18)']
        prop9 = odml.Property(name="Coos", dtype='string', values=val)
        self.assertError(Validate(prop9), msg_base % ("Coos", "3-tuple"))

    def load_section_validation(self, doc):
        filter_func = lambda x: x.msg == filter_msg and x.obj.name == filter_name

        # Check error for deliberate empty section type
        filter_msg = "Missing required attribute 'type'"
        filter_name = "sec_type_empty"
        self.assertGreater(len(list(filter(filter_func, Validate(doc).errors))), 0)

        # Check warning for not specified section type
        filter_msg = "Section type not specified"
        filter_name = "sec_type_undefined"
        self.assertGreater(len(list(filter(filter_func, Validate(doc).errors))), 0)

    def test_load_section_xml(self):
        """
        Test if loading xml document raises validation errors for Sections with undefined type.
        """

        path = os.path.join(RES_DIR, "validation_section.xml")
        doc = odml.load(path)

        self.load_section_validation(doc)

    def test_load_section_json(self):
        """
        Test if loading json document raises validation errors for Sections with undefined type.
        """

        path = os.path.join(RES_DIR, "validation_section.json")
        doc = odml.load(path, "JSON")

        self.load_section_validation(doc)

    def test_load_section_yaml(self):
        """
        Test if loading yaml document raises validation errors for Sections with undefined type.
        """

        path = os.path.join(RES_DIR, "validation_section.yaml")
        doc = odml.load(path, "YAML")

        self.load_section_validation(doc)

    def load_dtypes_validation(self, doc):
        msg_base = 'Dtype of property "%s" currently is "string", but might fit dtype "%s"!'

        doc_val = Validate(doc)
        self.assertError(doc_val, msg_base % ("members_no", "int"))
        self.assertError(doc_val, msg_base % ("potential_no", "float"))
        self.assertError(doc_val, msg_base % ("dates_no", "date"))
        self.assertError(doc_val, msg_base % ("datetimes_no", "datetime"))
        self.assertError(doc_val, msg_base % ("times_no", "time"))
        self.assertError(doc_val, msg_base % ("sent_no", "boolean"))
        self.assertError(doc_val, msg_base % ("Location_no", "2-tuple"))
        self.assertError(doc_val, msg_base % ("Coos_no", "3-tuple"))

        self.assertError(doc_val, msg_base % ("members_mislabelled", "int"))
        self.assertError(doc_val, msg_base % ("potential_mislabelled", "float"))
        self.assertError(doc_val, msg_base % ("dates_mislabelled", "date"))
        self.assertError(doc_val, msg_base % ("datetimes_mislabelled", "datetime"))
        self.assertError(doc_val, msg_base % ("times_mislabelled", "time"))
        self.assertError(doc_val, msg_base % ("sent_mislabelled", "boolean"))
        self.assertError(doc_val, msg_base % ("texts_mislabelled", "text"))
        self.assertError(doc_val, msg_base % ("Location_mislabelled", "2-tuple"))
        self.assertError(doc_val, msg_base % ("Coos_mislabelled", "3-tuple"))

    def test_load_dtypes_xml(self):
        """
        Test if loading xml document raises validation errors
        for Properties with undefined dtypes.
        """

        path = os.path.join(RES_DIR, "validation_dtypes.xml")
        doc = odml.load(path)
        self.load_dtypes_validation(doc)

    def test_load_dtypes_json(self):
        """
        Test if loading json document raises validation errors
        for Properties with undefined dtypes.
        """

        path = os.path.join(RES_DIR, "validation_dtypes.json")
        doc = odml.load(path, "JSON")
        self.load_dtypes_validation(doc)

    def test_load_dtypes_yaml(self):
        """
        Test if loading yaml document raises validation errors
        for Properties with undefined dtypes.
        """

        path = os.path.join(RES_DIR, "validation_dtypes.yaml")
        doc = odml.load(path, "YAML")
        self.load_dtypes_validation(doc)

    def test_section_in_terminology(self):
        """
        Test optional section in terminology validation.
        """
        doc = samplefile.parse("""s1[T1]""")

        # Set up custom validation and add section_repository_present handler
        res = odml.validation.Validation(doc, validate=False, reset=True)
        handler = odml.validation.section_repository_present
        res.register_custom_handler('section', handler)

        res.run_validation()
        self.assertError(res, "A section should have an associated repository",
                         filter_rep=False)

        odml.terminology.terminologies['map'] = samplefile.parse("""
        s0[t0]
        - S1[T1]
        """)
        doc.sections[0].repository = 'map'
        res = Validate(doc)
        # self.assertEqual(list(self.filter_mapping_errors(res.errors)), [])
        self.assertEqual(res.errors, [])
