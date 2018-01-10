import sys

try:
    from setuptools import setup
except ImportError as ex:
    from distutils.core import setup
from odml.info import AUTHOR, CONTACT, CLASSIFIERS, HOMEPAGE, VERSION

packages = [
    'odml',
    'odml.tools'
]

with open('README.rst') as f:
    description_text = f.read()

with open("LICENSE") as f:
    license_text = f.read()

install_req = ["lxml", "pyyaml", "rdflib", "rdflib-jsonld"]

if sys.version_info < (3, 4):
    install_req += ["enum34"]

setup(
    name='odML',
    version=VERSION,
    description='open metadata Markup Language',
    author=AUTHOR,
    author_email=CONTACT,
    url=HOMEPAGE,
    packages=packages,
    test_suite='test',
    install_requires=install_req,
    long_description=description_text,
    classifiers=CLASSIFIERS,
    license=license_text
)
