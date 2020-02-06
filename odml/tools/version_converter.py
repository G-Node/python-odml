"""
This module provides backwards compatibility for the VersionConverter class.
It is deprecated and will be removed in future versions.
"""

from .converters import VersionConverter

print("[DEPRECATION WARNING] The VersionConverter file has been moved to "
      "'odml.tools.converters' and will be removed from 'odml.tools' in future "
      "odML releases. Please update the imports in your code accordingly.")
