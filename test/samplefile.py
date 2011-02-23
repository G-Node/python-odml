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

class AttributeTest(unittest.TestCase):
    def test_value_int(self):
        v = odml.Value(value="1", dtype="int")
        self.assertEqual(v.data, 1)
    def test_conversion_int_to_float(self):
        v = odml.Value(value="1", dtype="int")
        v.dtype = "float" #change dtype
        self.assertEqual(v.dtype, "float")
        self.assertEqual(v.data, 1.0)
        self.assertEqual(v.value, "1.0")
    def test_conversion_float_to_int(self):
        v = odml.Value(value="1.5", dtype="float")
        v.dtype = "int"
        self.assertEqual(v.dtype, "int")
        self.assertEqual(v.data, 1)
    def test_value_float(self):
        v = odml.Value(value="1.5", dtype="float")
        self.assertEqual(v.data, 1.5)
        
if __name__ == '__main__':
    unittest.main()

