import re
from pathlib import Path
from typing import Optional

import pytest

from ..exception import (
    DuplicateRequirementException,
    FailedTestCaseException,
    MissingTestCaseException,
)
from ..schema import Requirement
from .specsmanager import specs_manager

DEFAULT_REQ_PATTERN = r"- (?P<req_id>[A-Z]+[0-9]+)( \[(?P<refs>[A-Z,0-9]+)\])?: (?P<desc>.*)"

RE_NEW_LINE = re.compile(r"\n")


class SpecFile(pytest.File):
    def collect(self):

        with open(self.fspath) as f:
            md_data = f.read()

        # Get regex to use
        req_regex = (
            self.config.getoption("nydok-specs-regex")
            or self.config.getini("nydok-specs-regex")
            or DEFAULT_REQ_PATTERN
        )

        # Parse out all requirements from file, and yield py.test Items
        pattern = re.compile(req_regex)
        for m in pattern.finditer(md_data):
            line_no = len(RE_NEW_LINE.findall(md_data, 0, m.start(1))) + 1
            matches = m.groupdict()
            req_id, desc = matches["req_id"], matches["desc"]
            refs = []
            if matches.get("refs"):
                refs = matches["refs"].split(",")
            req = Requirement(req_id, desc, Path(self.fspath), line_no, refs)
            specs_manager.add_requirement(req)
            yield ReqItem.from_parent(self, name=req_id, req=req)


class ReqItem(pytest.Item):
    def __init__(self, name, parent, req: Requirement):
        super().__init__(name, parent)
        self.req: Requirement = req
        self.duplicate_item: Optional[
            pytest.Item
        ] = None  # If there are duplicated Items with same name

    def runtest(self):

        if self.duplicate_item:
            raise DuplicateRequirementException()
        if not specs_manager.has_test_case(self.name):
            raise MissingTestCaseException()
        if not specs_manager.requirement_passed(self.name):
            raise FailedTestCaseException()

    def _func_name_suggestion(self):
        return "_".join(self.req.desc.lower().split(" ")[:8])

    def repr_failure(self, excinfo):
        """Called when self.runtest() raises an exception."""
        req_info = f"{self.name} ({self.req.file_path.resolve()}:{self.req.line_no})"

        if isinstance(excinfo.value, DuplicateRequirementException):
            req_duplicate_info = f"{self.name} ({self.req.file_path}:{self.req.line_no})"
            return f"Requirement {req_info} is already defined in {req_duplicate_info}\n"

        if isinstance(excinfo.value, MissingTestCaseException):
            receipe = (
                f'@testcase("{self.name}")\n'
                f"def test_{self._func_name_suggestion()}():\n"
                f'    raise NotImplementedError("To be implemented")'
            )
            return f"Requirement {req_info} is missing test case: \n\n{receipe}\n"

        if isinstance(excinfo.value, FailedTestCaseException):
            return (
                f"Requirement {req_info} test case failed. "
                "See corresponding test case for more details.\n"
            )

        return super().repr_failure(excinfo)

    def reportinfo(self):
        return self.fspath, self.req.line_no, f"RequirementTest: {self.name} {self.req.desc}"
