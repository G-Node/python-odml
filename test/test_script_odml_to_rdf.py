import os
import shutil
import unittest

from docopt import DocoptExit
from rdflib import Graph

from odml.scripts import odml_to_rdf

from . import util


class TestScriptOdmlToRDF(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = util.create_test_dir(__file__)
        self.dir_files = os.path.join(util.TEST_RESOURCES_DIR, "scripts", "odml_to_rdf")
        self.dir_invalid = os.path.join(self.dir_files, "test_invalid")
        self.dir_recursive = os.path.join(self.dir_files, "test_recursive")

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

    def _check_intermediate_dirs(self):
        # make sure an odml version conversion output directory has been created
        out_dir_lst = os.listdir(self.tmp_dir)
        self.assertEqual(len(out_dir_lst), 1)
        out_dir = os.path.join(self.tmp_dir, out_dir_lst[0])
        self.assertTrue(os.path.isdir(out_dir))

        # make sure an rdf conversion output directory has been created
        rdf_dir_lst = os.listdir(out_dir)
        self.assertEqual(len(rdf_dir_lst), 1)
        rdf_dir = os.path.join(out_dir, rdf_dir_lst[0])
        self.assertTrue(os.path.isdir(rdf_dir))

        return rdf_dir

    def test_valid_conversion(self):
        # make sure temp dir is empty
        self.assertListEqual(os.listdir(self.tmp_dir), [])

        # run converter on root directory containing two files
        odml_to_rdf.main(["-o", self.tmp_dir, self.dir_files])

        rdf_dir = self._check_intermediate_dirs()

        # make sure two files have been created
        file_lst = os.listdir(rdf_dir)
        self.assertEqual(len(file_lst), 2)

        # make sure the files are valid RDF files
        curr_graph = Graph()
        curr_graph.parse(os.path.join(rdf_dir, file_lst[0]))
        curr_graph.parse(os.path.join(rdf_dir, file_lst[1]))

    def test_invalid(self):
        # make sure temp dir is empty
        self.assertListEqual(os.listdir(self.tmp_dir), [])

        # run converter on directory with invalid files
        odml_to_rdf.main(["-o", self.tmp_dir, self.dir_invalid])

        rdf_dir = self._check_intermediate_dirs()

        # make sure no file has been created
        self.assertListEqual(os.listdir(rdf_dir), [])

    def test_recursive_conversion(self):
        # make sure temp dir is empty
        self.assertListEqual(os.listdir(self.tmp_dir), [])

        # run converter on root directory containing two files
        odml_to_rdf.main(["-r", "-o", self.tmp_dir, self.dir_recursive])

        rdf_dir = self._check_intermediate_dirs()

        # make sure two files have been created
        file_lst = os.listdir(rdf_dir)
        self.assertEqual(len(file_lst), 2)

        # make sure the files are valid RDF files
        curr_graph = Graph()
        curr_graph.parse(os.path.join(rdf_dir, file_lst[0]))
        curr_graph.parse(os.path.join(rdf_dir, file_lst[1]))
