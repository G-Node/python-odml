import odml.gui.treemodel.mixin
import unittest
import samplefile

class TestTreemodel(unittest.TestCase):
    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()

    def path_property(self, prop, path):
        for i, val in enumerate(prop):
            self.assertEqual(val.to_path(), path + (i,))

    def path_section(self, sec, path):
        for i, section in enumerate(sec.sections):
            p = path + (0,i)
            self.assertEqual(section.to_path(), p)
            self.path_section(section, p)

        for i, prop in enumerate(sec.properties):
            p = path + (1,i)
            self.assertEqual(prop.to_path(), p)
            self.path_property(prop, p)

    def test_path_example(self):
        self.assertEqual(self.doc.sections[0].sections[1].properties[1].value.to_path(), (0,0,1,1,1,0))
        self.assertEqual(self.doc.sections[0].sections[1].to_path(self.doc), self.doc.sections[0].sections[1].to_path())
        self.assertEqual(self.doc.sections[0].sections[1].to_path(self.doc.sections[0]), (0,1))
        self.assertEqual(self.doc.sections[0].sections[1].properties[1].value.to_path(self.doc.sections[0].sections[1]), (1,1,0))

    def test_path_consistency(self):
        for i, section in enumerate(self.doc):
            self.path_section(section, (i,))

if __name__ == '__main__':
    unittest.main()

