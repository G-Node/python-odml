#!/usr/bin/env bash

echo
echo "-- MAKE SURE TO RUN THIS SCRIPT IN INTERACTIVE MODE '-i' --"

PY_VER_ARRAY=("|3.5|3.6|3.7|3.8|3.9|")

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
echo "-- Installing odml from PyPI test"
echo

pip install -q --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple -I odml

echo
echo "-- Installing dependencies and odml-ui from PyPI test"
echo

conda install -q -c pkgw/label/superseded gtk3 -y
conda install -q -c conda-forge pygobject -y
conda install -q -c conda-forge gdk-pixbuf -y
conda install -q -c pkgw-forge adwaita-icon-theme -y

pip install -q --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple -I odml-ui

echo
echo "-- checking odml version"
python -c "import odml; print('-- Testing against odml version v%s' % odml.VERSION)"
python -c "import odmlui; print('-- Testing against odmlui version v%s' % odmlui.info.VERSION)"

echo
echo "-- Running basic tests"
cd ${ROOT_DIR}/resources/test_load
BASIC_SCRIPT=${ROOT_DIR}/resources/scripts/odml_basics.py
python ${BASIC_SCRIPT}

if [[ ! $? -eq 0 ]]; then
    cd ${ROOT_DIR}
    conda deactivate
    echo
    echo "-- [FAILED] Encountered error in script ${BASIC_SCRIPT}"
    exit
fi

echo
echo "-- Returning to root"
cd ${ROOT_DIR}

echo
echo "-- Creating convert output folder"
OUT_DIR=/tmp/odml/out/${PYVER}/convert
mkdir -vp ${OUT_DIR}

echo
echo "-- Running conversion script tests"

if ! [[ -x "$(command -v odmlconvert)" ]]; then
    conda deactivate
    cd ${ROOT_DIR}
    echo
    echo "-- [FAILED] odmlconvert not installed"
    exit
fi

cd ${ROOT_DIR}/resources/test_convert_script
odmlconvert -o ${OUT_DIR} -r .

echo
echo "-- Returning to root"
cd ${ROOT_DIR}

echo
echo "-- Creating rdf output folder"
OUT_DIR=/tmp/odml/out/${PYVER}/rdf
mkdir -vp ${OUT_DIR}

if ! [[ -x "$(command -v odmltordf)" ]]; then
    conda deactivate
    cd ${ROOT_DIR}
    echo
    echo "-- [FAILED] odmltordf not installed"
    exit
fi

echo
echo "-- Running rdf conversion script test"
cd ${ROOT_DIR}/resources/test_rdf_export_script
odmltordf -o ${OUT_DIR} -r .

echo
echo "-- Returning to root"
cd ${ROOT_DIR}

conda deactivate

echo "-- Done"
echo
