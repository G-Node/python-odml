#!/bin/bash
echo %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
echo Running install_osx_virtalenv.sh
python --version;
echo travis python version:  $TRAVIS_PYTHON_VERSION
echo %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then

    brew update;

    if [[ "$OSXENV" == "2.7" ]]; then
        echo python 2.7
        brew install python;
        virtualenv venv -p python;
        source venv/bin/activate;
    else
        echo some other version 
        brew install python3;
        virtualenv venv -p python3;
        source venv/bin/activate;
        export PYCMD=python3;
        export PIPCMD=pip3;
    fi
fi

which python
