"""
Utilities for the odml test package.
"""
import os
import tempfile

ODML_CACHE_DIR = os.path.join(tempfile.gettempdir(), "odml.cache")
