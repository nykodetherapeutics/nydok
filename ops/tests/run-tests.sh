#!/bin/bash -ue

SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BASEDIR="$SCRIPT_DIR/../.."

cd "$BASEDIR"
py.test -s --cov="nydok" \
    --ignore 'docs' \
    --ignore 'report.xml' \
    --nydok-risk-assessment="tests/risk_assessment.yml" \
    --junitxml=report.xml \
    --ignore coverage.xml \
    --ignore report.xml \
    tests $@

coverage xml
