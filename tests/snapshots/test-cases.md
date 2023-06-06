## TC001

ID    | Description             
----- | ------------------------
UR001 | User specification      
FR001 | Functional specification


### Test case implementation:

```python
@testcase(["UR001", "FR001"])
def test_hello():
    assert True
```

## TC002: Test failure status and description

ID    | Description
----- | -----------
FR002 | I will fail


### Test case implementation:

```python
@testcase(
    ["FR002"],
    desc="Test failure status and description"
)
def test_failure():
    assert False
```

