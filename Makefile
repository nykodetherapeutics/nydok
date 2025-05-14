SHELL := /bin/bash

GIT_REF ?= $(shell git rev-parse --verify --short HEAD)
IMAGE_NAME ?= nydok_$(GIT_REF)-$(USER)

# If running in CI or rootless mode, use root inside the container, otherwise use the container user
DOCKER_USER ?= $(shell docker info 2>/dev/null | grep -q rootless && echo 0:0 || echo $(shell id -u):$(shell id -g) )
USE_TTY ?= $(shell if [ -t 0 ]; then echo "-it"; fi)

# For CI report generation
FROM_REF ?= $(shell git describe --abbrev=0 --tags $(shell git rev-parse HEAD^))
TO_REF ?= $(shell git rev-parse --short HEAD)
VERSION ?= $(TO_REF)

.PHONY: build test lint docs docs-serve shell build-package

build:
	docker build -t $(IMAGE_NAME) .

test: build
	docker run \
	--rm $(USE_TTY) \
	-v $(PWD):/project \
	-u $(DOCKER_USER) \
	$(IMAGE_NAME) \
	bash -c 'poetry install && ops/tests/run-tests.sh'

changelog: build
	docker run \
	--rm \
	-e FROM_REF=$(FROM_REF) \
	-e TO_REF=$(TO_REF) \
	-v $(PWD):/project \
	-v $(PWD)/.local/output:/output \
	-u $(DOCKER_USER) \
	$(IMAGE_NAME) \
	bash -c 'git-cliff -r /project ${FROM_REF}..${TO_REF} > changelog.md'

docs: build
	mkdir -p .local/output
	docker run \
	--rm $(USE_TTY) \
	-v $(PWD):/project \
	-v $(PWD)/.local/output:/output \
	-u $(DOCKER_USER) \
	$(IMAGE_NAME) \
	bash -c 'poetry install && /project/ops/docs/build.sh';

docs-serve: build
	docker run \
	--rm $(USE_TTY) \
	-it \
	-v $(PWD):/project \
	-p 8000-8100:8000 \
	-u $(DOCKER_USER) \
	$(IMAGE_NAME) \
	bash -c 'poetry install && /project/ops/docs/serve.sh';

lint: build
	docker run \
	--rm $(USE_TTY) \
	-v $(PWD):/project \
	-u $(DOCKER_USER) \
	$(IMAGE_NAME) \
	ops/tests/run-linting.sh

shell: build
	docker run -it \
	--rm \
	-v $(PWD):/project \
	-u $(DOCKER_USER) \
	$(IMAGE_NAME) \
	bash -c 'poetry install && bash'

build-package: build
	docker run \
	--rm $(USE_TTY) \
	-e VERSION \
	-e REPOSITORY \
	-e USERNAME \
	-e PASSWORD \
	-v $(PWD):/project \
	-u $(DOCKER_USER) \
	$(IMAGE_NAME) \
	ops/dev/build-package.sh
