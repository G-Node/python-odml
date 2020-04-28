import datetime
import os
import unittest

from glob import glob

try:
    from urllib.request import pathname2url
except ImportError:
    from urllib import pathname2url

from odml import Document, Section, Property
from odml.doc import BaseDocument
from odml.dtypes import FORMAT_DATE
from .util import ODML_CACHE_DIR as CACHE_DIR, TEST_RESOURCES_DIR as RES_DIR


class TestSection(unittest.TestCase):
    def setUp(self):
        self.local_repo_file = "local_repository_file_v1.1.xml"

    def tearDown(self):
        """
        Remove all files loaded to the terminology cache directory
        to avoid test cross pollution.
        """
        temp_file_glob = "*%s" % self.local_repo_file
        find_us = os.path.join(CACHE_DIR, temp_file_glob)

        for file_path in glob(find_us):
            os.remove(file_path)

    def test_simple_attributes(self):
        author = "HPL"
        version = "4.8.15"
        doc = Document(author=author, version=version)

        self.assertEqual(doc.author, author)
        self.assertEqual(doc.version, version)

        doc.author = ""
        doc.version = ""
        self.assertIsNone(doc.author)
        self.assertIsNone(doc.version)

        doc.author = author
        doc.version = version
        self.assertEqual(doc.author, author)
        self.assertEqual(doc.version, version)

    def test_id(self):
        doc = Document()
        self.assertIsNotNone(doc.id)

        doc = Document("D", oid="79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertEqual(doc.id, "79b613eb-a256-46bf-84f6-207df465b8f7")

        doc = Document("D", oid="id")
        self.assertNotEqual(doc.id, "id")

        # Make sure id cannot be reset programmatically.
        with self.assertRaises(AttributeError):
            doc.id = "someId"

    def test_new_id(self):
        doc = Document()
        old_id = doc.id

        # Test assign new generated id.
        doc.new_id()
        self.assertNotEqual(old_id, doc.id)

        # Test assign new custom id.
        old_id = doc.id
        doc.new_id("79b613eb-a256-46bf-84f6-207df465b8f7")
        self.assertNotEqual(old_id, doc.id)
        self.assertEqual("79b613eb-a256-46bf-84f6-207df465b8f7", doc.id)

        # Test invalid custom id exception.
        with self.assertRaises(ValueError):
            doc.new_id("crash and burn")

    def test_date(self):
        datestring = "2000-01-02"
        doc = Document(date=datestring)

        self.assertIsInstance(doc.date, datetime.date)
        self.assertEqual(doc.date,
                         datetime.datetime.strptime(datestring, FORMAT_DATE).date())

        doc.date = None
        self.assertIsNone(doc.date)

        doc.date = datestring
        self.assertIsInstance(doc.date, datetime.date)
        self.assertEqual(doc.date,
                         datetime.datetime.strptime(datestring, FORMAT_DATE).date())

        doc.date = []
        self.assertIsNone(doc.date)
        doc.date = {}
        self.assertIsNone(doc.date)
        doc.date = ()
        self.assertIsNone(doc.date)
        doc.date = ""
        self.assertIsNone(doc.date)

        with self.assertRaises(ValueError):
            doc.date = "some format"

    def test_get_terminology_equivalent(self):
        repo_file = os.path.join(RES_DIR, self.local_repo_file)
        local_url = "file://%s" % pathname2url(repo_file)

        doc = Document(repository=local_url)

        teq = doc.get_terminology_equivalent()
        self.assertIsInstance(teq, BaseDocument)
        self.assertEqual(len(teq), 1)
        self.assertEqual(teq.sections[0].name, "Repository test")

        doc.repository = None
        self.assertIsNone(doc.get_terminology_equivalent())

    def test_append(self):
        doc = Document()
        self.assertListEqual(doc.sections, [])

        # Test append Section
        sec = Section(name="sec_one")
        doc.append(sec)
        self.assertEqual(len(doc.sections), 1)
        self.assertEqual(sec.parent, doc)

        # Test fail on Section list or tuple append
        with self.assertRaises(ValueError):
            doc.append([Section(name="sec_two"), Section(name="sec_three")])
        with self.assertRaises(ValueError):
            doc.append((Section(name="sec_two"), Section(name="sec_three")))
        self.assertEqual(len(doc.sections), 1)

        # Test fail on unsupported value
        with self.assertRaises(ValueError):
            doc.append(Document())
        with self.assertRaises(ValueError):
            doc.append("Section")
        with self.assertRaises(ValueError):
            doc.append(Property(name="prop"))

        # Test fail on same name entities
        with self.assertRaises(KeyError):
            doc.append(Section(name="sec_one"))
        self.assertEqual(len(doc.sections), 1)

    def test_extend(self):
        doc = Document()
        self.assertListEqual(doc.sections, [])

        # Test extend with Section list
        doc.extend([Section(name="sec_one"), Section(name="sec_two")])
        self.assertEqual(len(doc), 2)
        self.assertEqual(len(doc.sections), 2)
        self.assertEqual(doc.sections[0].name, "sec_one")

        # Test fail on non iterable
        with self.assertRaises(TypeError):
            doc.extend(1)
        self.assertEqual(len(doc.sections), 2)

        # Test fail on non Section entry
        with self.assertRaises(ValueError):
            doc.extend([Document()])
        with self.assertRaises(ValueError):
            doc.extend([Property(name="prop")])
        with self.assertRaises(ValueError):
            doc.extend([5])
        self.assertEqual(len(doc.sections), 2)

        # Test fail on same name entities
        with self.assertRaises(KeyError):
            doc.extend([Section(name="sec_three"), Section(name="sec_one")])
        self.assertEqual(len(doc.sections), 2)

    def test_insert(self):
        doc = Document()

        sec_one = Section(name="sec_one", parent=doc)
        sec_two = Section(name="sec_two", parent=doc)
        subsec = Section(name="sec_three")

        self.assertNotEqual(doc.sections[1].name, subsec.name)
        doc.insert(1, subsec)
        self.assertEqual(len(doc.sections), 3)
        self.assertEqual(doc.sections[1].name, subsec.name)
        self.assertEqual(doc.sections[0].name, sec_one.name)
        self.assertEqual(doc.sections[2].name, sec_two.name)
        self.assertEqual(subsec.parent, doc)

        # Test invalid object
        with self.assertRaises(ValueError):
            doc.insert(1, Document())
        with self.assertRaises(ValueError):
            doc.insert(1, Property(name="prop_one"))
        with self.assertRaises(ValueError):
            doc.insert(1, "some info")
        self.assertEqual(len(doc), 3)

        # Test same name entries
        with self.assertRaises(ValueError):
            doc.insert(0, subsec)
        self.assertEqual(len(doc), 3)

    def test_comparison(self):
        doc_auth = "author"
        doc_ver = "ver1.0"

        doc_a = Document(author=doc_auth, version=doc_ver)
        doc_b = Document(author=doc_auth, version=doc_ver)

        self.assertEqual(doc_a, doc_b)

        doc_b.author = "someone else"
        self.assertNotEqual(doc_a, doc_b)

        doc_b.author = doc_auth

        # Test section equality with subsections

        # Test equality with subsection of different entities
        # with same content and same children order
        sec_type = "sec type"
        sec_def = "an odml test section"
        sec_ref = "from over there"

        subsec_aa = Section(name="subsecA", type=sec_type,
                            definition=sec_def, reference=sec_ref)
        subsec_ab = Section(name="subsecB", type=sec_type,
                            definition=sec_def, reference=sec_ref)
        subsec_ba = Section(name="subsecA", type=sec_type,
                            definition=sec_def, reference=sec_ref)
        subsec_bb = Section(name="subsecB", type=sec_type,
                            definition=sec_def, reference=sec_ref)

        doc_a.extend([subsec_aa, subsec_ab])
        doc_b.extend([subsec_ba, subsec_bb])

        self.assertEqual(doc_a, doc_b)
        self.assertEqual(doc_a.sections, doc_b.sections)

        doc_b.sections[0].name = "newSubsecA"
        self.assertNotEqual(doc_a, doc_b)
        self.assertNotEqual(doc_a.sections, doc_b.sections)

        doc_b.sections[0].name = "subsecA"

        # Test inequality with different number of children
        doc_b.remove(doc_b.sections[1])
        self.assertNotEqual(doc_a, doc_b)
        self.assertNotEqual(doc_a.sections, doc_b.sections)

        # Test equality with subsection of different entities
        # with same content and different children order
        doc_b.remove(doc_b.sections[0])
        doc_b.extend([subsec_bb, subsec_ba])

        self.assertEqual(doc_a, doc_b)
        self.assertEqual(doc_a.sections, doc_b.sections)

        doc_b.sections[0].name = "newSubsecB"
        self.assertNotEqual(doc_a, doc_b)
        self.assertNotEqual(doc_a.sections, doc_b.sections)

        doc_b.sections[0].name = "subsecB"

        # Test section equality with properties

        # Test equality with properties of different entities
        # with same content and same children order
        prop_aa = Property(name="propA", definition="propDef")
        prop_ab = Property(name="propB", definition="propDef")
        prop_ba = Property(name="propA", definition="propDef")
        prop_bb = Property(name="propB", definition="propDef")

        doc_a.sections["subsecA"].extend([prop_aa, prop_ab])
        doc_b.sections["subsecA"].extend([prop_ba, prop_bb])

        self.assertEqual(doc_a, doc_b)

        doc_b.sections["subsecA"].properties[0].name = "newPropA"
        self.assertNotEqual(doc_a, doc_b)

        doc_b.sections["subsecA"].properties[0].name = "propA"

        # Test inequality with different number of children
        doc_b.sections["subsecA"].remove(doc_b.sections["subsecA"].properties[1])
        self.assertNotEqual(doc_a, doc_b)

        # Test equality with properties of different entities
        # with same content and different children order
        doc_b.sections["subsecA"].remove(doc_b.sections["subsecA"].properties[0])
        doc_b.sections["subsecA"].extend([prop_bb, prop_ba])

        self.assertEqual(doc_a, doc_b)

        doc_b.sections["subsecA"].properties[0].name = "newPropB"
        self.assertNotEqual(doc_a, doc_b)

    def test_create_section(self):
        root = Document()
        self.assertEqual(len(root.sections), 0)

        name = "subsec"
        sec_type = "subtype"
        oid = "79b613eb-a256-46bf-84f6-207df465b8f7"
        subsec = root.create_section(name, sec_type, oid)

        self.assertEqual(len(root.sections), 1)
        self.assertEqual(subsec.parent, root)
        self.assertEqual(root.sections[name], subsec)
        self.assertEqual(root.sections[name].type, sec_type)
        self.assertEqual(root.sections[name].oid, oid)

        name = "othersec"
        subsec = root.create_section(name)
        self.assertEqual(len(root.sections), 2)
        self.assertEqual(subsec.parent, root)
        self.assertEqual(root.sections[name], subsec)
        self.assertEqual(root.sections[name].type, "n.s.")

        name = "subsubsec"
        subsec = root.sections[0].create_section(name)
        self.assertEqual(len(root.sections), 2)
        self.assertEqual(subsec.parent, root.sections[0])
        self.assertEqual(len(root.sections[0].sections), 1)
        self.assertEqual(root.sections[0].sections[0].name, name)
