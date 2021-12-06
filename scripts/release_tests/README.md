# odml and odml dependent libraries installation tests

Used to document the minimal automated tests for `python-odml` and `odmltools` and not fully automated tests of `odml-ui` installations with a special focus on the execution of command line scripts and gui with different local installation methods.

## Automated odml and dependent library tests

The tests include
- basic odml import and file loading and saving
- `odml` command line script execution using realistic example files
  - odmlview
  - odmltordf
  - odmlconversion
- `odmltools` command line script execution
  - odmlimportdatacite
- basic odml-ui installation

### Local installation tests

To test the various local installations of odml, execute `run_test_matrix.sh` with option 'A'. odml will be installed into fresh conda environments using `pip install .` and `python setup.py install` and all Python versions >= 3.5.

### odml Test PyPI installation tests

To test the installation of the odml package from Test PyPI, execute `run_test_matrix.sh` with option 'B'. odml will be installed into fresh conda environments using `pip install odml` and all Python versions >= 3.5.
The package `odml-ui` will be installed as well and all installable odml command line scripts will be tested after the odml installation.

### odmltools Test PyPI installation tests

When executing `run_test_matrix.sh` with option 'C', the odml dependent package `odmltools` will be pip installed into fresh conda environments for all Python versions >= 3.6 from the Test PyPI repository and appropriate conversion tests will be run using the installed command line tool.

### nixodmlconverter Test PyPI installation tests

When executing `run_test_matrix.sh` with option 'D' the odml dependent package `nixodmlconverter` will be pip installed into fresh conda environments for all Python versions >= 3.6 from the Test PyPI repository and appropriate conversion tests will be run using the installed command line tool.

### odml PyPI installation tests

To test the installation of the odml package from PyPI proper, execute `run_test_matrix.sh` with option 'E'. odml will be installed into fresh conda environments using `pip install odml` and all Python versions >= 3.5.
The package `odml-ui` will be installed as well and all installable odml command line scripts will be tested after the odml installation.

## Manual odml-ui tests

To set up conda environments and run local or Test PyPI installations run the script `run_test_matrix.sh` with option `B` from the current directory.
Once set up, the conda environments can be used to manually test `odml-ui` as well.

Activate python installation environment

    CONDA_ENV_SETUP=pyinst
    CONDA_ENV_PIP=pipinst
    ROOT_DIR=$(pwd)
    cd $ROOT_DIR/resources/test_load
    conda activate ${CONDA_ENV_SETUP}
    odmlui

Run the following most tests:
- open `test_load\load_v1.odml.xml`
- check fail message
- import `test_load\load_v1.odml.xml`
- save as `pyi_conv.xml`
- save as `pyi_conv.yaml`
- save as `pyi_conv.json`
- open `pyi_conv.xml`
- open `pyi_conv.yaml`
- open `pyi_conv.json`
- check importing a terminology using the document wizard

Exit and switch to pip environment 

    conda deactivate
    conda activate ${CONDA_ENV_PIP}
    odmlui

Run manual tests again

Test odmltables plugin

    pip install odmltables
    pip install odmltables[gui]
    odmlui

Run the following minimal tests
- open `pyi_conv.xml`
- use odmltables `convert` button, save as csv file
- use odmltables `filter` button

Exit, move back to the root and cleanup

    cd $ROOT_DIR
    conda deactivate
    rm $ROOT_DIR/resources/test_load/load_v1.odml_converted.xml
    rm $ROOT_DIR/resources/test_load/pyi_conv.json
    rm $ROOT_DIR/resources/test_load/pyi_conv.xml
    rm $ROOT_DIR/resources/test_load/pyi_conv.yaml
