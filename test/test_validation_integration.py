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
        self.capture = StringIO()
        sys.stdout = self.capture

        self.msg_base = "Property values cardinality violated"

    def tearDown(self):
        # Reset stdout
        sys.stdout = sys.__stdout__

    def _get_captured_output(self):
        out = [txt.strip() for txt in self.capture.getvalue().split('\n') if txt]

        # Buffer reset
        self.capture.seek(0)
        self.capture.truncate()

        return out

