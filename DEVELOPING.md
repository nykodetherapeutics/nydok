# Development guidelines

## Project outline

Project development is centered around using Docker containers.

There's also a `Makefile` meant to ease some common tasks related to development and CI. Take a look in the `Makefile` for some pointers on available commands.

Using Visual Studio Code is the main supported method for development on the project. That being said, it's entirely possible to develop using other software.

### Development using VSCode

The project has a preconfigued `.devcontainer`. If you open the project in VSCode, it will ask you to open it inside the devcontainer. All related extensions and configurations should then be ready and pre-configured.

### Development using other tools

Developing using other tools is possible, but you'll have to configure linters, formatters and related tools yourself.

### Formatting and linting

- The project is using [black](https://github.com/psf/black) for auto-formatting.
- Linting is handled by `flake8` in CI and `Pylance` if using VSCode.

### Type checking

The project is type-checked by `mypy` by default if using VSCode.

### Shell access

To get a shell in a *new* development container, run

`make shell`

Note that if you're using VSCode, this will not be the same container that VSCode is using. Open a new terminal inside VSCode to access that same container.

## Testing

### Unit testing

Unit tests should be located next to the relevant source code, inside a `tests` folder.

Example:

```
├── client.py
├── parser.py
└── tests
    ├── test_client.py
    └── test_parser.py
```

Unit tests are executed using [py.test](https://docs.pytest.org/) runner.

To run the tests, you have multiple options:

- Use the integrated `Test explorer` inside VSCode
- Run the tests manually in a new container: `make test`
- Run the tests inside an existing container: `ops/tests/run-tests.sh`
- Run py.test yourself if you want to e.g. only run a specific test or change other options: `py.test -s -k function_i_want_to_test src/` (inside container)
- Use CI to execute the tests by pushing the code to your branch. It will also provide test coverage information.

## Documentation

The project uses [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) for documentation.


### Building

All documentation is located in the `docs/` folder. To build the documentation you can run:

`make docs`

This will both generate the HTML site for publishing and a PDF of the documentation.

### Developing

For development, you can start the MkDocs development server:

`make docs-serve`

It will start a server on an available port, which lets you open the documentation in a local browser. Any changes you make to the documentation code will be instantly updated in the browser.

To find out which port you should connect to on the host, you can use `docker ps` and locate the container that is running.
