import datetime
import os
import unittest
try:
    from urllib.request import pathname2url
except ImportError:
    from urllib import pathname2url

from odml import Document, Section, Property
from odml.doc import BaseDocument
from odml.dtypes import FORMAT_DATE


class TestSection(unittest.TestCase):
    def setUp(self):
        pass

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
        dir_path = os.path.dirname(os.path.realpath(__file__))
        repo_file = os.path.join(dir_path, "resources",
                                           "local_repository_file_v1.1.xml")
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
