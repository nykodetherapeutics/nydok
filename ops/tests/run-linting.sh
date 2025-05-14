#!/bin/bash -ue

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASEDIR="$SCRIPT_DIR/../.."

CLR="\e[39m"
GREEN="\e[32m"
RED="\e[31m"


HAS_ERROR=0

# ruff format
if RUFF_FORMAT_CHECK_OUTPUT=$(ruff format --check "$BASEDIR" 2>&1 ); then
    echo -e "${GREEN}PASSED: ruff format${CLR}"
else
    echo -e "${RUFF_FORMAT_CHECK_OUTPUT}"
    echo -e "${RED}FAILED: ruff format${CLR}"
    HAS_ERROR=1
fi

# ruff lint
if RUFF_CHECK_OUTPUT=$(ruff check "$BASEDIR" 2>&1 ); then
    echo -e "${GREEN}PASSED: ruff lint${CLR}"
else
    echo -e "${RUFF_CHECK_OUTPUT}"
    echo -e "${RED}FAILED: ruff lint${CLR}"
    HAS_ERROR=1
fi

# mypy
if MYPY_OUTPUT=$(mypy "$BASEDIR/nydok" 2>&1 ); then
    echo -e "${GREEN}PASSED: mypy${CLR}"
else
    echo -e "${MYPY_OUTPUT}"
    echo -e "${RED}FAILED: mypy${CLR}"
    HAS_ERROR=1
fi


if [ $HAS_ERROR -eq 1 ]; then
    exit 1
fi
