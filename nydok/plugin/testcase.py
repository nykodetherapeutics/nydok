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
    """Register a test function as the test case of one or more requirements.

    Test data given with `io=` is passed to the test function as its `io` argument, and listed
    in the test case report.

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
        req_id: Requirement ID, or list of them.
        testcase_id: Test case ID. By default one is generated, e.g. "TC001".
        desc: Description of the test case.
        io: Test data: an (input, expected output) tuple, or a list of them.
        ref_ids: IDs of other references, e.g. risk assessments. An ID can be any string.
        skip: Don't number the test case, unless `testcase_id` is given. For test functions that
            only add metadata. Defaults to False.

    Returns:
        A decorator for the test function.
    """
    # A single (input, output) tuple becomes a list of one
    io_list = [io] if io and isinstance(io, tuple) else (None if io is None else list(io))
    if io_list:
        assert all(len(i) == 2 for i in io_list), "io argument must be list of tuples [(input, expected_output)]"

    req_ids = req_id if isinstance(req_id, list) else [req_id]

    def outer(func: Callable[..., R]) -> Callable[..., R]:
        """Attach the TestCase to the test function, wrapped to receive the `io` test data."""

        @functools.wraps(func)
        def inner(*args: object, **kwargs: object) -> R:
            """Call the test function, with the `io` test data if there is any."""
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
