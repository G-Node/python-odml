import os
import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import odml

from .util import TEST_RESOURCES_DIR as RES_DIR


class TestTypes(unittest.TestCase):

    def setUp(self):
        self.file = os.path.join(RES_DIR, "example.odml")
        # Do not allow anything to be printed on STDOUT
        self.captured_stdout = StringIO()
        sys.stdout = self.captured_stdout

    def test_load_save(self):
        doc = odml.load(self.file)
        self.assertTrue(isinstance(doc, odml.doc.BaseDocument))
        file_name = "%s_copy" % self.file
        odml.save(doc, file_name)
        os.remove(file_name)

    def test_save_kwargs(self):
        doc = odml.load(self.file)
        file_name = "%s_copy" % self.file

        # Test unsupported kwarg does not raise an exception
        odml.save(doc, file_name, unsupported_kwarg="I do not matter")
        os.remove(file_name)

    def test_display(self):
        doc = odml.load(self.file)
        odml.display(doc)

    def test_invalid_parser(self):
        with self.assertRaises(NotImplementedError):
            odml.load(self.file, "html")

        doc = odml.load(self.file)
        with self.assertRaises(NotImplementedError):
            file_name = "%s_copy_html" % self.file
            odml.save(doc, file_name, "html")

        with self.assertRaises(NotImplementedError):
            odml.display(doc, "html")
