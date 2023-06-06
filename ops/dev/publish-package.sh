#!/bin/bash -ue

poetry version "${VERSION}"
poetry build
poetry publish -u "${USERNAME}" -p "${PASSWORD}"