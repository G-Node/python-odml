import os
import shutil
import unittest

import odml

from odml.tools.xmlparser import XML_HEADER, EXTERNAL_STYLE_HEADER, \
    INFILE_STYLE_HEADER, INFILE_STYLE_TEMPLATE
from odml.tools import XMLWriter
from .util import create_test_dir, TEST_RESOURCES_DIR as RES_DIR


class TestXMLWriter(unittest.TestCase):
    def setUp(self):
        # Set up test environment
        self.xmlfile = os.path.join(RES_DIR, "version_conversion_int.xml")

        self.tmp_dir = create_test_dir(__file__)
        self.outfile = os.path.join(self.tmp_dir, "xml_writer.xml")

        doc = odml.Document()
        sec = doc.create_section(name="sec", type="test")
        _ = sec.create_property(name="prop", value=['a', 'b', 'c'])

        self.doc = doc
        self.writer = XMLWriter(doc)

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_write_default(self):
        self.writer.write_file(self.outfile)

        # make sure the file can be read again without errors
        doc = odml.load(self.outfile)
        self.assertEqual(doc, self.doc)

        # test style content in saved file
        with open(self.outfile) as test_file:
            content = test_file.read()

        self.assertIn(XML_HEADER, content)
        self.assertIn(EXTERNAL_STYLE_HEADER, content)

    def test_write_style_default(self):
        self.writer.write_file(self.outfile, local_style=True)

        # make sure the file can be read again without errors
        doc = odml.load(self.outfile)
        self.assertEqual(doc, self.doc)

        # test style content in saved file
        with open(self.outfile) as test_file:
            content = test_file.read()

        self.assertIn(XML_HEADER, content)
        self.assertIn(INFILE_STYLE_HEADER, content)
        self.assertIn(INFILE_STYLE_TEMPLATE, content)

    def test_write_style_custom(self):
        # template stub just to see if its written properly; will not render anything
        cust_tmpl = "<xsl:template></xsl:template>"

        self.writer.write_file(self.outfile, local_style=True, custom_template=cust_tmpl)

        # make sure the file can be read again without errors
        doc = odml.load(self.outfile)
        self.assertEqual(doc, self.doc)

        # test style content in saved file
        with open(self.outfile) as test_file:
            content = test_file.read()

        self.assertIn(XML_HEADER, content)
        self.assertIn(INFILE_STYLE_HEADER, content)
        self.assertNotIn(INFILE_STYLE_TEMPLATE, content)
        self.assertIn(cust_tmpl, content)

        # --- test second possible way to save
        self.writer.write_file(self.outfile, local_style=False, custom_template=cust_tmpl)

        # make sure the file can be read again without errors
        doc = odml.load(self.outfile)
        self.assertEqual(doc, self.doc)

        # test style content in saved file
        with open(self.outfile) as test_file:
            content = test_file.read()

        self.assertIn(XML_HEADER, content)
        self.assertIn(INFILE_STYLE_HEADER, content)
        self.assertNotIn(INFILE_STYLE_TEMPLATE, content)
        self.assertIn(cust_tmpl, content)
