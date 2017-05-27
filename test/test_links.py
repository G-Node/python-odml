import unittest
from . import test_samplefile as samplefile


class TestLinks(unittest.TestCase):

    def setUp(self):
        self.doc = samplefile.SampleFileCreator().create_document()
        # for s in self.doc: xmlparser.dumpSection(s)

    def test_link_creation(self):
        obj = self.doc.sections[0].sections[0]
        dst = self.doc.sections[1].sections[1]

        self.assertNotEqual(obj, dst)
        obj.link = "/sec 1/sec 1,1"
        self.assertIsNot(obj, dst)
        self.assertEqual(obj.sections, dst.sections)
        self.assertEqual(obj.properties, dst.properties)

        obj.clean()
        self.assertNotEqual(obj, dst)

    def no_test_circles(self):
        # TODO this currently just works, although, maybe it shouldn't?

        # we cannot allow self-referencing links
        obj = self.doc.sections[0].sections[0]
        dst = self.doc.sections[0]

        samplefile.dumper.dumpSection(dst)

        obj.link = "/sec 0"
        # self.assertEqual(obj.sections, dst.sections) # this will FAIL
        # self.assertEqual(obj.properties, dst.properties)
        obj.clean()

        samplefile.dumper.dumpSection(dst)

    def test_merge(self):
        obj = self.doc.sections[0].sections[0]  # must be an empty section
        dst = self.doc.sections[1]  # .sections[1]
        org = obj.clone()

        obj.link = '/sec 1'
        self.assertEqual(obj.sections, dst.sections)
        self.assertEqual(obj.properties, dst.properties)
        self.assertEqual(obj._merged, dst)

        obj.clean()
        self.assertIsNone(obj._merged)
        self.assertEqual(obj.sections, org.sections)
        self.assertEqual(obj.properties, org.properties)
