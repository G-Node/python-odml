import json
import os
import sys

try:
    from setuptools import setup
except ImportError as ex:
    from distutils.core import setup

with open(os.path.join("odml", "info.json")) as infofile:
    infodict = json.load(infofile)

VERSION = infodict["VERSION"]
FORMAT_VERSION = infodict["FORMAT_VERSION"]
AUTHOR = infodict["AUTHOR"]
COPYRIGHT = infodict["COPYRIGHT"]
CONTACT = infodict["CONTACT"]
HOMEPAGE = infodict["HOMEPAGE"]
CLASSIFIERS = infodict["CLASSIFIERS"]


packages = [
    'odml',
    'odml.rdf',
    'odml.scripts',
    'odml.tools',
    'odml.tools.converters'
]

with open('README.md') as f:
    description_text = f.read()

install_req = ["lxml", "pyyaml==4.2b4", "rdflib", "docopt", "pathlib"]

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
    include_package_data=True,
    long_description=description_text,
    long_description_content_type="text/markdown",
    classifiers=CLASSIFIERS,
    license="BSD",
    entry_points={'console_scripts': ['odmltordf=odml.scripts.odml_to_rdf:main',
                                      'odmlconversion=odml.scripts.odml_convert:dep_note',
                                      'odmlconvert=odml.scripts.odml_convert:main',
                                      'odmlview=odml.scripts.odml_view:main']}
)
