import unittest
import odml
import os
import sys
import odml.validation
import odml.terminology
from . import test_samplefile as samplefile

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

validate = odml.validation.Validation


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()
        self.maxDiff = None
        self.dir_path = os.path.dirname(os.path.realpath(__file__))

    def filter_repository_errors(self, errors):
        return filter(lambda x: "A section should have an associated "
                                "repository" not in x.msg, errors)

    def test_errorfree(self):
        res = validate(self.doc)
        self.assertEqual(list(self.filter_repository_errors(res.errors)), [])

    def assertError(self, res, err, filter_rep=True, filter_map=False):
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
        for err in validate(doc).errors:
            self.assertNotEqual(err.obj.id, prop.id)

        # Test no warning on valid cardinality
        prop = odml.Property(name="prop_valid_cardinality", values=[1, 2, 3, 4],
                             val_cardinality=(2, 10), parent=sec)
        for err in validate(doc).errors:
            self.assertNotEqual(err.obj.id, prop.id)

        # Test minimum value cardinality validation
        test_val = [1, 2, 3]
        test_card = 2

        prop = odml.Property(name="prop_invalid_max_val", values=test_val,
                             val_cardinality=test_card, parent=sec)

        test_msg_base = "Property values cardinality violated"
        test_msg = "%s (maximum %s values, %s found)" % (test_msg_base, test_card, len(prop.values))
        for err in validate(doc).errors:
            if err.obj.id == prop.id:
                self.assertFalse(err.is_error)
                self.assertIn(test_msg, err.msg)

        # Test maximum value cardinality validation
        test_val = "I am a nice text to test"
        test_card = (4, None)

        prop = odml.Property(name="prop_invalid_min_val", values=test_val,
                             val_cardinality=test_card, parent=sec)

        test_msg = "%s (minimum %s values, %s found)" % (test_msg_base, test_card[0], len(prop.values))
        for err in validate(doc).errors:
            if err.obj.id == prop.id:
                self.assertFalse(err.is_error)
                self.assertIn(test_msg, err.msg)

    def test_section_type(self):
        doc = samplefile.parse("""s1[undefined]""")
        res = validate(doc)
        # the section type is undefined (also in the mapping)
        self.assertError(res, "Section type undefined")

    def test_section_in_terminology(self):
        doc = samplefile.parse("""s1[T1]""")
        res = validate(doc)
        self.assertError(res, "A section should have an associated repository",
                         filter_rep=False)

        odml.terminology.terminologies['map'] = samplefile.parse("""
        s0[t0]
        - S1[T1]
        """)
        doc.sections[0].repository = 'map'
        res = validate(doc)
        # self.assertEqual(list(self.filter_mapping_errors(res.errors)), [])
        self.assertEqual(res.errors, [])

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
        doc = samplefile.parse("""
            s1[t1]
            - P1
            """)
        odml.terminology.terminologies['term'] = samplefile.parse("""
            S1[T1]
            - P1
            """)
        doc.repository = 'term'
        res = validate(doc)
        self.assertEqual(res.errors, [])

        doc = samplefile.parse("""
            s1[t1]
            - p1
            - P1
            """)
        doc.repository = 'term'
        res = validate(doc)
        self.assertError(res, "Property 'p1' not found in terminology")

    def test_property_values(self):
        # different units
        doc = samplefile.parse("""s1[t1]""")
        p = odml.Property(name="p1", value=[0, 1])
        doc["s1"].append(p)

        # missing dependency
        p.dependency = "p2"
        res = validate(doc)
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

        res = validate(doc)
        self.assertError(res, "Duplicate id in Property")

    def test_section_unique_ids(self):
        """
        Test if identical ids in sections raise a validation error.
        """
        doc = odml.Document()
        sec = odml.Section("sec", parent=doc)

        csec = sec.clone(keep_id=True)
        sec.append(csec)

        res = validate(doc)
        self.assertError(res, "Duplicate id in Section")

    def test_section_name_readable(self):
        """
        Test if section name is not uuid and thus more readable.
        """
        doc = odml.Document()
        sec = odml.Section("sec", parent=doc)
        sec.name = sec.id
        res = validate(doc)
        self.assertError(res, "Name should be readable")

    def test_property_name_readable(self):
        """
        Test if property name is not uuid and thus more readable.
        """
        doc = odml.Document()
        sec = odml.Section("sec", parent=doc)
        prop = odml.Property("prop", parent=sec)
        prop.name = prop.id
        res = validate(doc)
        self.assertError(res, "Name should be readable")

    def test_standalone_section(self):
        """
        Test if standalone section does not return errors if required attributes are correct.
        If type is undefined, check error message.
        """

        sec_one = odml.Section("sec1")

        res = validate(sec_one)
        self.assertError(res, "Section type undefined")

        doc = samplefile.parse("""s1[undefined]""")
        res = validate(doc)
        self.assertError(res, "Section type undefined")

    def test_standalone_property(self):
        """
        Test if standalone property does not return errors if required attributes are correct.
        """

        prop = odml.Property()
        prop.type = ""

        errs = list(filter(lambda x: x.is_error, validate(prop).errors))
        self.assertEquals(len(errs), 0)

    def test_section_init(self):
        """
        Test validation errors printed to stdout on section init.
        """
        val_errs = StringIO()

        old_stdout = sys.stdout
        sys.stdout = val_errs
        odml.Section(name="sec", type=None)
        sys.stdout = old_stdout

        self.assertIn("Section type undefined", val_errs.getvalue())

    def test_prop_string_values(self):
        """
        Test if property values set as dtype string but could be of different dtype
        raise validation warning.
        """

        prop0 = odml.Property(name='words', dtype="string",
                              values=['-13', '101', '-11', 'hello'])
        assert len(validate(prop0).errors) == 0

        msg_base = 'Dtype of property "%s" currently is "string", but might fit dtype "%s"!'

        prop1 = odml.Property(name='members', dtype="string",
                              values=['-13', '101', '-11', '0', '-8'])
        self.assertError(validate(prop1), msg_base % ("members", "int"))

        prop2 = odml.Property(name='potential', dtype="string",
                              values=['-4.8', '10.0', '-11.9', '-10.0', '18.0'])
        self.assertError(validate(prop2), msg_base % ("potential", "float"))

        prop3 = odml.Property(name='dates', dtype="string",
                              values=['1997-12-14', '00-12-14', '89-07-04'])
        self.assertError(validate(prop3), msg_base % ("dates", "date"))

        prop4 = odml.Property(name='datetimes', dtype="string",
                              values=['97-12-14 11:11:11', '97-12-14 12:12', '1997-12-14 03:03'])
        self.assertError(validate(prop4), msg_base % ("datetimes", "datetime"))

        prop5 = odml.Property(name='times', dtype="string",
                              values=['11:11:11', '12:12:12', '03:03:03'])
        self.assertError(validate(prop5), msg_base % ("times", "time"))

        prop6 = odml.Property(name='sent', dtype="string",
                              values=['False', True, 'TRUE', False, 't'])
        self.assertError(validate(prop6), msg_base % ("sent", "boolean"))

        prop7 = odml.Property(name='texts', dtype="string",
                              values=['line1\n line2', 'line3\n line4', '\nline5\nline6'])
        self.assertError(validate(prop7), msg_base % ("texts", "text"))

        prop8 = odml.Property(name="Location", dtype='string',
                              values=['(39.12; 67.19)', '(39.12; 67.19)', '(39.12; 67.18)'])
        self.assertError(validate(prop8), msg_base % ("Location", "2-tuple"))

        prop9 = odml.Property(name="Coos", dtype='string',
                              values=['(39.12; 89; 67.19)', '(39.12; 78; 67.19)',
                                      '(39.12; 56; 67.18)'])
        self.assertError(validate(prop9), msg_base % ("Coos", "3-tuple"))

    def test_load_section_xml(self):
        """
        Test if loading xml document raises validation errors for Sections with undefined type.
        """

        path = os.path.join(self.dir_path, "resources", "validation_section.xml")
        doc = odml.load(path)

        assert len(list(filter(
            lambda x: x.msg == "Section type undefined" and x.obj.name == "sec_type_undefined",
            validate(doc).errors))) > 0
        assert len(list(filter(
            lambda x: x.msg == "Section type undefined" and x.obj.name == "sec_type_empty",
            validate(doc).errors))) > 0

    def test_load_section_json(self):
        """
        Test if loading json document raises validation errors for Sections with undefined type.
        """

        path = os.path.join(self.dir_path, "resources", "validation_section.json")
        doc = odml.load(path, "JSON")

        assert len(list(filter(
            lambda x: x.msg == "Section type undefined" and x.obj.name == "sec_type_undefined",
            validate(doc).errors))) > 0
        assert len(list(filter(
            lambda x: x.msg == "Section type undefined" and x.obj.name == "sec_type_empty",
            validate(doc).errors))) > 0

    def test_load_section_yaml(self):
        """
        Test if loading yaml document raises validation errors for Sections with undefined type.
        """

        path = os.path.join(self.dir_path, "resources", "validation_section.yaml")
        doc = odml.load(path, "YAML")

        assert len(list(filter(
            lambda x: x.msg == "Section type undefined" and x.obj.name == "sec_type_undefined",
            validate(doc).errors))) > 0
        assert len(list(filter(
            lambda x: x.msg == "Section type undefined" and x.obj.name == "sec_type_empty",
            validate(doc).errors))) > 0

    def load_dtypes_validation(self, doc):
        msg_base = 'Dtype of property "%s" currently is "string", but might fit dtype "%s"!'

        doc_val = validate(doc)
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

        path = os.path.join(self.dir_path, "resources", "validation_dtypes.xml")
        doc = odml.load(path)
        self.load_dtypes_validation(doc)

    def test_load_dtypes_json(self):
        """
        Test if loading json document raises validation errors
        for Properties with undefined dtypes.
        """

        path = os.path.join(self.dir_path, "resources", "validation_dtypes.json")
        doc = odml.load(path, "JSON")
        self.load_dtypes_validation(doc)

    def test_load_dtypes_yaml(self):
        """
        Test if loading yaml document raises validation errors
        for Properties with undefined dtypes.
        """

        path = os.path.join(self.dir_path, "resources", "validation_dtypes.yaml")
        doc = odml.load(path, "YAML")
        self.load_dtypes_validation(doc)
