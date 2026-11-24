"""Collection of test results from JUnit XML files (`*.junit.xml`)."""

import os
import re
from collections.abc import Iterator
from typing import TYPE_CHECKING

import lxml.etree  # type: ignore
import pytest

from ..exception import FailedTestCaseException
from ..patterns import JUNIT_PATTERN
from ..schema import TestCase
from .options import get_option

if TYPE_CHECKING:
    from _pytest._code.code import TerminalRepr, TracebackStyle


class JUnitFile(pytest.File):
    """A JUnit XML file, with one JUnitItem per test case whose name matches the JUnit regex."""

    def collect(self) -> Iterator["JUnitItem"]:
        """Yield a JUnitItem per test case name in each test suite."""
        # Binary, so lxml decodes with the file's declared encoding rather than the locale's
        with open(self.path, "rb") as f:
            root = lxml.etree.parse(f).getroot()
        # The root is <testsuites>, or a single <testsuite> in some reporters' output
        testsuites = [root] if root.tag == "testsuite" else root.findall("testsuite")

        pattern = re.compile(get_option(self.config, "nydok-junit-regex") or JUNIT_PATTERN)

        for testsuite in testsuites:
            # A test suite may report the same test case several times. The first failing one
            # is used, or the first one if none fail.
            chosen_testcases: dict[str, JUnitItem] = {}
            for testcase in testsuite.findall("testcase"):
                name = testcase.attrib["name"]
                classname = testcase.attrib.get("classname", "")

                # <error> is a test that crashed, so it fails like a <failure>.
                # Either may have only a message attribute and no text.
                failures: list[str] = [
                    failure.text or failure.get("message") or ""
                    for failure in [*testcase.findall("failure"), *testcase.findall("error")]
                ]

                for match in pattern.finditer(name):
                    groups = match.groupdict()
                    test_case = TestCase(
                        ids=groups["req_id"].split(","),
                        testcase_id=None,
                        desc=groups.get("desc") or "",
                        io=None,
                        func_name=classname,
                        func_src=None,
                        ref_ids=groups["refs"].split(",") if groups.get("refs") else [],
                        skip=False,
                        passed=not failures,
                    )
                    if name not in chosen_testcases or (failures and not chosen_testcases[name].failures):
                        chosen_testcases[name] = JUnitItem.from_parent(
                            self, name=name, test_case=test_case, failures=failures
                        )

            yield from chosen_testcases.values()


class JUnitItem(pytest.Item):
    """A test case from a JUnit file, failing if the file reports it as failed."""

    def __init__(
        self,
        name: str,
        parent: pytest.Collector,
        test_case: TestCase,
        failures: list[str],
    ) -> None:
        """Create the item for `test_case`, with the texts of its failures and errors."""
        super().__init__(name, parent)
        self.test_case = test_case
        self.failures = failures

    def runtest(self) -> None:
        """Fail if the JUnit file reports the test case as failed."""
        if not self.test_case.passed:
            raise FailedTestCaseException()

    def repr_failure(
        self, excinfo: pytest.ExceptionInfo[BaseException], style: "TracebackStyle | None" = None
    ) -> "str | TerminalRepr":
        """Describe why the item failed."""
        if isinstance(excinfo.value, FailedTestCaseException):
            return f"JUnit testcase '{self.test_case.desc}' is reported as failed: \n" + "\n".join(self.failures)
        return super().repr_failure(excinfo, style)

    def reportinfo(self) -> tuple[os.PathLike[str] | str, int | None, str]:
        """Location and description of the item in pytest's report."""
        return self.path, None, f"JUnitTestCase: {self.name}"
