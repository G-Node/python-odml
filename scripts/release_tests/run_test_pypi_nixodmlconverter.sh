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

if [[ "${PYVER}" == "3.5" ]]; then
    echo
    echo "-- Ignoring unsupported Python version 3.5"
    exit 0
fi

echo
echo "-- Using Python version ${PYVER}"

ROOT_DIR=$(pwd)
CONDA_ENV=odmlpip${PYVER}

echo
echo "-- Running directory check: ${ROOT_DIR}"
CHECK_DIR=$(basename ${ROOT_DIR})
if [[ ! "$CHECK_DIR" = "release_tests" ]]; then
    echo "-- [FAILED] In wrong directory ${ROOT_DIR}"
    exit 1
fi

echo
echo "-- Running active conda env check: ${CONDA_PREFIX}"
if [[ ! -z "${CONDA_PREFIX}" ]]; then
    echo "-- Deactivating conda env: ${CONDA_PREFIX}"
    conda deactivate
fi

echo
echo "-- Cleanup previous conda environment and create new one"
echo
conda remove -q -n ${CONDA_ENV} --all -y

conda create -q -n ${CONDA_ENV} python=${PYVER} -y

conda activate ${CONDA_ENV}
pip install -q --upgrade pip
pip install -q ipython

echo
echo "-- Installing nixodmlconverter from PyPI test"

pip install -q --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple -I nixodmlconverter

if ! [[ -x "$(command -v nixodmlconverter)" ]]; then
    conda deactivate
    cd ${ROOT_DIR}
    echo
    echo "-- [FAILED] nixodmlconverter not installed"
    exit
fi


OUT_DIR=/tmp/odml/out/${PYVER}/nixodmlconverter
mkdir -vp ${OUT_DIR}
cp ${ROOT_DIR}/resources/test_nixodmlconv/example.odml.xml ${OUT_DIR}/

cd ${OUT_DIR}

echo
echo "-- checking odml version"
python -c "import odml; print('-- Testing against odml version v%s' % odml.VERSION)"

echo
echo "-- running nixodmlconverter help"
nixodmlconverter -h

echo
echo "-- running nixodmlconversion odml->nix"
if [[ -f example.odml.nix ]]; then
    rm example.odml.nix
fi
nixodmlconverter example.odml.xml

if ! [[ -f example.odml.nix ]]; then
    conda deactivate
    cd ${ROOT_DIR}
    echo
    echo "-- [FAILED] nixodmlconverter conversion odml->nix"
    exit
fi

cp example.odml.nix export.odml.nix

echo
echo "-- running nixodmlconversion nix->odml"
if [[ -f export.odml.xml ]]; then
    rm export.odml.xml
fi
nixodmlconverter export.odml.nix

if ! [[ -f export.odml.xml ]]; then
    conda deactivate
    cd ${ROOT_DIR}
    echo
    echo "-- [FAILED] nixodmlconverter conversion nix->odml"
    exit
fi

echo
echo "-- Returning to root"
cd ${ROOT_DIR}

conda deactivate

echo "-- Done"
echo
