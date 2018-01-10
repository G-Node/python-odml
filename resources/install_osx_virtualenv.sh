#!/bin/bash

echo Running install_osx_virtalenv.sh

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then

    brew update;

    if [[ "$OSXENV" == "2.7" ]]; then
        brew install python;
        virtualenv venv -p python;
        source venv/bin/activate;
    else
        brew install python3;
        virtualenv venv -p python3;
        source venv/bin/activate;
    fi
fi

which python
