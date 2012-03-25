import unittest
import samplefile
import odml
import odml.validation
import odml.terminology

validate = odml.validation.Validation

class TestValidation(unittest.TestCase):
    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()

    def test_errorfree(self):
        res = validate(self.doc)
        self.assertEqual(res.errors, [])
        
    def assertError(self, res, err):
        """
        passes only if err appears in res.errors
        """
        for i in res.errors:
            if err in i.msg:
                return
        self.assertEqual(res.errors, err)
        
    def test_section_type(self):
        doc = samplefile.parse("""s1[undefined]""")
        res = validate(doc)
        # the section type is undefined (also in the mapping)
        self.assertError(res, "Section type undefined")
        
    def test_unique_names(self):
        doc = samplefile.parse("""
            s1[t1]
            s1[t2]
            """)
        res = validate(doc)
        self.assertError(res, "Object names must be unique")

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

if __name__ == '__main__':
    unittest.main()
