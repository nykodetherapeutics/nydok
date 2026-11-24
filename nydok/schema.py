"""Data classes for requirements, test cases and risk assessments, as stored in nydok's results JSON."""

import dataclasses
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


class DataclassJsonEncoder(json.JSONEncoder):
    """JSON encoder that also handles data classes, paths and dates."""

    def default(self, o: object) -> object:
        """Return a JSON-serialisable form of `o`."""
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return dataclasses.asdict(o)
        if isinstance(o, Path):
            return str(o)
        if isinstance(o, date):  # Also datetime, a subclass
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
    """A test covering one or more requirements: a `@testcase` function or a JUnit test case."""

    __test__ = False  # Not a pytest test class, despite the name

    ids: list[str]
    # None until numbered by the SpecsManager; stays None for skip test cases without one
    testcase_id: str | None
    desc: str
    io: list[tuple[Any, Any]] | None
    func_name: str
    func_src: str | None  # None for JUnit test cases
    ref_ids: list[str] | None
    skip: bool
    passed: bool


@dataclass
class Requirement:
    """A requirement from a specification file."""

    id: str
    desc: str
    file_path: Path
    line_no: int
    ref_ids: list[str]


@dataclass
class RiskAssessment:
    """A risk assessment item, with its risk priority before and after mitigation."""

    id: str
    description: str
    consequence: str
    prior_probability: str
    prior_severity: str
    prior_detectability: str
    mitigation: str
    mitigation_requirement_ids: list[str]
    residual_probability: str
    residual_severity: str
    residual_detectability: str

    def __post_init__(self) -> None:
        """Check that the risk levels are valid and the text fields are given."""
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
                raise ValueError(f"Error while checking Risk Assessment {self.id}: {attrib} must be defined")

    @property
    def prior_risk_priority(self) -> str:
        """Risk priority before mitigation."""
        prior_risk_class = RISK_ASSESSMENT_CLASS[self.prior_probability][self.prior_severity]
        return RISK_ASSESSMENT_PRIORITY[prior_risk_class][self.prior_detectability]

    @property
    def residual_risk_priority(self) -> str:
        """Risk priority after mitigation."""
        residual_risk_class = RISK_ASSESSMENT_CLASS[self.residual_probability][self.residual_severity]
        return RISK_ASSESSMENT_PRIORITY[residual_risk_class][self.residual_detectability]

    @classmethod
    def from_dict(cls, _id: str, risk_dict_object: dict[str, Any]) -> "RiskAssessment":
        """Populate a RiskAssessment from a dictionary object from a yaml-file."""
        _risk_dict_object = dict(risk_dict_object)
        _risk_dict_object.setdefault("id", _id)
        _risk_dict_object.setdefault("mitigation_requirement_ids", [])
        return cls(**_risk_dict_object)
