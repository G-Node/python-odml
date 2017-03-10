import sys
try:
    from setuptools import setup
except ImportError as ex:
    from distutils.core import setup

packages = [
    'odml',
    'odml.tools'
]

with open('README.rst') as f:
    description_text = f.read()

install_req = ["lxml"]
if sys.version_info < (3, 4):
    install_req += ["enum"]

setup(name='odML',
      version='1.3.dev0',
      description='open metadata Markup Language',
      author='Hagen Fritsch',
      author_email='fritsch+gnode@in.tum.de',
      url='http://www.g-node.org/projects/odml',
      packages=packages,
      test_suite='test',
      install_requires=install_req,
      long_description=description_text,
      )
