"""
Utilities for the odml test package.
"""
import os
import tempfile

ODML_CACHE_DIR = os.path.join(tempfile.gettempdir(), "odml.cache")

TEST_RESOURCES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  "resources")

TEST_TEMP_DIR = os.path.join(tempfile.gettempdir(), "odml_test")
if not os.path.exists(TEST_TEMP_DIR):
    os.mkdir(TEST_TEMP_DIR)


def create_test_dir(script_name):
    """
    Takes the name of a test script and creates a like-named directory
    in the main test directory if it does not yet exist.

    :param script_name: String that will be used to create the test directory

    :return: Path to the test directory.
    """
    dir_name = "_%s" % os.path.basename(os.path.splitext(script_name)[0])

    return tempfile.mkdtemp(suffix=dir_name, dir=TEST_TEMP_DIR)
