import unittest
import sys
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import odml

from odml.tools.dumper import dump_doc


class TestTypes(unittest.TestCase):

    def setUp(self):
        s_type = "type"

        self.doc = odml.Document(author='Rave', version='1.0')
        sec1 = odml.Section(name='Cell', type=s_type)
        prop1 = odml.Property(name='Type', values='Rechargeable')
        sec1.append(prop1)

        sec2 = odml.Section(name='Electrolyte', type=s_type)
        prop2 = odml.Property(name='Composition', values='Ni-Cd')
        sec2.append(prop2)
        sec1.append(sec2)

        sec3 = odml.Section(name='Electrode', type=s_type)
        prop3 = odml.Property(name='Material', values='Nickel')
        prop4 = odml.Property(name='Models', values=['AA', 'AAA'])
        sec3.append(prop3)
        sec3.append(prop4)
        sec2.append(sec3)

        self.doc.append(sec1)

    def test_dump_doc(self):
        # Capture the output printed by the functions to STDOUT, and use it for
        # testing purposes. It needs to be reset after the capture.
        captured_stdout = StringIO()
        sys.stdout = captured_stdout

        # This test dumps the whole document and checks it word by word.
        # If possible, maybe some better way of testing this?
        dump_doc(self.doc)
        output = [x.strip() for x in captured_stdout.getvalue().split('\n') if x]

        # Reset stdout
        sys.stdout = sys.__stdout__

        expected_output = ["*Cell (type='type')",
                           ":Type (values=Rechargeable, dtype='string')",
                           "*Electrolyte (type='type')",
                           ":Composition (values=Ni-Cd, dtype='string')",
                           "*Electrode (type='type')",
                           ":Material (values=Nickel, dtype='string')",
                           ":Models (values=[AA,AAA], dtype='string')"]

        self.assertEqual(len(output), len(expected_output))
        for i, _ in enumerate(output):
            self.assertEqual(output[i], expected_output[i])
