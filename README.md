![Travis build](https://travis-ci.org/G-Node/python-odml.svg?branch=master)
[![Build status](https://ci.appveyor.com/api/projects/status/br7pe6atlwdg5618/branch/master?svg=true)](https://ci.appveyor.com/project/G-Node/python-odml/branch/master)
![Test coverage](https://coveralls.io/repos/github/G-Node/python-odml/badge.svg?branch=master)
[![PyPI version](https://img.shields.io/pypi/v/odml.svg)](https://pypi.org/project/odML/)

# odML (Open metaData Markup Language) core library

The open metadata Markup Language is a file based format (XML, JSON, YAML) for storing
metadata in an organised human- and machine-readable way. odML is an initiative to define
and establish an open, flexible, and easy-to-use format to transport metadata.

The Python-odML library can be easily installed via ```pip```. The source code is freely
available on [GitHub](https://github.com/G-Node/python-odml). If you are not familiar
with the version control system **git**, but still want to use it, have a look at the
documentation available on the [git-scm website](https://git-scm.com/).


# Breaking changes


odML Version 1.4 introduced breaking format and API changes compared to the previous
versions of odML. Files saved in the previous format versions can be converted to a 1.4
compatible format using the version converter from the odml/tools package.

Be aware that the value dtype ```binary``` has been removed. Incorporating actual binary
data into odML files is discouraged, provide references to the original files using the
```URL``` dtype instead.

For details regarding the introduced changes please check the [github
release notes](https://github.com/G-Node/python-odml/releases).


# Dependencies

* Python 2.7 or 3.5
* Python packages:

  * enum (version 0.4.4)
  * lxml (version 3.7.2)
  * yaml (version 3.12)
  * rdflib (version >=4.2.2)

* These packages will be downloaded and installed automatically if the ```pip```
  method is used to install odML. Alternatively, they can be installed from the OS
  package manager. On Ubuntu, they are available as:

  * python-enum
  * python-lxml
  * python-yaml
  * python-rdflib

* If you prefer installing using the Python package manager, the following packages are
  required to build the lxml Python package on Ubuntu 14.04:

  * libxml2-dev
  * libxslt1-dev
  * lib32z1-dev


# Installation

The simplest way to install Python-odML is from PyPI using the pip tool:


```
  $ pip install odml
```

On Ubuntu, the pip package manager is available in the repositories as ```python-pip```.

If this method is used, the appropriate Python dependencies are downloaded and installed
automatically.


# Building from source

To download the Python-odML library please either use git and clone
the repository from GitHub:

```
  $ git clone https://github.com/G-Node/python-odml.git
```

If you don't want to use git download the ZIP file also provided on
GitHub to your computer (e.g. as above on your home directory under a "toolbox"
folder).

To install the Python-odML library, enter the corresponding directory and run:

```
  $ cd python-odml
  $ python setup.py install
```

**Note** The master branch is our current development branch, not all features might be
working as expected. Use the release tags instead.

# odML Project page

More information about the project including related projects as well as tutorials and
examples can be found at our odML [project page](https://g-node.github.io/python-odml).

# Contributing and Governance

See the [CONTRIBUTING](CONTIBUTING.md) document for more information on this.

# Bugs & Questions

Should you find a behaviour that is likely a bug, please file a bug report at
[the github bug tracker](https://github.com/G-Node/python-odml/issues).

If you have questions regarding the use of the library, feel free to join the
[#gnode](http://webchat.freenode.net?channels=%23gnode) IRC channel on freenode.
