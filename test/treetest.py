from odml.tools import treemodel, xmlparser
import unittest
import samplefile

class TestTreemodel(unittest.TestCase):
    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()
        for s in self.doc: xmlparser.dumpSection(s)

    def path_property(self, prop, path):
        for i, val in enumerate(prop):
            self.assertEqual(val.to_path(), path + (i,))
        
    def path_section(self, sec, path):
        for i, section in enumerate(sec.sections):
            p = path + (i,)
            self.assertEqual(section.to_path(), p)
            self.path_section(section, p)
        
        for i, prop in enumerate(sec.properties):
            p = path + ('p%d' % i,)
            self.assertEqual(prop.to_path(), p)
            self.path_property(prop, p)
            
    def test_path_consistency(self):
        doc = self.doc
        self.assertEqual(doc.sections[0].sections[1].properties[1].value.to_path(), (0,1,'p1',0))
        for i, section in enumerate(doc):
            self.path_section(section, (i,))

if __name__ == '__main__':
    unittest.main()

