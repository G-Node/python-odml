#!/usr/bin/env bash

echo
echo "-- MAKE SURE TO RUN THIS SCRIPT IN INTERACTIVE MODE '-i' --"

PY_VER_ARRAY=("|3.5|3.6|3.7|3.8|3.9|3.10|")

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
echo "-- Installing odmltools from PyPI test"

pip install -q --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple -I odmltools

if ! [[ -x "$(command -v odmlimportdatacite)" ]]; then
    conda deactivate
    cd ${ROOT_DIR}
    echo
    echo "-- [FAILED] odmlimportdatacite not installed"
    exit
fi

OUT_DIR=/tmp/odml/out/${PYVER}/odmltools
mkdir -vp ${OUT_DIR}
cd ${ROOT_DIR}/resources/test_odmltools

echo
echo "-- checking odml version"
python -c "import odml; print('-- Testing against odml version v%s' % odml.VERSION)"

echo
echo "-- running odmltools conversion tests"
odmlimportdatacite -o ${OUT_DIR} -r ./datacite
odmlimportdatacite -o ${OUT_DIR} -r -f RDF ./datacite
odmlimportdatacite -o ${OUT_DIR} -r -f YAML ./datacite
odmlimportdatacite -o ${OUT_DIR} -r -f JSON ./datacite

echo
echo "-- checking namespace test success"
odmlimportdatacite -o ${OUT_DIR} ./datacite_namespace/fullDataCiteSchemaNS.xml

echo
echo "-- checking namespace test fail"
odmlimportdatacite -o ${OUT_DIR} ./datacite_namespace/DataCitePreviousNS.xml

echo
echo "-- checking namespace escape test success"
odmlimportdatacite -o ${OUT_DIR} -n http://datacite.org/schema/kernel-2 ./datacite_namespace/DataCitePreviousNS.xml

echo
echo "-- Returning to root"
cd ${ROOT_DIR}

conda deactivate

echo "-- Done"
echo
