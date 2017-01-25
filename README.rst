odML libraries and editor
=========================
.. image:: https://travis-ci.org/G-Node/python-odml.svg?branch=master
    :target: https://travis-ci.org/G-Node/python-odml
.. image:: https://coveralls.io/repos/github/G-Node/python-odml/badge.svg?branch=master
    :target: https://coveralls.io/github/G-Node/python-odml?branch=master

The Python-odML library (including the odML-Editor) is available on
`GitHub <https://github.com/G-Node/python-odml>`_. If you are not familiar with
the version control system **git**, but still want to use it, have a look at
the documentaion available on the `git-scm website <https://git-scm.com/>`_.

Dependencies
------------

* Python 2.7 or 3.5
* Python packages:

  * enum (version 0.4.4)
  * lxml (version 3.7.2)

* These packages will be downloaded and installed automatically if the :code:`pip` method is used to install odML. Alternatively, they can be installed from the OS package manager. On Ubuntu, they are available as:

  * python-enum
  * python-lxml

* If you prefer installing using the Python package manager, the following packages are required to build the lxml Python package on Ubuntu 14.04:

  * libxml2-dev
  * libxslt1-dev
  * lib32z1-dev


Installation
------------

The simplest way to install Python-odML is from PyPI using the pip tool::

  $ pip install odml

On Ubuntu, the pip package manager is available in the repositories as :code:`python-pip`.

If this method is used, the appropriate Python dependencies (enum and lxml) are downloaded and installed automatically.


Building from source
--------------------

To download the Python-odML library please either use git and clone the
repository from GitHub::

  $ cd /home/usr/toolbox/
  $ git clone https://github.com/G-Node/python-odml.git

If you don't want to use git download the ZIP file also provided on
GitHub to your computer (e.g. as above on your home directory under a "toolbox"
folder).

To install the Python-odML library, enter the corresponding directory and run::

  $ cd /home/usr/toolbox/python-odml/
  $ python setup.py install


Documentation
-------------

`Documentation <https://g-node.github.io/python-odml>`_

Bugs & Questions
----------------

Should you find a behaviour that is likely a bug, please file a bug report at
`the github bug tracker <https://github.com/G-Node/python-odml/issues>`_.

If you have questions regarding the use of the library or the editor, ask
the question on `Stack Overflow <http://stackoverflow.com/>`_, be sure to tag
it with :code:`odml` and we'll do our best to quickly solve the problem.
