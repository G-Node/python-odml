import odml
import unittest
from odml.tools import xmlparser

class SampleFileCreator:
    def create_document(self):
        doc = odml.Document()
        for i in xrange(3):
            doc.append(self.create_section("sec %d" % i))
        return doc
    
    def create_section(self, name, depth=0):
        s = odml.Section(name=name)
        if depth < 1:
            for i in xrange(2):
                s.append(self.create_section("%s/%d" % (name, i), depth=depth+1))
                
        if name.endswith("1"):
            for i in xrange(3):
                s.append(self.create_property("%s:%d" % (name, i)))
        
        return s
    
    def create_property(self, name):
        value = self.create_value(name)
        return odml.Property(name=name.replace("sec", "prop"), value=value)

    def create_value(self, content):
        return odml.Value(content)

class SampleFileCreatorTest(unittest.TestCase):
    def test_samplefile(self):
        doc = SampleFileCreator().create_document()
        for sec in doc.sections:
            xmlparser.dumpSection(sec)
        
if __name__ == '__main__':
    unittest.main()

