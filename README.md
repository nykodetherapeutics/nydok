<div align="center">
    <img src="https://github.com/nykodetherapeutics/nydok/raw/main/docs/assets/nydok-logo.png" width="70%">
</div>

[![Main](https://github.com/nykodetherapeutics/nydok/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/nykodetherapeutics/nydok/actions/workflows/main.yml) [![PyPI version](https://badge.fury.io/py/nydok.svg)](https://badge.fury.io/py/nydok)

[Home page](https://nykodetherapeutics.github.io/nydok/) | [Getting started](https://nykodetherapeutics.github.io/nydok/intro/)

**nydok** is a combined specification writing and testing framework, for producing consistent and traceable specification documents. It is developed for Computerized Systems Validation in a GAMP 5 / GxP context, but is applicable to any software development process where traceability is important.

Write your requirements and risk assessment alongside your Python code, ensuring 1:1 mapping between requirements and the code you're writing.

It is implemented as a plugin for `py.test` for running the tests, combined with a CLI for creating reports.

## Features

Some notable features are:

- Lets you write specification documents including requirements as normal Markdown.
- Keeps track of which requirements are missing test cases.
- Supports a risk assessment process where you can link mitigations to your requirements.
- Can generate several types of reports in Markdown format for use in a Computerized System Validation process, such as:
    - Traceability matrix
    - Code review reports (Gitlab)
    - Risk assessment report
    - Test summary report
    - CI pipeline logs report (Gitlab)


## Installation


**Note!** nydok is still under development and hasn't yet had a v1.0.0 release, so expect breaking changes.


To install nydok using `pip`:

```
pip install nydok
```

or using Poetry:

```
poetry add nydok --group dev
```

## Usage

See documentation for details on how to use nydok, the following is just meant as a quick glimpse of how it works. nydok has a lot more features than what is shown here.

Create a `cowsay.spec.md` specification file:

```markdown
# Cowsay functional specification

## Functional requirements

- REQ001: The program must take as input a text string
- REQ002: The program must return a string with a cow in ASCII art, displaying the input text as a speech bubble
```

and a `test_cowsay.py` file:

```python
from nydok import testcase
import cowsay


@testcase(["REQ001", "REQ002"])
def test_cowsay():
    assert cowsay("Hello world") == """
     _____________
    < Hello world >
     -------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
    """

```

Next, run `py.test` to check the specification:

```
$ py.test --nydok-output nydok.json cowsay/
========================= test session starts =========================
platform linux -- Python 3.10.6, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /project
plugins: nydok-0.8.0
collected 3 items

cowsay/test_cowsay.py::test_cowsay PASSED                       [ 33%]
cowsay/cowsay.spec.md::REQ001 PASSED                            [ 66%]
cowsay/cowsay.spec.md::REQ002 PASSED                            [100%]

========================== 3 passed in 0.01s ==========================
```

Each requirement listed in the specification file is counted as a test item, and will pass or fail depending on it's test case.

Finally, run `nydok report` to generate reports.

As an example, to create a traceability matrix, run:

```
$ nydok report traceability-matrix nydok.json
```

to generate the following Markdown table:


ID     | Description                                                                                          | References | Test case
------ | ---------------------------------------------------------------------------------------------------- | ---------- | ---------
REQ001 | The program must take as input a text string                                                         |            | TC001
REQ002 | The program must return a string with a cow in ASCII art, displaying the input text as a speech bubble |            | TC001

## License

`nydok` is released under the MIT license. See [LICENSE](LICENSE) for details.
