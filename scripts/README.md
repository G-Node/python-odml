## python-odml convenience scripts

This folder contains convenience scripts for build and deployment tests and should not be part of any release. Check the README files in the specific folders for details. 

The `release_tests` folder contains scripts and resources to test the odML library and all its dependent libraries like odmltools, odmlui, odmlconverter and nix-odml-converter from a local odML installation, from Test-PyPI and PyPI packages.
The local version tests the installation via `pip install .` and `python setup.py install`. The Test-PyPI and PyPI package tests use conda environments to test the installation with all Python versions >= 3.5. 
