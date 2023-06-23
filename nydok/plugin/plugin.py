import re
from pathlib import Path
from typing import Dict

import pytest

from .junit import JUNIT_PATTERN, JUnitFile, JUnitItem
from .specification import DEFAULT_REQ_PATTERN, ReqItem, SpecFile
from .specsmanager import specs_manager
from .testcase import REQ_TESTCASE_TAG

RE_NEW_LINE = re.compile(r"\n")


def _get_option_or_ini(config, setting, default=None):
    return config.getoption(setting) or config.getini(setting) or default


# Pytest lifecycle hooks, in order of occurrence:
def pytest_addoption(parser):
    """Pytest specific hook that is triggered upon setting up the command argument parser."""
    group = parser.getgroup("nydok", "Specification testing")

    def add_opt_ini(opt_name: str, help: str):
        group.addoption(f"--{opt_name}", dest=opt_name, help=help, type=str)
        parser.addini(opt_name, help, type="string")

    add_opt_ini(
        "nydok-specs-regex", f"Regex for specification parsing. Default: '{DEFAULT_REQ_PATTERN}'"
    )
    add_opt_ini("nydok-junit-regex", f"Regex for JUnit name parsing. Default: '{JUNIT_PATTERN}'")
    add_opt_ini("nydok-risk-assessment", "Input path for risk assessment.")
    add_opt_ini("nydok-risk-priority-threshold", "Threshold for risk priority. Default: 'low'")
    add_opt_ini("nydok-output", "Path for nydok json results file.")


def pytest_configure(config):
    """Pytest specific hook that is triggered after options are parsed."""
    if ra_file := _get_option_or_ini(config, "nydok-risk-assessment"):
        specs_manager.enable_risk_assessment(ra_file)


def pytest_collect_file(parent, path):
    """Pytest specific hook that is triggered for evaluating inclusion of a file in the tests."""
    if str(path).endswith(".spec.md"):
        return SpecFile.from_parent(parent, fspath=path)

    if str(path).endswith(".junit.xml"):
        return JUnitFile.from_parent(parent, fspath=path)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item):
    """Pytest specific hook that is triggered for each test being run."""

    def is_pytest_with_testcase(item):
        return isinstance(item, pytest.Function) and hasattr(item.function, REQ_TESTCASE_TAG)

    test_case = None

    if isinstance(item, JUnitItem):
        test_case = item.test_case
    elif is_pytest_with_testcase(item):
        test_case = getattr(item.function, REQ_TESTCASE_TAG)

    if test_case:
        specs_manager.add_test_case(test_case)

    # Run the test
    result = yield

    # Update TestCase.passed if the test passed
    if is_pytest_with_testcase(item) and not result.excinfo:
        test_case.passed = True


def pytest_collection_finish(session):
    """Runs after py.test is done collecting test Items.

    We need to ensure that all ReqItems runs last,
    in order to make sure that corresponding TestCaseItems can be found.
    """

    def sort_req_last(item):
        # Sort function for sorting ReqItems last,
        # with the Python functions next.
        # Any other items are run first.
        if isinstance(item, ReqItem):
            return 2
        if isinstance(item, pytest.Function):
            return 1
        return 0

    session.items = sorted(session.items, key=sort_req_last)

    req_items = [i for i in session.items if isinstance(i, ReqItem)]
    seen_names: Dict[str, ReqItem] = dict()
    for req_item in req_items:
        if req_item.name in seen_names:
            req_item.duplicate_item = seen_names[req_item.name]
        seen_names[req_item.name] = req_item

    # Ensure that all risk assessments' risk priority are within the specified threshold
    permissable_risk_priority = _get_option_or_ini(
        session.config, "nydok-risk-priority-threshold", default="low"
    )
    specs_manager.check_risk_assessment(permissable_risk_priority)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_sessionfinish(session):
    """Pytest specific hook that is triggered as the pytest session is complete."""

    outcome = yield
    outcome.get_result()

    # Optionally write the results to a file
    if output := _get_option_or_ini(session.config, "nydok-output"):
        specs_manager.to_json(Path(output))
