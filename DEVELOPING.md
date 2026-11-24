# Development guidelines

## Project outline

Project development is centered around using Docker containers.

There's also a `Makefile` meant to ease some common tasks related to development and CI. Take a look in the `Makefile` for some pointers on available commands.

Using Visual Studio Code is the main supported method for development on the project. That being said, it's entirely possible to develop using other software.

### Development using VSCode

The project has a preconfigued `.devcontainer`. If you open the project in VSCode, it will ask you to open it inside the devcontainer. All related extensions and configurations should then be ready and pre-configured.

### Development using other tools

Developing using other tools is possible, but you'll have to configure linters, formatters and related tools yourself.

### Formatting, linting and type checking

- [ruff](https://docs.astral.sh/ruff/) formats and lints the code; see `ruff.toml`. The tests are formatted but not linted.
- [mypy](https://mypy.readthedocs.io/) type-checks `nydok/`.
- `make lint` (or `ops/tests/run-linting.sh` inside a container) runs all three, as CI does.

### Python versions

nydok supports Python 3.10 and newer: HPVSpot, its main user, runs it on 3.10. The image uses Python 3.14 by default; set `PYTHON_VERSION` to use another, e.g. `make test PYTHON_VERSION=3.10`. CI runs the lint and tests on both.

### Shell access

To get a shell in a *new* development container, run

`make shell`

Note that if you're using VSCode, this will not be the same container that VSCode is using. Open a new terminal inside VSCode to access that same container.

## Testing

### Tests

nydok is tested with itself: the tests in `tests/` are `@testcase`s for the requirements in `tests/*.spec.md`, nydok's specification (also published in the documentation). A new test needs a requirement in a spec file, and the reports' output is compared with `tests/snapshots/`.

To run the tests, you have multiple options:

- Use the integrated `Test explorer` inside VSCode
- Run the tests manually in a new container: `make test`
- Run the tests inside an existing container: `ops/tests/run-tests.sh`
- Run pytest yourself, e.g. to run only some tests: `pytest -s -k function_i_want_to_test` (inside container)
- Use CI to execute the tests by pushing the code to your branch. It will also provide test coverage information.

## Documentation

The project uses [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) for documentation.


### Building

All documentation is located in the `docs/` folder. To build the documentation you can run:

`make docs`

This generates the HTML site in `.local/output/docs`.

### Developing

For development, you can start the MkDocs development server:

`make docs-serve`

It will start a server on an available port, which lets you open the documentation in a local browser. Any changes you make to the documentation code will be instantly updated in the browser.

To find out which port you should connect to on the host, you can use `docker ps` and locate the container that is running.

## Releases

Pushing a tag `vX.Y.Z` builds the package, publishes it to PyPI and creates a GitHub release. The release notes are made by [git-cliff](https://git-cliff.org/) (`make changelog`, with its default configuration) from the commit messages since the previous tag. Only [conventional commits](https://www.conventionalcommits.org/) (e.g. `fix: ...`, `chore: ...`, `ci: ...`) are included.
