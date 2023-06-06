# Test case reports

nydok supports two different test report contents, a test case overview and a test case report.

## Test case overview

The test case overview provides a simple table of all the test cases, their description and PASS/FAIL status.

### Usage

You can create a test case overview by running the following command:

```bash
nydok report test-overview <args>
```


### Example

Test case | Description                           | Passed
--------- | ------------------------------------- | --------
TC001     | Test of some requirement              | Pass
TC002     | Test the failure status of test cases | **Fail**


## Test case report

The test case report provides more details for each test case, including the requirements tested and the test case implementation.

### Usage

You can create a test case overview by running the following command:

```bash
nydok report test-cases <args>
```


### Example

<h2>TC001 - Test of some requirement</h2>

ID    | Description
----- | ------------------------
UR001 | User requirement
FR001 | Functional requirement


<h3>Test case implementation:</h3>

```python
@testcase(["UR001", "FR001"])
def test_hello():
    assert True
```

