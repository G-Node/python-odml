import sys

try:
    from setuptools import setup
except ImportError as ex:
    from distutils.core import setup

try:
    from odml.info import AUTHOR, CONTACT, CLASSIFIERS, HOMEPAGE, VERSION
except ImportError as ex:
    # Read the information from odml.info.py if package dependencies
    # are not yet available during a local install.
    CLASSIFIERS = ""
    with open('odml/info.py') as f:
        for line in f:
            curr_args = line.split(" = ")
            if len(curr_args) == 2:
                if curr_args[0] == "AUTHOR":
                    AUTHOR = curr_args[1].replace('\'', '').replace('\\', '').strip()
                elif curr_args[0] == "CONTACT":
                    CONTACT = curr_args[1].replace('\'', '').strip()
                elif curr_args[0] == "HOMEPAGE":
                    HOMEPAGE = curr_args[1].replace('\'', '').strip()
                elif curr_args[0] == "VERSION":
                    VERSION = curr_args[1].replace('\'', '').strip()

packages = [
    'odml',
    'odml.tools'
]

with open('README.rst') as f:
    description_text = f.read()

install_req = ["lxml", "pyyaml", "rdflib"]

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
    license="BSD"
)
