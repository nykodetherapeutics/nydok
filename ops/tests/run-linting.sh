#!/bin/bash -ue

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASEDIR="$SCRIPT_DIR/../.."

CLR="\e[39m"
GREEN="\e[32m"
RED="\e[31m"


HAS_ERROR=0

# Black
if BLACK_OUTPUT=$(black --check "$BASEDIR" 2>&1 ); then
    echo -e "${GREEN}PASSED: Black${CLR}"
else
    echo -e "${BLACK_OUTPUT}"
    echo -e "${RED}FAILED: Black${CLR}"
    HAS_ERROR=1
fi

# flake8
if FLAKE_OUTPUT=$(flake8 "$BASEDIR" 2>&1 ); then
    echo -e "${GREEN}PASSED: flake8${CLR}"
else
    echo -e "${FLAKE_OUTPUT}"
    echo -e "${RED}FAILED: flake8${CLR}"
    HAS_ERROR=1
fi

# mypy
if MYPY_OUTPUT=$(mypy "$BASEDIR" --exclude "docs/" 2>&1 ); then
    echo -e "${GREEN}PASSED: mypy${CLR}"
else
    echo -e "${MYPY_OUTPUT}"
    echo -e "${RED}FAILED: mypy${CLR}"
    HAS_ERROR=1
fi


if [ $HAS_ERROR -eq 1 ]; then
    exit 1
fi
