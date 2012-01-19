odML libraries and editor
=========================

Installation
------------

To install the package simply run:

    $ sudo python setup.py install --prefix /usr

If you just want to try out, tell python where to find the library
and start either the gui or a python shell:

    $ PYTHONPATH=. ./odml-gui
    $ PYTHONPATH=. python

### Windows

A windows package is seperately bundled.
To build the windows package from source, follow these instructions:

1. Install the following software (ALWAYS use the 32-bit versions!)
    * [python-2.7](http://www.python.org/getit/windows/)
    * [pygtk-windows](all-in-one installer: http://www.pygtk.org/downloads.html)
    * [py2exe](http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/py2exe-0.6.9.win32-py2.7.exe/download)
    * [setuptools](http://pypi.python.org/pypi/setuptools#files)

2. Install build dependencies

   `$ easy_install.exe lxml`

   If this fails, you can fall back to installing it from the 
   [Unofficial Windows Binaries for Python Extension Packages](http://www.lfd.uci.edu/~gohlke/pythonlibs/#lxml)

3. To just run the software use:

   `$ python.exe odml-gui`

   You may also rename odml-gui to odml-gui.py, which allows you to start
   the gui through double clicking on that file. You can even right click and
   send it as a shortcut to the desktop.

4. Compile a binary for redistribution

   `$ python.exe setup.py py2exe`

   For some reason the compiled binary has a different look, so running
   the software from source gets a more native look.

Bugs & Questions
----------------

Should you find a behaviour that is likely a bug, please file
a bug report at [the github bug tracker](https://github.com/G-Node/python-odml/issues).

If you have questions regarding the use of the library or the editor, ask
the question on [Stack Overflow](http://stackoverflow.com/), be sure to tag
it with `odml` and we'll do our best to quickly solve the problem.
