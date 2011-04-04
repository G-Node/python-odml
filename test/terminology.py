import odml
import odml.terminology
import unittest
from odml.tools import xmlparser

class TerminologyTest(unittest.TestCase):
    def test_load(self):
        doc = odml.Document()
        odml.terminology.load(doc, "http://portal.g-node.org/odml/terminologies/v1.0/experiment/experiment.xml")
        self.assertEqual(doc.sections['Experiment']._parent, doc)
        return doc

    def test_merge(self):
        pass

    def test_modifications(self):
        doc = self.test_load()
        self.assertEqual(doc.sections[0].is_terminology_default(), True)
        doc.sections[0].properties[0].name = 'modified'
        self.assertEqual(doc.sections[0].is_terminology_default(), False)
        self.assertEqual(doc.sections[0].is_terminology_default(recursive=False), True)
        
if __name__ == '__main__':
    unittest.main()

