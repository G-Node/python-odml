import unittest
import odml
import odml.validation
import odml.terminology
from . import test_samplefile as samplefile

validate = odml.validation.Validation


class TestValidation(unittest.TestCase):

    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()
        self.maxDiff = None

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

    def test_standalone_section(self):
        """
        Test if standalone section is validated right.
        """

        sec_one = odml.Section("sec1")
        sec_two = odml.Section("sec2", parent=sec_one)
        prop = odml.Property("prop", parent=sec_one, values=[1, 2])

        validate(sec_one)
