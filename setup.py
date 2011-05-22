#!/usr/bin/env python
from distutils.core import setup
import os, glob

kwargs = {}
try:
    # only necessary for the windows build
    import py2exe
    kwargs.update({'console': ['odml-gui']})
except ImportError:
    pass

#TODO install gui.py as /usr/local/bin/odml-gui or similar
setup(name='odML',
      version='1.0',
      description='open metadata Markup Language',
      author='Hagen Fritsch',
      author_email='fritsch+gnode@in.tum.de',
      url='http://www.g-node.org/projects/odml',
      packages=[
        'odml',
        'odml.tools',
        'odml.tools.treemodel',
        'odml.tools.gui',
        ],
      scripts=['odml-gui'],
      data_files=[
        ('share/applications', ['odml.desktop']),
        ('share/pixmaps', glob.glob(os.path.join("images", "*")))
        ],
      options = {
          'py2exe': {
              'packages': 'odml',
              'includes': 'cairo, pango, pangocairo, atk, gobject, gio, lxml, gzip',
          }
      },
      **kwargs
     )

