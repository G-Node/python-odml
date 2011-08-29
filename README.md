odML libraries and editor
=========================

Installation
------------

To install the package simply run:

   `$ sudo python setup.py install --prefix /usr`

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

3. Compile

   `$ python.exe setup.py py2exe`
