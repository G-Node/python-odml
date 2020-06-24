import os
import shutil
import unittest

from docopt import DocoptExit

from odml import load as odml_load
from odml.scripts import odml_convert
from . import util


class TestScriptOdmlConvert(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = util.create_test_dir(__file__)
        self.dir_files = os.path.join(util.TEST_RESOURCES_DIR, "scripts", "odml_convert")

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_script_exit(self):
        with self.assertRaises(DocoptExit):
            odml_convert.main([])

        with self.assertRaises(DocoptExit):
            odml_convert.main(["-o", self.tmp_dir])

        with self.assertRaises(SystemExit):
            odml_convert.main(["-h"])

    def test_valid_conversion(self):
        # make sure temp dir is empty
        self.assertListEqual(os.listdir(self.tmp_dir), [])

        # run converter on root directory containing two files
        odml_convert.main(["-o", self.tmp_dir, self.dir_files])

        # make sure an output directory has been created
        out_dir_lst = os.listdir(self.tmp_dir)
        self.assertEqual(len(out_dir_lst), 1)
        out_dir = os.path.join(self.tmp_dir, out_dir_lst[0])
        self.assertTrue(os.path.isdir(out_dir))

        # make sure two files have been created
        file_lst = os.listdir(out_dir)
        self.assertEqual(len(file_lst), 2)

        # make sure the files are valid odml files
        _ = odml_load(os.path.join(out_dir, file_lst[0]))
        _ = odml_load(os.path.join(out_dir, file_lst[1]))
