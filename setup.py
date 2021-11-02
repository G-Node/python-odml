import json
import os

from sys import version_info as _python_version

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

# pyparsing needs to be pinned to 2.4.7 for the time being. setup install fetches a pre-release
# package that currently results in issues with the rdflib library.
install_req = ["lxml", "pyyaml>=5.1", "rdflib==5.0.0", "docopt", "pathlib", "pyparsing==2.4.7"]

# owlrl depends on rdflib - the pinned version should be removed once the version pin has also been
# removed from rdflib. Also needs to be updated in requirements-test.txt
tests_req = ["pytest", "owlrl==5.2.3", "requests"]

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
    tests_require=tests_req,
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

# Make this the last thing people read after a setup.py install
if _python_version.major < 3:
    msg = "Python 2 has reached end of live."
    msg += "\n\todML support for Python 2 has been dropped."
    print(msg)
elif _python_version.major == 3 and _python_version.minor < 6:
    msg = "\n\nThis package is not tested with your Python version. "
    msg += "\n\tPlease consider upgrading to the latest Python distribution."
    print(msg)
