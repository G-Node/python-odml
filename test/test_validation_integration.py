"""
This file tests built-in odml validations.
"""

import sys
import unittest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import odml


class TestValidationIntegration(unittest.TestCase):

    def setUp(self):
        # Redirect stdout to test messages
        self.stdout_orig = sys.stdout
        self.capture = StringIO()
        sys.stdout = self.capture

        self.msg_base = "Property values cardinality violated"

    def tearDown(self):
        # Reset stdout; resetting using 'sys.__stdout__' fails on windows
        sys.stdout = self.stdout_orig
        self.capture.close()

    def _clear_output(self):
        self.capture.seek(0)
        self.capture.truncate()

    def _get_captured_output(self):
        out = [txt.strip() for txt in self.capture.getvalue().split('\n') if txt]

        # Buffer reset
        self.capture.seek(0)
        self.capture.truncate()

        return out

    def test_property_values_cardinality(self):
        # -- Test assignment validation warnings
        doc = odml.Document()
        sec = odml.Section(name="sec", type="sec_type", parent=doc)

        # Making sure only the required warnings are tested
        self._clear_output()

        # -- Test cardinality validation warnings on Property init
        # Test warning when setting invalid minimum
        _ = odml.Property(name="prop_card_min", values=[1], val_cardinality=(2, None), parent=sec)
        output = self._get_captured_output()
        test_msg = "%s (minimum %s values, %s found)" % (self.msg_base, 2, 1)
        self.assertEqual(len(output), 1)
        self.assertIn(test_msg, output[0])

        # Test warning when setting invalid maximum
        _ = odml.Property(name="prop_card_max", values=[1, 2, 3], val_cardinality=2, parent=sec)
        output = self._get_captured_output()
        test_msg = "%s (maximum %s values, %s found)" % (self.msg_base, 2, 3)
        self.assertEqual(len(output), 1)
        self.assertIn(test_msg, output[0])

        # Test no warning on valid init
        prop_card = odml.Property(name="prop_card", values=[1, 2],
                                  val_cardinality=(1, 5), parent=sec)
        output = self._get_captured_output()
        self.assertEqual(output, [])

        # -- Test cardinality validation warnings on cardinality updates
        # Test warning when setting minimally required values cardinality
        prop_card.val_cardinality = (3, None)
        output = self._get_captured_output()
        test_msg = "%s (minimum %s values, %s found)" % (self.msg_base, 3, 2)
        self.assertEqual(len(output), 1)
        self.assertIn(test_msg, output[0])

        # Test warning when setting maximally required values cardinality
        prop_card.values = [1, 2, 3]
        prop_card.val_cardinality = 2
        output = self._get_captured_output()
        test_msg = "%s (maximum %s values, %s found)" % (self.msg_base, 2, 3)
        self.assertEqual(len(output), 1)
        self.assertIn(test_msg, output[0])

        # Test no warning on valid cardinality
        prop_card.val_cardinality = (1, 10)
        output = self._get_captured_output()
        self.assertEqual(output, [])

        # Test no warning when setting cardinality to None
        prop_card.val_cardinality = None
        output = self._get_captured_output()
        self.assertEqual(output, [])

        # -- Test cardinality validation warnings on values updates
        # Test warning when violating minimally required values cardinality
        prop_card.val_cardinality = (3, None)
        prop_card.values = [1, 2]
        output = self._get_captured_output()
        test_msg = "%s (minimum %s values, %s found)" % (self.msg_base, 3, 2)
        self.assertEqual(len(output), 1)
        self.assertIn(test_msg, output[0])

        # Test warning when violating maximally required values cardinality
        prop_card.val_cardinality = (None, 2)
        prop_card.values = [1, 2, 3]
        output = self._get_captured_output()
        test_msg = "%s (maximum %s values, %s found)" % (self.msg_base, 2, 3)
        self.assertEqual(len(output), 1)
        self.assertIn(test_msg, output[0])

        # Test no warning when setting correct number of values
        prop_card.values = [1, 2]
        output = self._get_captured_output()
        self.assertEqual(output, [])

        # Test no warning when setting values to None
        prop_card.values = None
        output = self._get_captured_output()
        self.assertEqual(output, [])
