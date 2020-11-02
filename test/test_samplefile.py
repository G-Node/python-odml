import os
import re
import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import odml

from odml.info import FORMAT_VERSION
from odml.tools import xmlparser
from .util import create_test_dir


def dump(doc, filename):
    """
    Helper function to dump a document for debugging purposes
    """
    odml_string = str(xmlparser.XMLWriter(doc))
    open(filename, "w").write(odml_string)


def parse(data):
    """
    Parses strings to quickly create odml-documents

    e.g.:
        s1[t1] mapping [T1]
        - p1
        s2[t1]
        - s21[t2] linked to /s1/s2
    """
    lines = data.strip(" ").strip("\n").split("\n")
    offset = len(re.compile(r'(\s*)').match(lines[0]).group())
    pat = re.compile(r'(?P<name>\w+)(\[(?P<type>\w+)\])?(\s+mapping \[(?P<dst>'
                     r'[\w:]+)\])?(\s+linked to (?P<link>[\w/]+))?')

    parents = [odml.Document(), None]
    for line in lines:
        line = line[offset:]
        while len(parents) > 1:
            parp_ref = (len(parents) - 2) * 2
            if line.startswith(" " * parp_ref):
                line = line[parp_ref:]
                break
            parents.pop()

        if line.startswith('- '):
            line = line[2:]
        else:
            parents.pop()

        try:
            match_line = pat.match(line).groupdict()
        except:
            print("error parsing", repr(line))
            raise

        if match_line['type'] is None:
            obj = odml.Property(name=match_line['name'], value="[val]")
        else:
            obj = odml.Section(name=match_line['name'], type=match_line['type'])

        if match_line['dst'] is not None:
            obj.mapping = 'map#%s' % match_line['dst']

        if match_line['link'] is not None:
            obj._link = match_line['link']

        parents[-1].append(obj)
        parents.append(obj)

    return parents[0]


class SampleFileCreator:
    def create_document(self):
        doc = odml.Document()
        for i in range(3):
            doc.append(self.create_section("sec %d" % i))

        return doc

    def create_section(self, name, depth=0):
        sec = odml.Section(name=name, type=name.replace("sec", "type"))
        if depth < 1:
            for i in range(2):
                sec.append(self.create_section("%s,%d" % (name, i), depth=depth + 1))

        if name.endswith("1"):
            for i in range(3):
                sec.append(self.create_property("%s:%d" % (name, i)))

        return sec

    @staticmethod
    def create_property(name):
        return odml.Property(name=name.replace("sec", "prop"),
                             value=name.replace("sec", "val"))


class SampleFileCreatorTest(unittest.TestCase):

    @staticmethod
    def test_sample_file():
        _ = SampleFileCreator().create_document()


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

    def test_xml_writer_version(self):
        doc = odml.Document()
        val = str(xmlparser.XMLWriter(doc))

        self.assertIn('version="%s"' % FORMAT_VERSION, val)
        doc = xmlparser.XMLReader().from_string(val)

        # This test is switched off until the XML versioning support is implemented
        # self.assertEqual(doc._xml_version, FORMAT_VERSION)

    def test_save(self):
        base_path = create_test_dir(__file__)
        for module in [xmlparser.XMLWriter]:
            path = os.path.join(base_path, "temp.odml")
            doc = module(self.doc)
            doc.write_file(path)
            os.remove(path)

    def test_restore(self):
        modules = [(xmlparser.XMLWriter, xmlparser.XMLReader)]

        for Writer, Reader in modules:
            doc = Writer(self.doc)
            doc = StringIO(str(doc))
            doc = Reader().from_file(doc)
            self.assertEqual(doc, self.doc)

#        for a,b in zip(doc.sections, self.doc.sections):
#            print "sec cmp", a, b
#            self.assertEqual(a, b)
#        print "A ---------------------------------"
#        for sec in doc.sections:
#            xmlparser.dump_section(sec)
#        print "B ---------------------------------"
#        for sec in self.doc.sections:
#            xmlparser.dump_section(sec)
#        print "-----------------------------------"


class AttributeTest(unittest.TestCase):

    def test_value_int(self):
        prop = odml.Property("test", 1, dtype="int")
        self.assertEqual(prop.values[0], 1)

    def test_conversion_int_to_float(self):
        prop = odml.Property("test", "1", dtype="int")
        self.assertEqual(prop.dtype, "int")
        self.assertIsInstance(prop.values[0], int)

        # change dtype
        prop.dtype = "float"
        self.assertEqual(prop.dtype, "float")
        self.assertEqual(prop.values[0], 1.0)

    def test_conversion_float_to_int(self):
        prop = odml.Property("test", "1.5", dtype="float")
        self.assertEqual(prop.dtype, "float")
        prop.dtype = "int"
        self.assertEqual(prop.dtype, "int")
        self.assertEqual(prop.values[0], 1)

    def test_value_float(self):
        prop = odml.Property("test", value="1.5", dtype="float")
        self.assertEqual(prop.values[0], 1.5)


class CopyTest(unittest.TestCase):

    def setUp(self):
        self.prop = odml.Property(name="test", value=1)

    def test_dependence(self):
        prop1 = self.prop
        prop2 = self.prop
        self.assertEqual(prop1, prop2)
        prop1.values = 5
        self.assertEqual(prop1, prop2)
        self.assertEqual(prop1.values, prop2.values)

    def test_independence(self):
        prop1 = self.prop.clone()
        prop2 = self.prop.clone()
        self.assertEqual(prop1, prop2)
        prop1.values = 5
        self.assertNotEqual(prop1, prop2)
        # self.assertUn


class MiscTest(unittest.TestCase):

    def setUp(self):
        self.doc = SampleFileCreator().create_document()

    def test_paths(self):
        sec = odml.Section("sec")
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
        self.assertIs(sec1.get_section_by_path(path_to_sec10), sec10)

        path_to_sec11 = sec10.get_relative_path(sec11)
        self.assertEqual(path_to_sec11, "../" + sec11.name)
        self.assertIs(sec10.get_section_by_path(path_to_sec11), sec11)

    def test_findall_related(self):
        doc = parse("""
        s1[T1]
        - s2[T1]
        """)
        self.assertEqual(len(doc.find_related(type="T1", findAll=True)), 2)

        doc = parse("""
        s0[T1]
        - s00[T2]
        s1[T2]
        s2[T1]
        """)
        self.assertEqual(
            len(doc.sections[1].find_related(type="T1", findAll=True)), 2)

    def test_reorder_post(self):
        old_index = self.doc.sections[0].reorder(2)
        self.assertEqual(old_index, 0)
        self.assertEqual(self.doc.sections[0].name, "sec 1")
        self.assertEqual(self.doc.sections[1].name, "sec 2")
        self.assertEqual(self.doc.sections[2].name, "sec 0")

    def test_reorder_first(self):
        old_index = self.doc.sections[2].reorder(0)
        self.assertEqual(old_index, 2)
        self.assertEqual(self.doc.sections[0].name, "sec 2")
        self.assertEqual(self.doc.sections[1].name, "sec 0")
        self.assertEqual(self.doc.sections[2].name, "sec 1")

    def test_get_section_by_path(self):
        sec1 = self.doc.sections[1]
        sec10 = sec1.sections[0]
        sec11 = sec1.sections[1]

        # test absolute path
        current = self.doc.get_section_by_path(sec10.get_path())
        self.assertEqual(current, sec10)

        # test relative path with ../
        current = sec10.get_section_by_path(sec10.get_relative_path(sec11))
        self.assertEqual(current, sec11)

        # test relative path with ./
        current = sec1.get_section_by_path(
            "./" + sec1.get_relative_path(sec11))
        self.assertEqual(current, sec11)

        # test relative path
        current = sec1.get_section_by_path(sec1.get_relative_path(sec11))
        self.assertEqual(current, sec11)

        # test wrong parent
        wrong_path = "../" + sec10.get_relative_path(sec11)
        self.assertRaises(ValueError, sec10.get_section_by_path, wrong_path)

        # test wrong child
        wrong_path = sec1.get_relative_path(sec10) + "/sec"
        self.assertRaises(ValueError, sec1.get_section_by_path, wrong_path)

        # test absolute path with no document
        new_sec = SampleFileCreator().create_section("sec", 0)
        path = new_sec.sections[0].get_path()
        self.assertRaises(ValueError, new_sec.sections[1].get_section_by_path, path)

        # test path with property is invalid
        path = sec11.properties[0].get_path()
        self.assertRaises(ValueError, self.doc.get_section_by_path, path)

    def test_get_property_by_path(self):
        sec0 = self.doc.sections[0]
        sec1 = self.doc.sections[1]
        sec00 = self.doc.sections[0].sections[0]
        sec11 = self.doc.sections[1].sections[1]
        sec10 = self.doc.sections[1].sections[0]
        prop = sec11.properties[0]

        # test absolute path from document
        current = self.doc.get_property_by_path(prop.get_path())
        self.assertEqual(current, prop)

        # test absolute path from section
        current = sec00.get_property_by_path(prop.get_path())
        self.assertEqual(current, prop)

        # test relative path from section
        manual_path = "../%s/%s:%s" % (sec1.name, sec11.name, prop.name)
        current = sec0.get_property_by_path(manual_path)
        self.assertEqual(current, prop)

        # test non-existing property
        wrong_path = sec10.get_relative_path(sec11) + ":foo"
        self.assertRaises(ValueError, sec1.get_property_by_path, wrong_path)

        # test path with section is invalid
        wrong_path = sec11.get_path()
        self.assertRaises(ValueError, sec1.get_property_by_path, wrong_path)

    def test_save_version(self):
        tmp_dir = create_test_dir(__file__)
        tmp_file = os.path.join(tmp_dir, "example.odml")

        self.doc.version = '2.4'
        writer = xmlparser.XMLWriter(self.doc)
        writer.write_file(tmp_file)

        restored = xmlparser.load(tmp_file)
        self.assertEqual(self.doc.version, restored.version)
