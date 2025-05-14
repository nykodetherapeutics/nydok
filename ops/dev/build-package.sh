#!/bin/bash -ue

poetry version "${VERSION}"
poetry build
