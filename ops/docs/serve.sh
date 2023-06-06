#!/bin/bash -ue

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASEDIR="$SCRIPT_DIR/../.."

pushd "${BASEDIR}" > /dev/null
mkdocs serve -a 0.0.0.0:8000
popd