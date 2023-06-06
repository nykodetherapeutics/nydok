# Overview


## Concepts

nydok introduces a few concepts, outlined below, that are useful to know to get a picture of how to use it.

``` mermaid
graph LR
  subgraph External documents
    DOC1[Document 1];
  end
  subgraph Risk Assessment
    RA1[Risk assessment 1];
    RA2[Risk assessment 2];
  end
  subgraph Specification
    R1[Requirement 1];
    R2[Requirement 2];
    R3[Requirement 3];
  end
  subgraph Code tests
    TC1[Test case 1];
    TC2[Test case 2];
  end

  R1 --> TC1;
  R2 --> TC1;
  R3 --> TC2;

  RA1 --> R1;
  RA2 --> R2;
  RA2 --> R3;
  R3 --> DOC1;

```



### Specification

A Markdown document, containing specification documentation and one or more `Requirement`s.

### Requirement

A line within a `Specification` document given in a specific format. Registers a requirement in nydok, letting you keep track of your requirements, their references to other requirements and any test cases testing the implementation of the requirement.

A `Requirement` may include the following information:

- Requirement ID
- References
- Description

An example `Requirement` could look like the following:

```
- FUNC001: Requirement description.
```

### Test case

A test case checking the implementation of a `Requirement`. Normally written as a py.test test, but can also come from external sources.

A `Test case` may include the following information and more:

- Test case ID
- One or more requirements IDs
- Description
- Example input data and expected output data
- References

An example `Test case` implementing a test case for two `Requirement`s could look like the following:

```python
@testcase(
  ["FUNC001", "FUNC002"],
  desc="Testing something",
)
def test_something():
    ...

```


## Running the tests

Since nydok utilizes py.test, each `Requirement` counts as a test item in py.test. The specification files are therefore handled like a test source, yielding a set of test items. Running a py.test session with one specification file with corresponding test cases will therefore look something like the following:

```
============================= test session starts ==============================
platform linux -- Python 3.8.10, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: /project
plugins: nydok-0.0
collected 13 items
tests/test_urs_spec.py ..                                                [ 50%]
tests/urs.spec.md ...........                                            [100%]
============================ 13 passed in 12.40s ==============================
```

Here two test cases in `test_urs_spec.py` together refers to the 11 requirements in `urs.spec.md`, in this particular example acting as end-to-end tests for the application given the high-level of requirements in a user requirement specification.

## How to structure your tests

Since nydok is a py.test plugin, it utilizes py.test's collection of tests to scan for both requirements and tests. You can therefore either put the specification files in one directory and test cases in another, or mix them both in the same directory, as long as you provide all relevant paths when running py.test.

One suggested structure is the following, but what's best will likely depend on the surrounding tooling:

```
specifications/
    definitions/
        mymodule.spec.md
    implementations/
        test_mymodule.py
```
