import json
from pathlib import Path
from typing import Dict

import yaml

from ..exception import (
    DuplicateRequirementException,
    RiskPriorityExceedsThresholdException,
)
from ..schema import (
    DataclassJsonEncoder,
    Requirement,
    RiskAssessment,
    TestCase,
    RISK_ASSESSMENT_CATEGORIES,
)


class SpecsManager:
    def __init__(self):
        self.test_cases: Dict[str, TestCase] = {}
        self.requirements: Dict[str, Requirement] = {}
        self.testcase_prefix = "TC"
        self.testcase_no = 1
        self.risk_assessments: Dict[str, RiskAssessment] = {}

    def enable_risk_assessment(self, path: str):
        with open(path, "r") as file:
            for _id, risk in yaml.full_load(file).items():
                self.risk_assessments[_id] = RiskAssessment.from_dict(_id, risk)

    def _format_testcase_id(self) -> str:
        return f"{self.testcase_prefix}{self.testcase_no:03}"

    def add_requirement(self, req: Requirement) -> None:
        self.requirements[req.id] = req

    def _add_test_case(self, req_id: str, test_case: TestCase) -> None:
        if req_id in self.test_cases:
            existing = self.test_cases[req_id]
            raise DuplicateRequirementException(
                f"TestCase for id {req_id} is already added by {existing.func_name}."
            )
        self.test_cases[req_id] = test_case

    def add_test_case(self, test_case: TestCase) -> None:
        if not test_case.skip and not test_case.testcase_id:
            test_case.testcase_id = self._format_testcase_id()
            self.testcase_no += 1

        for _id in test_case.ids:
            self._add_test_case(_id, test_case)

    def get_test_case(self, req_id: str) -> TestCase:
        return self.test_cases[req_id]

    def has_test_case(self, req_id: str) -> bool:
        return req_id in self.test_cases

    def requirement_passed(self, req_id: str) -> bool:
        return self.test_cases[req_id].passed

    def check_risk_assessment(self, permissable_risk_priority: str):

        for ra_id, ra in self.risk_assessments.items():

            if RISK_ASSESSMENT_CATEGORIES.index(
                ra.residual_risk_priority
            ) > RISK_ASSESSMENT_CATEGORIES.index(permissable_risk_priority):
                raise RiskPriorityExceedsThresholdException(
                    f"Risk assessment {ra_id}: Residual risk "
                    f"priority '{ra.residual_risk_priority}' "
                    f"exceeds permissable risk priority '{permissable_risk_priority}'."
                )

            # Check requirement ids
            for req_id in ra.mitigation_requirement_ids:
                if req_id not in self.requirements:
                    raise ValueError(
                        f"Risk assessment {ra_id}: mitigation_requirement_id '{req_id}' not found."
                    )

    def to_json(self, path: Path):
        data = json.dumps(
            {
                "test_cases": self.test_cases,
                "requirements": self.requirements,
                "risk_assessments": self.risk_assessments,
            },
            cls=DataclassJsonEncoder,
            indent=4,
        )
        path.write_text(data)


specs_manager = SpecsManager()
