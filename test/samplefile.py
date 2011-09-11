import odml
import unittest
import os
from odml.tools import xmlparser

def dump(doc, filename):
    """
    helper function to dump a duocument for debugging purposes
    """
    open(filename, "w").write(unicode(xmlparser.XMLWriter(doc)))

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
                s.append(self.create_section("%s,%d" % (name, i), depth=depth+1))

        if name.endswith("1"):
            for i in xrange(3):
                s.append(self.create_property("%s:%d" % (name, i)))

        return s

    def create_property(self, name):
        value = self.create_value(name.replace("sec", "val"))
        return odml.Property(name=name.replace("sec", "prop"), value=value)

    def create_value(self, content):
        return odml.Value(content)

class SampleFileCreatorTest(unittest.TestCase):
    def test_samplefile(self):
        doc = SampleFileCreator().create_document()
        for sec in doc.sections:
            xmlparser.dumpSection(sec)

class SampleFileOperationTest(unittest.TestCase):
    def setUp(self):
        doc = SampleFileCreator().create_document()
        doc.sections['sec 0'].sections['sec 0,1'].type = "test"
        self.doc = doc

    def test_find_key(self):
        self.assertEqual(self.doc.find(key="sec 1,1"), None)

        # find distant child
        sec = self.doc.find_related(key="sec 1,1")
        self.assertEqual(sec.name, "sec 1,1")

        # find sibling
        res = sec.find_related(key="sec 0,0")
        self.assertEqual(res, None)

        sec = sec.find_related(key="sec 1,0")
        self.assertEqual(sec.name, "sec 1,0")

        # find parent
        res = sec.find_related(key="sec 0")
        self.assertEqual(res, None)

        sec = sec.find_related(key="sec 1")
        self.assertEqual(sec.name, "sec 1")

        # find section by type
        self.assertEqual(self.doc.find_related(type="test").name, "sec 0,1")

    def test_save(self):
        doc = xmlparser.XMLWriter(self.doc)
        path = os.tempnam()
        doc.write_file(path)
        os.unlink(path)

    def test_restore(self):
        import StringIO
        doc = xmlparser.XMLWriter(self.doc)
        doc = StringIO.StringIO(unicode(doc))
        doc = xmlparser.parseXML(doc)
        self.assertEqual(doc, self.doc)
#        for a,b in zip(doc.sections, self.doc.sections):
#            print "sec cmp", a, b
#            self.assertEqual(a, b)
#        print "A ---------------------------------"
#        for sec in doc.sections:
#            xmlparser.dumpSection(sec)
#        print "B ---------------------------------"
#        for sec in self.doc.sections:
#            xmlparser.dumpSection(sec)
#        print "-----------------------------------"
#
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

class CopyTest(unittest.TestCase):
    def setUp(self):
        self.p = odml.Property(name="test", value=1)

    def test_dependence(self):
        a = self.p
        b = self.p
        self.assertEqual(a, b)
        a.value = odml.Value(5)
        self.assertEqual(a, b)
        self.assertEqual(a.value, b.value)

    def test_independence(self):
        a = self.p.clone()
        b = self.p.clone()
        self.assertEqual(a, b)
        a.value = odml.Value(5)
        self.assertNotEqual(a, b)

        #self.assertUn

class MiscTest(unittest.TestCase):
    def setUp(self):
        self.doc = SampleFileCreator().create_document()

    def test_paths(self):
        sec = odml.Section("bar")
        self.assertEqual(sec._get_relative_path("/a", "/b"), "/b")
        self.assertEqual(sec._get_relative_path("/a", "/a/b"), "b")
        self.assertEqual(sec._get_relative_path("/a/b", "/a/c"), "../c")
        self.assertEqual(sec._get_relative_path("/a/b/c", "/a"), "../..")
        self.assertEqual(sec._get_relative_path("/a/b", "/a"), "..")

    def test_section_path(self):
        sec1 = self.doc.sections[1]
        sec10 = sec1.sections[0]
        sec11 = sec1.sections[1]
        path = sec10.get_path()
        self.assertEqual(path, "/%s/%s" % (sec1.name, sec10.name))
        self.assertEqual(self.doc.get_path(), "/")
        self.assertEqual(sec10.get_relative_path(sec1), "..")

        path_to_sec10 = sec1.get_relative_path(sec10)
        self.assertEqual(path_to_sec10, sec10.name)
        self.assertIs(sec1.find_by_path(path_to_sec10), sec10)

        path_to_sec11 = sec10.get_relative_path(sec11)
        self.assertEqual(path_to_sec11, "../" + sec11.name)
        self.assertIs(sec10.find_by_path(path_to_sec11), sec11)


if __name__ == '__main__':
    unittest.main()

