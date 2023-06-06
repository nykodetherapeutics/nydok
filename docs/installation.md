# Installation and usage

## Installation

nydok can be installed using from PyPI using pip:

`pip install nydok`

or using poetry:

`poetry add nydok --group dev`

Once installed it will register itself as a plugin to py.test automatically, along with installing the `nydok` command line tool for generating reports.

## Usage

Once installed, you can simply run `py.test` with the paths to your specification files and corresponding test case implementations:

```title="Usage example"
$ py.test \
    --nydok-output="nydok.json" \
    --nydok-risk-assessment="specifications/implementations/risk_assessment.yml" \
    specifications/

========================== test session starts ==========================
platform linux -- Python 3.8.10, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /project, configfile: pyproject.toml
plugins: nydok-0.2
collected 3 items

specifications/implementations/test_example_spec.py .             [ 33%]
specifications/definitions/example.spec.md ..                     [100%]

=========================== 3 passed in 0.02s ===========================
```

Next, you can use the `nydok` command line tool to generate reports from the output JSON file:

```title="CLI example"
$ nydok report traceability-matrix -o matrix.md nydok.json

```

See Reports and Configuration for more usage options.

!!! note
    nydok itself doesn't include functionality for generating the final reports. The output reports are meant to be included together with other reports you may have and then converted to HTML and/or PDF using additional software.
