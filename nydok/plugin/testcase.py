"""The `@testcase` decorator, linking a Python test function to the requirements it tests."""

import functools
import inspect
from collections.abc import Callable
from typing import Any, TypeVar

from ..schema import TestCase

REQ_TESTCASE_TAG = "__req_testcase__"  # Attribute for storing metadata on the test functions

R = TypeVar("R")


def testcase(
    req_id: str | list[str],
    testcase_id: str | None = None,
    desc: str = "",
    io: list[tuple[Any, Any]] | tuple[Any, Any] | None = None,
    ref_ids: list[str] | None = None,
    skip: bool = False,
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """Register test case for a corresponding requirement.

    Test data handling:

    When providing test data using the `io=` argument,
    the input and expected output can be documented in the test report.

    Example:
        @testcase("FR001", "TC001",
            io=[
                ((2, 4), 6),
                ((3, 3), 6)
            ]
        )
        def test_sum(io=None):
            for i, e in io:
                assert sum(i) == e

    Args:
        req_id: Requirement id, or list of them.
        testcase_id: Override test case id. Default is to autogenerate one.
        desc: Description of the test case.
        io: Input/output test data in a tuple, or list of, (input, output).
        ref_ids: List of ids to other references. An id can be any string.
        skip: Whether checking test function result should be skipped. Defaults to False.

    """
    # A single (input, output) tuple becomes a list of one
    io_list = [io] if io and isinstance(io, tuple) else (None if io is None else list(io))
    if io_list:
        assert all(len(i) == 2 for i in io_list), "io argument must be list of tuples [(input, expected_output)]"

    req_ids = req_id if isinstance(req_id, list) else [req_id]

    def outer(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def inner(*args: object, **kwargs: object) -> R:
            # Add io arguments to function
            if io_list:
                kwargs["io"] = io_list
            return func(*args, **kwargs)

        setattr(
            inner,
            REQ_TESTCASE_TAG,
            TestCase(
                ids=req_ids,
                testcase_id=testcase_id,
                desc=desc,
                io=io_list,
                func_name=func.__name__,
                func_src=inspect.getsource(func),
                ref_ids=ref_ids,
                skip=skip,
                passed=False,
            ),
        )
        return inner

    return outer


testcase.__test__ = False  # type: ignore[attr-defined]
