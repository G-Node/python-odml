import unittest
import samplefile
import odml
import odml.validation
import odml.terminology
import odml.mapping

validate = odml.validation.Validation

class TestValidation(unittest.TestCase):

    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()
        self.maxDiff = None

    def filter_repository_errors(self, errors):
        return filter(lambda x: not "A section should have an associated repository" in x.msg, errors)

    def filter_mapping_errors(self, errors):
        return filter(lambda x: not x.msg.startswith("mapping:"), errors)    

    def test_errorfree(self):
        res = validate(self.doc)
        self.assertEqual(self.filter_repository_errors(res.errors), [])
        
    def assertError(self, res, err, filter_rep=True, filter_map=False):
        """
        passes only if err appears in res.errors
        """
        errs = res.errors
        if filter_rep: errs = self.filter_repository_errors(errs)
        if filter_map: errs = self.filter_mapping_errors(errs)
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
        self.assertError(res, "A section should have an associated repository", filter_rep=False)

        odml.terminology.terminologies['map'] = samplefile.parse("""
        s0[t0]
        - S1[T1]
        """)
        odml.mapping.unmap_document(doc)
        doc.sections[0].repository = 'map'
        res = validate(doc)
        # TODO: mappings don't take over the repository attribute yet
        #       thus the mapped equivalent of the document would still raise the error
        self.assertEqual(self.filter_mapping_errors(res.errors), [])
        
    def test_uniques(self):
        doc = samplefile.parse("""
            s1[t1]
            s1[t1]
            """)
        res = validate(doc)
        self.assertError(res, "name/type combination must be unique")

        doc = samplefile.parse("""
            s1[t1]
            - p1
            - p1
            """)
        res = validate(doc)
        self.assertError(res, "Object names must be unique")
        
    def test_mapping_errors(self):
        # 1. mappings don't resolve
        doc = samplefile.parse("""s1[t1] mapping [T2]""")
        odml.terminology.terminologies['map'] = samplefile.parse("S1[T1]")
        res = validate(doc)
        self.assertError(res, "No section of type 'T2' could be found")
        
        # 2. mapped property does not resolve
        doc = samplefile.parse("""
            s1[t1]
            - p1 mapping [T1:P1]
            """)
        res = validate(doc)
        self.assertError(res, "No property named 'P1' could be found in section 'S1'")
        
    def test_invalid_mapped_document(self):
        # the following mapping creates an illegal document
        # in which the property P1 is found twice in the same section
        doc = samplefile.parse("""
            s1[t1]
            - p1 mapping [T1:P1]
            - P1
            """)
        odml.terminology.terminologies['map'] = samplefile.parse("""
            S1[T1]
            - P1
            """)
        res = validate(doc)
        self.assertError(res, "mapping: Object names must be unique")
        
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
        p = odml.Property(name="p1", value=[0,1])
        doc["s1"].append(p)
        p.values[0].unit = "km"
        p.values[1].unit = "mV"
        res = validate(doc)
        self.assertError(res, "the same unit")

        del p.values[1]
        # missing dependency
        p.dependency = "p2"
        res = validate(doc)
        self.assertError(res, "non-existant dependency object")
        

if __name__ == '__main__':
    unittest.main()
