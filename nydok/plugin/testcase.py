import functools
import inspect
from typing import Any, Callable, List, Tuple, Union

from ..schema import TestCase

REQ_TESTCASE_TAG = "__req_testcase__"  # Attribute for storing metadata on the test functions


def testcase(
    req_id: Union[str, List[str]],
    testcase_id: str = None,
    desc: str = "",
    io: List[Tuple[Any, Any]] = None,
    ref_ids: List[str] = None,
    skip=False,
) -> Callable:
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
        req_id: Requirement id.
        testcase_id: Override test case id. Default is to autogenerate one.
        io: Input/output test data in a tuple, or list of, (input, output).
        ref_ids: List of ids to other references. An id can be any string.
        skip: Whether checking test function result should be skipped. Defaults to False.

    """

    if io:
        if isinstance(io, tuple):
            io = [io]
        assert all(
            len(i) == 2 for i in io
        ), "io argument must be list of tuples [(input, expected_output)]"

    if not isinstance(req_id, list):
        req_id = [req_id]

    def outer(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):

            # TODO: Check that func is a py.test function (test_)

            # Add io arguments to function
            if io:
                kwargs["io"] = io
            return func(*args, **kwargs)

        setattr(
            inner,
            REQ_TESTCASE_TAG,
            TestCase(
                req_id,
                testcase_id,
                desc,
                io,
                func.__name__,
                inspect.getsource(func),
                ref_ids,
                skip,
                False,
            ),
        )
        return inner

    return outer


testcase.__test__ = False  # type: ignore
