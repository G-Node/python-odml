#!/usr/bin/env python
from distutils.core import setup
import sys, os, glob

kwargs = {}
try:
    # only necessary for the windows build
    import py2exe
    kwargs.update({'console': ['odml-gui']})
except ImportError:
    pass

packages=[
        'odml',
        'odml.tools'
	]

if '--no-gui' in sys.argv:
    sys.argv.remove('--no-gui')
else:
    packages.append('odml.gui')
    packages.append('odml.gui.dnd')
    packages.append('odml.gui.treemodel')
    kwargs['data_files']=[
        ('share/applications', ['odml.desktop']),
        ('share/pixmaps', glob.glob(os.path.join("images", "*")))
        ]
    kwargs['scripts']=['odml-gui']

setup(name='odML',
      version='1.0',
      description='open metadata Markup Language',
      author='Hagen Fritsch',
      author_email='fritsch+gnode@in.tum.de',
      url='http://www.g-node.org/projects/odml',
      packages=packages,
      options = {
          'py2exe': {
              'packages': 'odml',
              'includes': 'cairo, pango, pangocairo, atk, gobject, gio, lxml, gzip',
          }
      },
      **kwargs
     )

