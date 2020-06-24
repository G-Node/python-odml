import os
import shutil
import unittest

from docopt import DocoptExit

from odml.scripts import odml_to_rdf

from . import util


class TestScriptOdmlToRDF(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = util.create_test_dir(__file__)

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_script_exit(self):
        with self.assertRaises(DocoptExit):
            odml_to_rdf.main([])

        with self.assertRaises(DocoptExit):
            odml_to_rdf.main(["-o", self.tmp_dir])

        with self.assertRaises(SystemExit):
            odml_to_rdf.main(["-h"])

        with self.assertRaises(SystemExit):
            odml_to_rdf.main(["--version"])
