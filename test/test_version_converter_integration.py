"""
This file tests proper conversion of complex v1.0 odML files
to v1.1 with all supported file formats.
"""

import os
import shutil
import tempfile
import unittest


class TestVersionConverterIntegration(unittest.TestCase):
    def setUp(self):
        # Set up test environment
        self.tmp_dir = tempfile.mkdtemp(suffix=".odml")

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
