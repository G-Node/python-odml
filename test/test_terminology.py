"""
Tests functions and classes from the odml terminology module.
"""

import os
import tempfile
import unittest

from glob import glob
from sys import platform
from time import sleep
try:
    from urllib.request import pathname2url
except ImportError:
    from urllib import pathname2url

from odml import Document, save, Section, terminology
from .util import ODML_CACHE_DIR as CACHE_DIR


class TestTerminology(unittest.TestCase):

    def setUp(self):
        """
        Set up local temporary terminology files in a temporary folder
        """
        tmp_dir = tempfile.mkdtemp("_odml")
        tmp_name = os.path.basename(tmp_dir)

        main_name = "%s_main.xml" % tmp_name
        main_file_path = os.path.join(tmp_dir, main_name)
        main_url = "file://%s" % pathname2url(main_file_path)

        include_name = "%s_include.xml" % tmp_name
        include_file_path = os.path.join(tmp_dir, include_name)
        include_url = "file://%s" % pathname2url(include_file_path)

        include_doc = Document()
        _ = Section(name="include_sec", type="test", parent=include_doc)
        save(include_doc, include_file_path)

        main_doc = Document()
        _ = Section(name="main_sec", type="test", include=include_url, parent=main_doc)
        save(main_doc, main_file_path)

        self.main_terminology_url = main_url
        self.temp_dir_base = tmp_name

    def tearDown(self):
        """
        Remove all created files from the odml.cache to not cross pollute other tests.
        The created tmp directory should be cleaned up automatically upon startup.
        """
        temp_file_glob = "*%s*" % self.temp_dir_base
        find_us = os.path.join(CACHE_DIR, temp_file_glob)

        for file_path in glob(find_us):
            os.remove(file_path)

    @staticmethod
    def _cache_files_map(file_filter="*"):
        """
        Returns a dict mapping the basefilenames of cached odml files
        to their md5 hash and mtime.

        :param file_filter: a valid glob to search for files in the odml cache directory.
                            The cache directory is provided and must not be part of the glob.
                            Default value is '*'.

        :return: dict of the format {filename: [md5_hash, mtime]}
        """
        temp_file_glob = os.path.join(CACHE_DIR, file_filter)

        curr_map = {}
        for file_path in glob(temp_file_glob):
            split_name = os.path.basename(file_path).split('.')
            file_mtime = os.path.getmtime(file_path)
            curr_map[split_name[1]] = [split_name[0], file_mtime]

        return curr_map

    def test_terminology_refresh(self):
        """
        Test terminology cache refresh using local files to detach
        loading and resolving from the live online terminology repository.
        """
        # Fetch current cache content specific to the two local terminologies
        # With the default file glob '*' all files in the odml cache directory would be
        # included in the test.
        file_filter = "*%s*" % self.temp_dir_base
        main_url = self.main_terminology_url

        # Initially load main and included file from temp directory into the odml cache directory
        terminology.load(main_url)

        orig_map = self._cache_files_map(file_filter)

        # Test cache content does not change
        terminology.load(main_url)
        load_map = self._cache_files_map(file_filter)

        self.assertEqual(len(orig_map), len(load_map))
        for curr_file in orig_map:
            self.assertIn(curr_file, load_map)
            self.assertEqual(orig_map[curr_file], load_map[curr_file])

        sleep_time = 0.5
        if platform == "darwin":
            sleep_time = 2

        # Sleep is needed since the tests might be too fast to result in a
        # different file mtime. Travis macOS seems to require sleep time > 1s.
        sleep(sleep_time)

        # Test refresh loads same cached files but changes them.
        # Different mtimes and id strings are sufficient.
        terminology.refresh(main_url)
        refresh_map = self._cache_files_map(file_filter)
        self.assertEqual(len(orig_map), len(refresh_map))
        for curr_file in orig_map:
            self.assertIn(curr_file, refresh_map)
            # Check identical md5 hash
            self.assertEqual(orig_map[curr_file][0], refresh_map[curr_file][0])
            # Check different mtime
            self.assertLess(orig_map[curr_file][1], refresh_map[curr_file][1])
