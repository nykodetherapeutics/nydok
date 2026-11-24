"""Registry of the requirements, test cases and risk assessments found in one pytest run."""

import json
from pathlib import Path

import yaml

from ..exception import (
    DuplicateRequirementException,
    RiskPriorityExceedsThresholdException,
)
from ..schema import (
    RISK_ASSESSMENT_CATEGORIES,
    DataclassJsonEncoder,
    Requirement,
    RiskAssessment,
    TestCase,
)


class SpecsManager:
    """Links requirements to their test cases, numbers test cases, and writes the results JSON."""

    def __init__(self) -> None:
        """Create an empty registry."""
        self.test_cases: dict[str, TestCase] = {}
        self.requirements: dict[str, Requirement] = {}
        self.testcase_prefix = "TC"
        self.testcase_no = 1
        self.risk_assessments: dict[str, RiskAssessment] = {}

    def enable_risk_assessment(self, path: str) -> None:
        """Load the risk assessments from the YAML file at `path`."""
        with open(path, encoding="utf-8") as file:
            for _id, risk in yaml.safe_load(file).items():
                self.risk_assessments[_id] = RiskAssessment.from_dict(_id, risk)

    def _format_testcase_id(self) -> str:
        return f"{self.testcase_prefix}{self.testcase_no:03}"

    def add_requirement(self, req: Requirement) -> None:
        """Register a requirement."""
        self.requirements[req.id] = req

    def _add_test_case(self, req_id: str, test_case: TestCase) -> None:
        if req_id in self.test_cases:
            existing = self.test_cases[req_id]
            raise DuplicateRequirementException(f"TestCase for id {req_id} is already added by {existing.func_name}.")
        self.test_cases[req_id] = test_case

    def add_test_case(self, test_case: TestCase) -> None:
        """Register a test case for each requirement it covers, numbering it unless it has an ID or is skip."""
        if not test_case.skip and not test_case.testcase_id:
            test_case.testcase_id = self._format_testcase_id()
            self.testcase_no += 1

        for _id in test_case.ids:
            self._add_test_case(_id, test_case)

    def has_test_case(self, req_id: str) -> bool:
        """Whether a test case covers requirement `req_id`."""
        return req_id in self.test_cases

    def requirement_passed(self, req_id: str) -> bool:
        """Whether the test case covering requirement `req_id` passed."""
        return self.test_cases[req_id].passed

    def check_risk_assessment(self, permissible_risk_priority: str) -> None:
        """Raise if a residual risk priority exceeds the threshold or a mitigation requirement is unknown."""
        for ra_id, ra in self.risk_assessments.items():
            if RISK_ASSESSMENT_CATEGORIES.index(ra.residual_risk_priority) > RISK_ASSESSMENT_CATEGORIES.index(
                permissible_risk_priority
            ):
                raise RiskPriorityExceedsThresholdException(
                    f"Risk assessment {ra_id}: Residual risk "
                    f"priority '{ra.residual_risk_priority}' "
                    f"exceeds permissable risk priority '{permissible_risk_priority}'."
                )

            # Check requirement ids
            for req_id in ra.mitigation_requirement_ids:
                if req_id not in self.requirements:
                    raise ValueError(f"Risk assessment {ra_id}: mitigation_requirement_id '{req_id}' not found.")

    def to_json(self, path: Path) -> None:
        """Write the requirements, test cases and risk assessments to `path` as JSON."""
        data = json.dumps(
            {
                "test_cases": self.test_cases,
                "requirements": self.requirements,
                "risk_assessments": self.risk_assessments,
            },
            cls=DataclassJsonEncoder,
            indent=4,
        )
        path.write_text(data, encoding="utf-8")


specs_manager = SpecsManager()
