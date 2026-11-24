# CI builds this with the oldest supported Python (HPVSpot's) and the newest
ARG PYTHON_VERSION=3.14
FROM python:${PYTHON_VERSION}-slim-trixie AS base-image

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
  git \
  curl \
  less \
  && rm -rf /var/lib/apt/lists/*

# Use normal user in container
RUN adduser --disabled-password --gecos '' dockeruser

RUN mkdir -p /software/bin && chown dockeruser -R /software

USER dockeruser
ENV PATH=/software/venv/bin:/software/bin:$PATH \
  VIRTUAL_ENV=/software/venv

# Poetry in its own venv; the project's packages go in /software/venv
ARG POETRY_VERSION=2.5.2
RUN python3 -m venv /software/poetry && \
  /software/poetry/bin/pip install --no-cache-dir "poetry==${POETRY_VERSION}" && \
  ln -s /software/poetry/bin/poetry /software/bin/poetry

COPY --chown=dockeruser poetry.lock pyproject.toml /software/
RUN python3 -m venv /software/venv && \
  cd /software && \
  poetry install --no-interaction --no-ansi --no-root --all-extras

# git-cliff for changelog generation in CI
ARG GIT_CLIFF_VERSION=2.14.2
ARG GIT_CLIFF_SHA256=24f397c733add5390fdceee3a2088588ab0d5f944ce00d34cb7029b888cf2db4
RUN cd /software && \
  curl -sSLO "https://github.com/orhun/git-cliff/releases/download/v${GIT_CLIFF_VERSION}/git-cliff-${GIT_CLIFF_VERSION}-x86_64-unknown-linux-gnu.tar.gz" && \
  echo "${GIT_CLIFF_SHA256}  git-cliff-${GIT_CLIFF_VERSION}-x86_64-unknown-linux-gnu.tar.gz" | sha256sum -c && \
  tar -xzf "git-cliff-${GIT_CLIFF_VERSION}-x86_64-unknown-linux-gnu.tar.gz" && \
  rm "git-cliff-${GIT_CLIFF_VERSION}-x86_64-unknown-linux-gnu.tar.gz" && \
  ln -s "../git-cliff-${GIT_CLIFF_VERSION}/git-cliff" bin/git-cliff

# To support running container as any UID, set $HOME explicitly
ENV HOME=/home/dockeruser

# Files are meant to be mounted in locally, don't copy in data as it can lead to confusion
WORKDIR /project

# Default user is root, container is meant to be run on rootless Docker and Github Actions
USER root

# Nicer prompt for shell in dev containers
RUN echo "PS1='[\[\e[31m\]\A\[\e[m\]] \[\e[33m\]\w\[\e[m\]: '" >> $HOME/.bashrc
