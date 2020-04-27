import os
import shutil
import tempfile
import unittest

from contextlib import contextmanager

from odml.tools.converters import FormatConverter
from .util import create_test_dir

FC = FormatConverter

# TODO The used NamedTemporaryFile does not play nice with Windows;
# deactivating all affected tests for Windows until this has been fixed.


class TestFormatConverter(unittest.TestCase):
    def setUp(self):
        self.doc = """<odML version="1.1">
                        <section>
                            <type>some</type>
                            <name>S</name>
                        </section>
                      </odML>
                   """
        self.tmp_dir = None

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    @contextmanager
    def assertNotRaises(self, exc_type):
        try:
            yield None
        except exc_type:
            raise self.failureException('{} raised'.format(exc_type.__name__))

    def _create_open_file(self, in_dir):
        in_file = tempfile.NamedTemporaryFile(mode='a+', suffix=".xml", dir=in_dir)
        in_file.write(self.doc)
        in_file.seek(0)

        return in_file

    def test_convert(self):
        if os.name == 'nt':
            raise unittest.SkipTest("Skipping test on Windows")

        self.test_convert_dir_no_output_dir(False, FC.convert)
        self.test_convert_dir_no_output_dir(True, FC.convert)
        self.test_convert_dir_with_output_dir_specified(FC.convert)

    def test_convert_dir(self):
        if os.name == 'nt':
            raise unittest.SkipTest("Skipping test on Windows")

        with self.assertRaises(ValueError):
            FC.convert_dir(None, None, False, "not valid format")

        # Testing recursive part of the converter for not nested input dir
        self.test_convert_dir_no_output_dir(True)

    def test_convert_dir_no_output_dir(self, recursive=False, func=None):
        if os.name == 'nt':
            raise unittest.SkipTest("Skipping test on Windows")

        self.tmp_dir = create_test_dir(__file__)
        in_dir = tempfile.mkdtemp(dir=self.tmp_dir)
        in_file = self._create_open_file(in_dir)
        in_file2 = self._create_open_file(in_dir)

        if not func:
            FC.convert_dir(in_dir, None, recursive, "odml")
        else:
            if recursive:
                func([in_dir, "odml", "-r"])
            else:
                func([in_dir, "odml"])

        files = []
        for dir_path, dir_names, file_names in os.walk(self.tmp_dir):
            for file_name in file_names:
                files.append(os.path.join(dir_path, file_name))

        # check if the input file in the correct repo
        self.assertIn(os.path.join(in_dir, in_file.name), files)
        self.assertIn(os.path.join(in_dir, in_file2.name), files)

        # check if the output file in correct repo and has intended name
        in_files = [in_file.name, in_file2.name]
        for file in in_files:
            odml_file_name = os.path.basename(file)
            odml_file_name = odml_file_name.replace(".xml", ".odml")
            root, odml_dir_name = os.path.split(in_dir)
            odml_dir_name = odml_dir_name + "_odml"
            self.assertIn(os.path.join(root, odml_dir_name, odml_file_name), files)

        in_file.close()
        in_file2.close()

    def test_convert_dir_with_output_dir_specified(self, func=None):
        if os.name == 'nt':
            raise unittest.SkipTest("Skipping test on Windows")

        # Testing FC.convert_dir(in_dir, out_dir, False, "odml")
        self.tmp_dir = create_test_dir(__file__)
        in_dir = tempfile.mkdtemp(dir=self.tmp_dir)
        out_dir = tempfile.mkdtemp(dir=self.tmp_dir)
        in_file = self._create_open_file(in_dir)
        in_file2 = self._create_open_file(in_dir)

        if not func:
            FC.convert_dir(in_dir, out_dir, False, "odml")
        else:
            func([in_dir, "odml", "-out", out_dir])

        in_files = []
        out_files = []
        for dir_path, dir_names, file_names in os.walk(in_dir):
            for file_name in file_names:
                in_files.append(os.path.join(dir_path, file_name))

        for dir_path, dir_names, file_names in os.walk(out_dir):
            for file_name in file_names:
                out_files.append(os.path.join(dir_path, file_name))

        # check if the input file in the correct repo
        self.assertIn(os.path.join(in_dir, in_file.name), in_files)
        self.assertIn(os.path.join(in_dir, in_file2.name), in_files)

        # check if the output file in correct repo and has intended name
        check_in_files = [in_file.name, in_file2.name]
        for file in check_in_files:
            _, out_file_name = os.path.split(file)
            pre, ext = os.path.splitext(out_file_name)
            out_file_name = out_file_name.replace(out_file_name, pre + ".odml")
            self.assertIn(os.path.join(out_dir, out_file_name), out_files)

        in_file.close()
        in_file2.close()

    def test_check_io_directory(self):
        self.tmp_dir = create_test_dir(__file__)
        out_dir = tempfile.mkdtemp(dir=self.tmp_dir)
        in_dir = tempfile.mkdtemp(dir=self.tmp_dir)
        with self.assertRaises(ValueError):
            FC._check_input_output_directory(None, None)
        with self.assertRaises(ValueError):
            FC._check_input_output_directory("/not_valid_path", None)
        with self.assertRaises(ValueError):
            FC._check_input_output_directory(in_dir, "/not_valid_path")
        self.assertNotRaises(FC._check_input_output_directory(in_dir, None))
        self.assertNotRaises(FC._check_input_output_directory(in_dir, out_dir))
