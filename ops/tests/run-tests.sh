#!/bin/bash -ue

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASEDIR="$SCRIPT_DIR/../.."

cd "$BASEDIR"
pytest -s --cov="nydok" \
    --nydok-risk-assessment="tests/risk_assessment.yml" \
    --junitxml=report.xml \
    tests "$@"

coverage xml
