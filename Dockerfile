# Update peridically to latest specific tag
FROM ubuntu AS base-image

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# gettext-base -> envsubst
RUN apt-get update && apt-get install -y \
  git \
  wget \
  gawk \
  less \
  ripgrep \
  python3 \
  python3-pip \
  python3-venv \
  gettext-base \
  && rm -rf /var/lib/apt/lists/*

# Use normal user in container
RUN adduser --disabled-password --gecos '' dockeruser

RUN mkdir -p /software/bin && chown dockeruser -R /software

USER dockeruser
ENV PATH=/software/bin:$PATH

# Install Poetry, create venv and install Python production packages
COPY --chown=dockeruser poetry.lock pyproject.toml /software/
ENV PATH=/software/venv/bin:/home/dockeruser/.local/bin:$PATH \
  VIRTUAL_ENV=/software/venv
RUN pip3 install "poetry==1.5.0" && \
  python3 -m venv /software/venv && \
  /software/venv/bin/pip3 install pip=="22.3" && \
  cd /software && \
  poetry install --no-interaction --no-ansi --no-root

# To support running container as any UID, set $HOME explicitly
ENV HOME=/home/dockeruser

# Ensure any UID can read/write all relevant files
USER root
RUN chmod o+rwX -R /home /software
USER dockeruser

# Install git-cliff for changelog generation in CI
RUN cd /software/ && \
  wget https://github.com/orhun/git-cliff/releases/download/v0.5.0/git-cliff-0.5.0-x86_64-unknown-linux-gnu.tar.gz && \
  echo '4fecba7d764c193ff59bb3cc607782b90566950ef1b4ea74b7b9dfa879fed297 /software/git-cliff-0.5.0-x86_64-unknown-linux-gnu.tar.gz' | sha256sum -c && \
  tar -xvf git-cliff-0.5.0-x86_64-unknown-linux-gnu.tar.gz && \
  rm git-cliff-0.5.0-x86_64-unknown-linux-gnu.tar.gz && \
  cd bin && \
  ln -s ../git-cliff-0.5.0/git-cliff .

# Files are meant to be mounted in locally, don't copy in data as it can lead to confusion
WORKDIR /project

# Default user is root, container is meant to be run on rootless Docker and Github Actions
USER root
# We've added some software,
# ensure (again) any UID can read/write all relevant files
RUN chmod o+rwX -R /home /software

# Nicer prompt for shell in dev containers
RUN echo "PS1='[\[\e[31m\]\A\[\e[m\]] \[\e[33m\]\w\[\e[m\]: '" >> $HOME/.bashrc
