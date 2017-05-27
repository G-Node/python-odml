import sys
try:
    from setuptools import setup
except ImportError as ex:
    from distutils.core import setup

from odml import __version__

packages = [
    'odml',
    'odml.tools'
]

with open('README.rst') as f:
    description_text = f.read()

install_req = ["lxml"]
if sys.version_info < (3, 4):
    install_req += ["enum34"]

setup(name='odML',
      version=__version__,
      description='open metadata Markup Language',
      author='Hagen Fritsch',
      author_email='fritsch+gnode@in.tum.de',
      url='http://www.g-node.org/projects/odml',
      packages=packages,
      test_suite='test',
      install_requires=install_req,
      long_description=description_text,
      )
