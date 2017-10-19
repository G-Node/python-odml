import unittest
import sys
import odml

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class TestTypes(unittest.TestCase):

    def setUp(self):
        # Capture the output printed by the functions to STDOUT, and use it for
        # testing purposes.
        self.captured_stdout = StringIO()
        sys.stdout = self.captured_stdout

        self.doc = odml.Document(author='Rave', version='1.0')
        s1 = odml.Section(name='Cell')
        p1 = odml.Property(name='Type', value='Rechargeable')
        s1.append(p1)

        s2 = odml.Section(name='Electrolyte')
        p2 = odml.Property(name='Composition', value='Ni-Cd')
        s2.append(p2)
        s1.append(s2)

        s3 = odml.Section(name='Electrode')
        p3 = odml.Property(name='Material', value='Nickel')
        p4 = odml.Property(name='Models', value=['AA', 'AAA'])
        s3.append(p3)
        s3.append(p4)
        s2.append(s3)

        self.doc.append(s1)

    def test_dump_doc(self):
        # This test dumps the whole document and checks it word by word.
        # If possible, maybe some better way of testing this ?
        odml.tools.dumper.dumpDoc(self.doc)
        output = [x.strip() for x in self.captured_stdout.getvalue().split('\n') if x]
        expected_output = []
        expected_output.append("*Cell ()")
        expected_output.append(":Type (value=Rechargeable, dtype='string')")
        expected_output.append("*Electrolyte ()")
        expected_output.append(":Composition (value=Ni-Cd, dtype='string')")
        expected_output.append("*Electrode ()")
        expected_output.append(":Material (value=Nickel, dtype='string')")
        expected_output.append(":Models (value=[AA,AAA], dtype='string')")
        self.assertEqual(len(output), len(expected_output))
        for i in range(len(output)):
            self.assertEqual(output[i], expected_output[i])

        # Discard the document output from stdout stream
        self.captured_stdout.seek(0)
        self.captured_stdout.truncate(0)
