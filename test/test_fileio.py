import unittest
import sys
import os
import odml

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class TestTypes(unittest.TestCase):
    # TODO :- Write tests for JSONParser once it's completed.

    def setUp(self):
        self.file = 'doc/example_odMLs/THGTTG.odml'
        # Do not allow anything to be printed on STDOUT
        self.captured_stdout = StringIO()
        sys.stdout = self.captured_stdout

    def test_load_save(self):
        doc = odml.load(self.file)
        self.assertTrue(isinstance(doc, odml.doc.BaseDocument))
        odml.save(doc, self.file + '_copy')
        os.remove(self.file + '_copy')

    def test_display(self):
        doc = odml.load(self.file)
        odml.display(doc)

    def test_invalid_parser(self):
        with self.assertRaises(NotImplementedError):
            odml.load(self.file, 'html')

        doc = odml.load(self.file)
        with self.assertRaises(NotImplementedError):
            odml.save(doc, self.file + '_copy_html', 'html')

        with self.assertRaises(NotImplementedError):
            odml.display(doc, 'html')

