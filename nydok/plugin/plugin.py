"""nydok's pytest hooks, registered through the `pytest11` entry point."""

from collections.abc import Generator
from pathlib import Path

import pytest

from ..patterns import DEFAULT_REQ_PATTERN, JUNIT_PATTERN
from ..schema import TestCase
from .junit import JUnitFile, JUnitItem
from .options import get_option
from .specification import ReqItem, SpecFile
from .specsmanager import specs_manager
from .testcase import REQ_TESTCASE_TAG


# Pytest lifecycle hooks, in order of occurrence:
def pytest_addoption(parser: pytest.Parser) -> None:
    """Register nydok's settings, each as a command line option and an ini setting."""
    group = parser.getgroup("nydok", "Specification testing")

    def add_opt_ini(opt_name: str, help_text: str) -> None:
        group.addoption(f"--{opt_name}", dest=opt_name, help=help_text, type=str)
        parser.addini(opt_name, help_text, type="string")

    add_opt_ini("nydok-specs-regex", f"Regex for specification parsing. Default: '{DEFAULT_REQ_PATTERN}'")
    add_opt_ini("nydok-junit-regex", f"Regex for JUnit name parsing. Default: '{JUNIT_PATTERN}'")
    add_opt_ini("nydok-risk-assessment", "Input path for risk assessment.")
    add_opt_ini("nydok-risk-priority-threshold", "Threshold for risk priority. Default: 'low'")
    add_opt_ini("nydok-output", "Path for nydok json results file.")


def pytest_configure(config: pytest.Config) -> None:
    """Load the risk assessment, if one is given."""
    if ra_file := get_option(config, "nydok-risk-assessment"):
        specs_manager.enable_risk_assessment(ra_file)


def pytest_collect_file(parent: pytest.Collector, file_path: Path) -> pytest.Collector | None:
    """Collect specification files and JUnit result files."""
    if file_path.name.endswith(".spec.md"):
        return SpecFile.from_parent(parent, path=file_path)
    if file_path.name.endswith(".junit.xml"):
        return JUnitFile.from_parent(parent, path=file_path)
    return None


def _testcase_of(item: pytest.Item) -> TestCase | None:
    """Return the TestCase that `@testcase` attached to a Python test function, if any."""
    if isinstance(item, pytest.Function):
        return getattr(item.function, REQ_TESTCASE_TAG, None)
    return None


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item: pytest.Item) -> Generator[None, object, object]:
    """Register each test's TestCase, and mark a Python test's TestCase passed if it passes."""
    test_case = item.test_case if isinstance(item, JUnitItem) else _testcase_of(item)
    if test_case:
        specs_manager.add_test_case(test_case)

    # Raises if the test fails, leaving `passed` False
    result = yield

    if py_test_case := _testcase_of(item):
        py_test_case.passed = True
    return result


def pytest_collection_finish(session: pytest.Session) -> None:
    """Run ReqItems last, mark duplicated requirements and check the risk assessment.

    ReqItems must run after the tests that register their test cases. Sorting here rather than in
    pytest_collection_modifyitems runs it after the reordering done by --lf/--ff/--nf, which wrap
    that hook.
    """

    def sort_req_last(item: pytest.Item) -> int:
        # Other items (e.g. JUnitItems) first, then Python test functions, then ReqItems
        if isinstance(item, ReqItem):
            return 2
        if isinstance(item, pytest.Function):
            return 1
        return 0

    session.items = sorted(session.items, key=sort_req_last)

    seen_names: dict[str, ReqItem] = {}
    for req_item in (i for i in session.items if isinstance(i, ReqItem)):
        if req_item.name in seen_names:
            req_item.duplicate_item = seen_names[req_item.name]
        seen_names[req_item.name] = req_item

    # Ensure that all risk assessments' risk priority are within the specified threshold
    permissible_risk_priority = get_option(session.config, "nydok-risk-priority-threshold") or "low"
    specs_manager.check_risk_assessment(permissible_risk_priority)


@pytest.hookimpl(tryfirst=True, wrapper=True)
def pytest_sessionfinish(session: pytest.Session) -> Generator[None, object, object]:
    """Write the results to the JSON file given by `nydok-output`, if any."""
    result = yield
    if output := get_option(session.config, "nydok-output"):
        specs_manager.to_json(Path(output))
    return result
