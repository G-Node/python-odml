import os
import shutil
import tempfile
import unittest

import odml

from odml.tools.xmlparser import XML_HEADER, EXTERNAL_STYLE_HEADER, \
    INFILE_STYLE_HEADER, INFILE_STYLE_TEMPLATE
from odml.tools import XMLWriter


class TestXMLWriter(unittest.TestCase):
    def setUp(self):
        # Set up test environment
        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.xmlfile = os.path.join(dir_path, "resources", "version_conversion_int.xml")

        self.tmp_dir = tempfile.mkdtemp(suffix=".odml")
        self.outfile = os.path.join(self.tmp_dir, "xml_writer.xml")

        doc = odml.Document()
        sec = doc.create_section(name="sec", type="test")
        _ = sec.create_property(name="prop", value=['a', 'b', 'c'])

        self.doc = doc
        self.writer = XMLWriter(doc)

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_write_default(self):
        self.writer.write_file(self.outfile)

        # make sure the file can be read again without errors
        doc = odml.load(self.outfile)
        self.assertEqual(doc, self.doc)

    def test_write_style_default(self):
        self.writer.write_file(self.outfile, local_style=True)

        # make sure the file can be read again without errors
        doc = odml.load(self.outfile)
        self.assertEqual(doc, self.doc)

    def test_write_style_custom(self):
        # template stub just to see if its written properly; will not render anything
        cust_tmpl = "<xsl:template></xsl:template>"

        self.writer.write_file(self.outfile, local_style=True, custom_template=cust_tmpl)

        # make sure the file can be read again without errors
        doc = odml.load(self.outfile)
        self.assertEqual(doc, self.doc)

        # test second possible way to save
        self.writer.write_file(self.outfile, local_style=False, custom_template=cust_tmpl)

        # make sure the file can be read again without errors
        doc = odml.load(self.outfile)
        self.assertEqual(doc, self.doc)
