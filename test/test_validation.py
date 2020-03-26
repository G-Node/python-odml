import unittest
import odml
import os
import odml.validation
import odml.terminology
from . import test_samplefile as samplefile

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

        for err in validate(prop).errors:
            assert not err.is_error

    def test_prop_string_values(self):
        """
        Test if property values set as dtype string but could be of different dtype
        raise validation warning.
        """

        prop0 = odml.Property(name='words', dtype="string",
                              values=['-13', '101', '-11', 'hello'])
        assert len(validate(prop0).errors) == 0

        prop1 = odml.Property(name='members', dtype="string",
                              values=['-13', '101', '-11', '0', '-8'])
        self.assertError(validate(prop1), 'Dtype of property "members" currently is "string",'
                                          ' but might fit dtype "int"!')

        prop2 = odml.Property(name='potential', dtype="string",
                              values=['-4.8', '10.0', '-11.9', '-10.0', '18.0'])
        self.assertError(validate(prop2),'Dtype of property "potential" currently is "string", '
                                         'but might fit dtype "float"!')

        prop3 = odml.Property(name='dates', dtype="string",
                              values=['1997-12-14', '00-12-14', '89-07-04'])
        self.assertError(validate(prop3), 'Dtype of property "dates" currently is "string", '
                                          'but might fit dtype "date"!')

        prop4 = odml.Property(name='datetimes', dtype="string",
                              values=['97-12-14 11:11:11', '97-12-14 12:12', '1997-12-14 03:03'])
        self.assertError(validate(prop4), 'Dtype of property "datetimes" currently is "string", '
                                          'but might fit dtype "datetime"!')

        prop5 = odml.Property(name='times', dtype="string",
                              values=['11:11:11', '12:12:12', '03:03:03'])
        self.assertError(validate(prop5), 'Dtype of property "times" currently is "string", '
                                          'but might fit dtype "time"!')

        prop6 = odml.Property(name='sent', dtype="string",
                              values=['False', True, 'TRUE', False, 't'])
        self.assertError(validate(prop6), 'Dtype of property "sent" currently is "string", '
                                          'but might fit dtype "boolean"!')

        prop7 = odml.Property(name='texts', dtype="string",
                              values=['line1\n line2', 'line3\n line4', '\nline5\nline6'])
        self.assertError(validate(prop7), 'Dtype of property "texts" currently is "string", '
                                          'but might fit dtype "text"!')

        prop8 = odml.Property(name="Location", dtype='string',
                              values=['(39.12; 67.19)', '(39.12; 67.19)', '(39.12; 67.18)'])
        self.assertError(validate(prop8), 'Dtype of property "Location" currently is "string", '
                                          'but might fit dtype "2-tuple"!')

        prop9 = odml.Property(name="Coos", dtype='string',
                              values=['(39.12; 89; 67.19)', '(39.12; 78; 67.19)',
                                      '(39.12; 56; 67.18)'])
        self.assertError(validate(prop9), 'Dtype of property "Coos" currently is "string", '
                                          'but might fit dtype "3-tuple"!')

    def test_load_section_xml(self):
        """
        Test if loading xml document raises validation errors for Sections with undefined type.
        """

        path = os.path.join(self.dir_path, "resources", "validation_section.xml")
        doc = odml.load(path)

        sec_type_undefined_err = False
        sec_type_empty_err = False

        for err in validate(doc).errors:
            if err.msg == "Section type undefined" and err.obj.name == "sec_type_undefined":
                sec_type_undefined_err = True
            elif err.msg == "Section type undefined" and err.obj.name == "sec_type_empty":
                sec_type_empty_err = True

        assert sec_type_undefined_err
        assert sec_type_empty_err

    def test_load_dtypes_xml(self):
        """
        Test if loading xml document raises validation errors for Properties with undefined dtypes.
        """

        path = os.path.join(self.dir_path, "resources", "validation_dtypes.xml")
        doc = odml.load(path)

        self.assertError(validate(doc), 'Dtype of property "members_no" currently is "string", '
                                        'but might fit dtype "int"!')

        self.assertError(validate(doc), 'Dtype of property "potential_no" currently is "string", '
                                        'but might fit dtype "float"!')

        self.assertError(validate(doc), 'Dtype of property "dates_no" currently is "string", '
                                        'but might fit dtype "date"!')

        self.assertError(validate(doc), 'Dtype of property "datetimes_no" currently is "string", '
                                        'but might fit dtype "datetime"!')

        self.assertError(validate(doc), 'Dtype of property "times_no" currently is "string", '
                                        'but might fit dtype "time"!')

        self.assertError(validate(doc), 'Dtype of property "sent_no" currently is "string", '
                                        'but might fit dtype "boolean"!')

        self.assertError(validate(doc), 'Dtype of property "Location_no" currently is "string", '
                                        'but might fit dtype "2-tuple"!')

        self.assertError(validate(doc), 'Dtype of property "Coos_no" currently is "string", '
                                        'but might fit dtype "3-tuple"!')

        self.assertError(validate(doc), 'Dtype of property "members_mislabelled" currently is '
                                        '"string", but might fit dtype "int"!')

        self.assertError(validate(doc), 'Dtype of property "potential_mislabelled" currently is '
                                        '"string", but might fit dtype "float"!')

        self.assertError(validate(doc), 'Dtype of property "dates_mislabelled" currently is '
                                        '"string", but might fit dtype "date"!')

        self.assertError(validate(doc), 'Dtype of property "datetimes_mislabelled" currently is '
                                        '"string", but might fit dtype "datetime"!')

        self.assertError(validate(doc), 'Dtype of property "times_mislabelled" currently is '
                                        '"string", but might fit dtype "time"!')

        self.assertError(validate(doc), 'Dtype of property "sent_mislabelled" currently is '
                                        '"string", but might fit dtype "boolean"!')

        self.assertError(validate(doc), 'Dtype of property "texts_mislabelled" currently is '
                                        '"string", but might fit dtype "text"!')

        self.assertError(validate(doc), 'Dtype of property "Location_mislabelled" currently is '
                                        '"string", but might fit dtype "2-tuple"!')

        self.assertError(validate(doc), 'Dtype of property "Coos_mislabelled" currently is '
                                        '"string", but might fit dtype "3-tuple"!')

    def test_load_section_json(self):
        """
        Test if loading json document raises validation errors for Sections with undefined type.
        """

        path = os.path.join(self.dir_path, "resources", "validation_section.json")
        doc = odml.load(path, "JSON")

        sec_type_undefined_err = False
        sec_type_empty_err = False

        for err in validate(doc).errors:
            if err.msg == "Section type undefined" and err.obj.name == "sec_type_undefined":
                sec_type_undefined_err = True
            elif err.msg == "Section type undefined" and err.obj.name == "sec_type_empty":
                sec_type_empty_err = True

        assert sec_type_undefined_err
        assert sec_type_empty_err

    def test_load_dtypes_json(self):
        """
        Test if loading json document raises validation errors for Properties with undefined dtypes.
        """

        path = os.path.join(self.dir_path, "resources", "validation_dtypes.json")
        doc = odml.load(path, "JSON")

        self.assertError(validate(doc), 'Dtype of property "members_no" currently is "string", '
                                        'but might fit dtype "int"!')

        self.assertError(validate(doc), 'Dtype of property "potential_no" currently is "string", '
                                        'but might fit dtype "float"!')

        self.assertError(validate(doc), 'Dtype of property "dates_no" currently is "string", '
                                        'but might fit dtype "date"!')

        self.assertError(validate(doc), 'Dtype of property "datetimes_no" currently is "string", '
                                        'but might fit dtype "datetime"!')

        self.assertError(validate(doc), 'Dtype of property "times_no" currently is "string", '
                                        'but might fit dtype "time"!')

        self.assertError(validate(doc), 'Dtype of property "sent_no" currently is "string", '
                                        'but might fit dtype "boolean"!')

        self.assertError(validate(doc), 'Dtype of property "Location_no" currently is "string", '
                                        'but might fit dtype "2-tuple"!')

        self.assertError(validate(doc), 'Dtype of property "Coos_no" currently is "string", '
                                        'but might fit dtype "3-tuple"!')

        self.assertError(validate(doc), 'Dtype of property "members_mislabelled" currently is '
                                        '"string", but might fit dtype "int"!')

        self.assertError(validate(doc), 'Dtype of property "potential_mislabelled" currently is '
                                        '"string", but might fit dtype "float"!')

        self.assertError(validate(doc), 'Dtype of property "dates_mislabelled" currently is '
                                        '"string", but might fit dtype "date"!')

        self.assertError(validate(doc), 'Dtype of property "datetimes_mislabelled" currently is '
                                        '"string", but might fit dtype "datetime"!')

        self.assertError(validate(doc), 'Dtype of property "times_mislabelled" currently is '
                                        '"string", but might fit dtype "time"!')

        self.assertError(validate(doc), 'Dtype of property "sent_mislabelled" currently is '
                                        '"string", but might fit dtype "boolean"!')

        self.assertError(validate(doc), 'Dtype of property "texts_mislabelled" currently is '
                                        '"string", but might fit dtype "text"!')

        self.assertError(validate(doc), 'Dtype of property "Location_mislabelled" currently is '
                                        '"string", but might fit dtype "2-tuple"!')

        self.assertError(validate(doc), 'Dtype of property "Coos_mislabelled" currently is '
                                        '"string", but might fit dtype "3-tuple"!')

    def test_load_section_yaml(self):
        """
        Test if loading yaml document raises validation errors for Sections with undefined type.
        """

        path = os.path.join(self.dir_path, "resources", "validation_section.yaml")
        doc = odml.load(path, "YAML")

        sec_type_undefined_err = False
        sec_type_empty_err = False

        for err in validate(doc).errors:
            if err.msg == "Section type undefined" and err.obj.name == "sec_type_undefined":
                sec_type_undefined_err = True
            elif err.msg == "Section type undefined" and err.obj.name == "sec_type_empty":
                sec_type_empty_err = True

        assert sec_type_undefined_err
        assert sec_type_empty_err

    def test_load_dtypes_yaml(self):
        """
        Test if loading yaml document raises validation errors for Properties with undefined dtypes.
        """

        path = os.path.join(self.dir_path, "resources", "validation_dtypes.yaml")
        doc = odml.load(path, "YAML")

        self.assertError(validate(doc), 'Dtype of property "members_no" currently is "string", '
                                        'but might fit dtype "int"!')

        self.assertError(validate(doc), 'Dtype of property "potential_no" currently is "string", '
                                        'but might fit dtype "float"!')

        self.assertError(validate(doc), 'Dtype of property "dates_no" currently is "string", '
                                        'but might fit dtype "date"!')

        self.assertError(validate(doc), 'Dtype of property "datetimes_no" currently is "string", '
                                        'but might fit dtype "datetime"!')

        self.assertError(validate(doc), 'Dtype of property "times_no" currently is "string", '
                                        'but might fit dtype "time"!')

        self.assertError(validate(doc), 'Dtype of property "sent_no" currently is "string", '
                                        'but might fit dtype "boolean"!')

        self.assertError(validate(doc), 'Dtype of property "Location_no" currently is "string", '
                                        'but might fit dtype "2-tuple"!')

        self.assertError(validate(doc), 'Dtype of property "Coos_no" currently is "string", '
                                        'but might fit dtype "3-tuple"!')

        self.assertError(validate(doc), 'Dtype of property "members_mislabelled" currently is '
                                        '"string", but might fit dtype "int"!')

        self.assertError(validate(doc), 'Dtype of property "potential_mislabelled" currently is '
                                        '"string", but might fit dtype "float"!')

        self.assertError(validate(doc), 'Dtype of property "dates_mislabelled" currently is '
                                        '"string", but might fit dtype "date"!')

        self.assertError(validate(doc), 'Dtype of property "datetimes_mislabelled" currently is '
                                        '"string", but might fit dtype "datetime"!')

        self.assertError(validate(doc), 'Dtype of property "times_mislabelled" currently is '
                                        '"string", but might fit dtype "time"!')

        self.assertError(validate(doc), 'Dtype of property "sent_mislabelled" currently is '
                                        '"string", but might fit dtype "boolean"!')

        self.assertError(validate(doc), 'Dtype of property "texts_mislabelled" currently is '
                                        '"string", but might fit dtype "text"!')

        self.assertError(validate(doc), 'Dtype of property "Location_mislabelled" currently is '
                                        '"string", but might fit dtype "2-tuple"!')

        self.assertError(validate(doc), 'Dtype of property "Coos_mislabelled" currently is '
                                        '"string", but might fit dtype "3-tuple"!')
