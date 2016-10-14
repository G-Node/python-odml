#!/usr/bin/env python

import sys
import os
import glob

try:
    from setuptools import setup
except ImportError as ex:
    from distutils.core import setup

kwargs = {}

packages = [
    'odml',
    'odml.tools'
]


setup(name='odML',
      version='1.2',
      description='open metadata Markup Language',
      author='Hagen Fritsch',
      author_email='fritsch+gnode@in.tum.de',
      url='http://www.g-node.org/projects/odml',
      packages=packages,
      test_suite='test',
      **kwargs)
