import re
from typing import Dict, List

import lxml.etree  # type: ignore
import pytest

from ..exception import FailedTestCaseException
from ..schema import TestCase

JUNIT_PATTERN = r"(?P<req_id>[A-Z,0-9]+)( \[(?P<refs>[A-Z,0-9]+)\])?: (?P<desc>.*)"


class JUnitFile(pytest.File):
    def collect(self):

        with open(self.fspath) as f:

            xml_data = lxml.etree.parse(f)
            testsuites = xml_data.getroot()

            pattern = re.compile(
                self.session.config.getoption("nydok-junit-regex")
                or self.session.config.getini("nydok-junit-regex")
                or JUNIT_PATTERN
            )

            for testsuite in testsuites.findall("testsuite"):
                testcases = testsuite.findall("testcase")

                # We allow several results for a testcase within a single testsuite
                # If there are no failures, we select the first test case.
                # If there are failures, we select the first failure.
                chosen_testcases: Dict[str, JUnitItem] = {}
                for testcase in testcases:

                    name = testcase.attrib["name"]
                    classname = testcase.attrib.get("classname", "")
                    # file = testcase.attrib.get("file", "")
                    # line_no = testcase.attrib.get("line", "")

                    failures: List[str] = []
                    for failure in testcase.findall("failure"):
                        failures.append(failure.text)

                    skipped: List[str] = []
                    for skip in testcase.findall("skipped"):
                        skipped.append(skip.text)

                    # testcase_data = {
                    #     "path": self.fspath,
                    #     "name": name,
                    #     "file": file,
                    #     "line_no": line_no,
                    #     "failures": failures,
                    #     "skipped": skipped,
                    # }

                    # Parse out references
                    for re_result in re.finditer(pattern, name):

                        matches = re_result.groupdict()
                        refs = []
                        if matches.get("refs"):
                            refs = matches["refs"].split(",")
                        test_case = TestCase(
                            matches["req_id"].split(","),
                            None,
                            matches.get("desc"),
                            None,
                            classname,
                            None,
                            refs,
                            False,
                            not bool(failures),
                        )
                        if name not in chosen_testcases or (
                            failures and not chosen_testcases[name].failures
                        ):
                            chosen_testcases[name] = JUnitItem.from_parent(
                                self, name=name, test_case=test_case, failures=failures
                            )

                yield from chosen_testcases.values()


class JUnitItem(pytest.Item):
    def __init__(
        self,
        name,
        parent,
        test_case: TestCase,
        failures: List[str],
    ):
        super().__init__(name, parent)
        self.test_case: TestCase = test_case
        self.failures: List[str] = failures

    def runtest(self):

        if not self.test_case.passed:
            raise FailedTestCaseException()

    def repr_failure(self, excinfo):
        """Called when self.runtest() raises an exception."""

        if isinstance(excinfo.value, FailedTestCaseException):
            return f"JUnit testcase '{self.test_case.desc}' is reported as failed: \n" + "\n".join(
                self.failures
            )

        return super().repr_failure(excinfo)

    def reportinfo(self):
        return self.fspath, None, f"JUnitTestCase: {self.name}"
