import dataclasses
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


class DataclassJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif isinstance(o, Path):
            return str(o)
        elif isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, date):
            return o.isoformat()
        return super().default(o)


# Ordered according to level of severity, don't change
RISK_ASSESSMENT_CATEGORIES = ("low", "medium", "high")

RISK_ASSESSMENT_CLASS = {
    # Given probability then severity
    "high": {"high": 1, "medium": 1, "low": 2},
    "medium": {"high": 1, "medium": 2, "low": 3},
    "low": {"high": 2, "medium": 3, "low": 3},
}

RISK_ASSESSMENT_PRIORITY = {
    # Given class then detectability
    1: {
        "high": "medium",
        "medium": "high",
        "low": "high",
    },
    2: {
        "high": "low",
        "medium": "medium",
        "low": "high",
    },
    3: {
        "high": "low",
        "medium": "low",
        "low": "medium",
    },
}


@dataclass
class TestCase:
    ids: List[str]
    testcase_id: str
    desc: str
    io: List[Tuple[Any, Any]]
    func_name: str
    func_src: str
    ref_ids: List[str]
    skip: bool
    passed: bool


@dataclass
class Requirement:
    id: str
    desc: str
    file_path: Path
    line_no: int
    ref_ids: List[str]


@dataclass
class RiskAssessment:
    id: str
    description: str
    consequence: str
    prior_probability: str
    prior_severity: str
    prior_detectability: str
    mitigation: str
    mitigation_requirement_ids: List[str]
    residual_probability: str
    residual_severity: str
    residual_detectability: str

    def __post_init__(self):

        risk_fields = [
            "prior_probability",
            "prior_severity",
            "prior_detectability",
            "residual_probability",
            "residual_severity",
            "residual_detectability",
        ]
        for field in risk_fields:
            if getattr(self, field) not in RISK_ASSESSMENT_CATEGORIES:
                raise ValueError(
                    f"Error while checking Risk Assessment {self.id}: {field} "
                    f"must be one of {RISK_ASSESSMENT_CATEGORIES}"
                )

        required_attribs = [
            "id",
            "description",
            "consequence",
            "mitigation",
        ]
        for attrib in required_attribs:
            if not getattr(self, attrib):
                raise ValueError(
                    f"Error while checking Risk Assessment {self.id}: {attrib} must be defined"
                )

    @property
    def prior_risk_priority(self) -> str:
        prior_risk_class = RISK_ASSESSMENT_CLASS[self.prior_probability][self.prior_severity]
        prior_risk_priority = RISK_ASSESSMENT_PRIORITY[prior_risk_class][self.prior_detectability]
        return prior_risk_priority

    @property
    def residual_risk_priority(self) -> str:
        residual_risk_class = RISK_ASSESSMENT_CLASS[self.residual_probability][
            self.residual_severity
        ]
        residual_risk_priority = RISK_ASSESSMENT_PRIORITY[residual_risk_class][
            self.residual_detectability
        ]
        return residual_risk_priority

    @classmethod
    def from_dict(cls, _id, risk_dict_object: Dict):
        """Populate a RiskAssessment from a dictionary object from a yaml-file."""
        _risk_dict_object = dict(risk_dict_object)
        _risk_dict_object.setdefault("id", _id)
        _risk_dict_object.setdefault("mitigation_requirement_ids", [])
        return cls(**_risk_dict_object)
