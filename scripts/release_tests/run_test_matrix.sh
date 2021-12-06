#!/usr/bin/env bash

echo
echo "-- Running python-odml package test installation matrix"

print_options () {
    echo
    echo "-- Missing or invalid test script selection letter (A|B|C|D|E), please provide one of the following"
    echo "     A: local install test (odml)"
    echo "     B: Test PyPI install test (odml)"
    echo "     C: Test PyPI install test (odmltools)"
    echo "     D: Test PyPI install test (nixodmlconverter)"
    echo "     E: PyPI install test (odml)"
}

if [[ $# != 1 ]]; then
    print_options
    exit 1
fi

TEST_ARRAY=("|A|B|C|D|E|")
TEST=$1

if [[ ! "${TEST_ARRAY}" =~ "|${TEST}|" ]]; then
    print_options
    exit 1
fi

if [[ "${TEST}" == "A" ]]; then
    echo
    echo "-- Running local test odml installations"
    LOG_DIR=/tmp/odml/local_install_odml
    SCRIPT=./run_test_local_odml.sh
    echo "${SCRIPT}"
fi

if [[ "${TEST}" == "B" ]]; then
    echo
    echo "-- Running PyPI test odml installations"
    LOG_DIR=/tmp/odml/pypi_test_install_odml
    SCRIPT=./run_test_pypi_odml.sh
fi

if [[ "${TEST}" == "C" ]]; then
    echo
    echo "-- Running PyPI test odmltools installations"
    LOG_DIR=/tmp/odml/pypi_test_install_odmltools
    SCRIPT=./run_test_pypi_odmltools.sh
fi

if [[ "${TEST}" == "D" ]]; then
    echo
    echo "-- Running PyPI test nixodmlconverter installations"
    LOG_DIR=/tmp/odml/pypi_test_install_nixodmlconverter
    SCRIPT=./run_test_pypi_nixodmlconverter.sh
fi

if [[ "${TEST}" == "E" ]]; then
    echo
    echo "-- Running PyPI odml installations"
    LOG_DIR=/tmp/odml/pypi_install_odml
    SCRIPT=./run_pypi_odml.sh
fi

ROOT_DIR=$(pwd)

echo
echo "-- Running directory check: ${ROOT_DIR}"
CHECK_DIR=$(basename ${ROOT_DIR})
if [[ ! "${CHECK_DIR}" = "release_tests" ]]; then
    echo
    echo "-- In wrong directory ${ROOT_DIR}"
    exit 1
fi

echo
echo "-- Creating log directory ${LOG_DIR}"
mkdir -vp ${LOG_DIR}
if [[ ! -d "${LOG_DIR}" ]]; then
    echo
    echo "-- Cannot find ${LOG_DIR} output directory"
    exit 1
fi

echo
echo "-- Log files of all tests can be found in ${LOG_DIR}"

function run_script () {
    echo
    echo "-- Running script for Python version ${PYVER}"
    bash -i ${SCRIPT} ${PYVER} > ${LOG_DIR}/${PYVER}_testrun.log 2>&1
    FAIL_COUNT=$(cat ${LOG_DIR}/${PYVER}_testrun.log | grep -c FAILED)
    if [[ "${FAIL_COUNT}" -gt 0 ]]; then
        echo "-- Test fail in Python ${PYVER} tests. Check ${LOG_DIR}/${PYVER}_testrun.log"
    fi
    PY_ERR_COUNT=$(cat ${LOG_DIR}/${PYVER}_testrun.log | grep -c Traceback)
    if [[ "${PY_ERR_COUNT}" -gt 0 ]]; then
        echo "-- Runtime error in Python ${PYVER} tests. Check ${LOG_DIR}/${PYVER}_testrun.log"
    fi
}

PYVER=3.9
run_script

PYVER=3.8
run_script

PYVER=3.7
run_script

PYVER=3.6
run_script

PYVER=3.5
run_script

echo
echo "-- Done"
