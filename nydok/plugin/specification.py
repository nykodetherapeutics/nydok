"""Collection of requirements from specification files (`*.spec.md`)."""

import os
import re
from collections.abc import Iterator
from typing import TYPE_CHECKING

import pytest

from ..exception import (
    DuplicateRequirementException,
    FailedTestCaseException,
    MissingTestCaseException,
)
from ..patterns import DEFAULT_REQ_PATTERN
from ..schema import Requirement
from .options import get_option
from .specsmanager import specs_manager

if TYPE_CHECKING:
    from _pytest._code.code import TerminalRepr, TracebackStyle


class SpecFile(pytest.File):
    """A specification file, with one ReqItem per requirement."""

    def collect(self) -> Iterator["ReqItem"]:
        """Register each requirement matching the specification regex, and yield its ReqItem."""
        with open(self.path, encoding="utf-8") as f:
            md_data = f.read()

        pattern = re.compile(get_option(self.config, "nydok-specs-regex") or DEFAULT_REQ_PATTERN)
        for m in pattern.finditer(md_data):
            line_no = md_data.count("\n", 0, m.start(1)) + 1
            groups = m.groupdict()
            req = Requirement(
                id=groups["req_id"],
                desc=groups["desc"],
                file_path=self.path,
                line_no=line_no,
                ref_ids=groups["refs"].split(",") if groups.get("refs") else [],
            )
            specs_manager.add_requirement(req)
            yield ReqItem.from_parent(self, name=req.id, req=req)


class ReqItem(pytest.Item):
    """A requirement, passing if exactly one test case covers it and that test case passed."""

    def __init__(self, name: str, parent: pytest.Collector, req: Requirement) -> None:
        """Create the item for `req`."""
        super().__init__(name, parent)
        self.req = req
        # Earlier ReqItem with the same name, if any
        self.duplicate_item: ReqItem | None = None

    def runtest(self) -> None:
        """Fail if the requirement is duplicated, has no test case, or its test case failed."""
        if self.duplicate_item:
            raise DuplicateRequirementException()
        if not specs_manager.has_test_case(self.name):
            raise MissingTestCaseException()
        if not specs_manager.requirement_passed(self.name):
            raise FailedTestCaseException()

    def _func_name_suggestion(self) -> str:
        """Test function name from the first words of the description."""
        return "_".join(re.findall(r"\w+", self.req.desc.lower())[:8])

    def repr_failure(
        self, excinfo: pytest.ExceptionInfo[BaseException], style: "TracebackStyle | None" = None
    ) -> "str | TerminalRepr":
        """Describe why the item failed, with a test case template if it has none."""
        req_info = f"{self.name} ({self.req.file_path.resolve()}:{self.req.line_no})"

        if isinstance(excinfo.value, DuplicateRequirementException):
            assert self.duplicate_item
            first = self.duplicate_item.req
            req_duplicate_info = f"{self.name} ({first.file_path.resolve()}:{first.line_no})"
            return f"Requirement {req_info} is already defined in {req_duplicate_info}\n"

        if isinstance(excinfo.value, MissingTestCaseException):
            recipe = (
                f'@testcase("{self.name}")\n'
                f"def test_{self._func_name_suggestion()}():\n"
                f'    raise NotImplementedError("To be implemented")'
            )
            return f"Requirement {req_info} is missing test case: \n\n{recipe}\n"

        if isinstance(excinfo.value, FailedTestCaseException):
            return f"Requirement {req_info} test case failed. See corresponding test case for more details.\n"

        return super().repr_failure(excinfo, style)

    def reportinfo(self) -> tuple[os.PathLike[str] | str, int | None, str]:
        """Location and description of the item in pytest's report."""
        return self.path, self.req.line_no, f"RequirementTest: {self.name} {self.req.desc}"
