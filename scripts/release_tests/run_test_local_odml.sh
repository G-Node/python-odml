#!/usr/bin/env bash

echo
echo "-- MAKE SURE TO RUN THIS SCRIPT IN INTERACTIVE MODE '-i' --"

PY_VER_ARRAY=("|3.5|3.6|3.7|3.8|3.9|3.10|3.11|")

if [[ $# != 1 ]]; then
    echo
    echo "-- [FAILED] Please provide a valid Python version: ${PY_VER_ARRAY}"
    exit 1
fi

PYVER=$1

if [[ ! "${PY_VER_ARRAY}" =~ "|${PYVER}|" ]]; then
    echo
    echo "-- [FAILED] Please provide a valid Python version: ${PY_VER_ARRAY}"
    exit 1
fi

echo
echo "-- Using Python version ${PYVER}"

SCRIPT_DIR=$(pwd)
cd ../..
ROOT_DIR=$(pwd)

echo
echo "-- Running directory check: ${ROOT_DIR}"
CHECK_DIR=$(basename ${ROOT_DIR})
if [[ ! "$CHECK_DIR" = "python-odml" ]]; then
    echo "-- [FAILED] In wrong directory ${ROOT_DIR}"
    exit 1
fi

echo
echo "-- Running active conda env check: ${CONDA_PREFIX}"
if [[ ! -z "${CONDA_PREFIX}" ]]; then
    echo "-- Deactivating conda env: ${CONDA_PREFIX}"
    conda deactivate
fi

CONDA_ENV_SETUP=odmlsetup${PYVER}
CONDA_ENV_PIP=odmlpip${PYVER}

echo
echo "-- Testing local pip installation"
echo "-- Cleanup previous conda environment and create new one"
echo
conda remove -q -n ${CONDA_ENV_PIP} --all -y
conda create -q -n ${CONDA_ENV_PIP} python=${PYVER} -y

conda activate ${CONDA_ENV_PIP}
pip install -q --upgrade pip

echo
echo "-- Local installation (pip)"
echo
pip install .

echo
echo "-- Installing test dependencies"
pip install -r requirements-test.txt

echo
echo "-- Running tests"
pytest -v

conda deactivate

echo
echo "-- Testing local setup installation"
echo "-- Cleanup previous conda environment and create new one"
echo
conda remove -q -n ${CONDA_ENV_SETUP} --all -y
conda create -q -n ${CONDA_ENV_SETUP} python=${PYVER} -y

conda activate ${CONDA_ENV_SETUP}
pip install -q --upgrade pip

echo
echo "-- Local installation (setup.py)"
echo
python setup.py install

echo
echo "-- Installing test dependencies"
pip install -r requirements-test.txt

echo
echo "-- Running tests"
pytest -v

conda deactivate

echo
echo "-- Returning to script directory ${SCRIPT_DIR}"
echo
cd ${SCRIPT_DIR}

echo "-- Done"
echo
