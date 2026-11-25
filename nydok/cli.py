"""The `nydok` command line interface."""

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

import click

from .report import (
    create_codereview_report,
    create_pipeline_logs_report,
    create_risk_report,
    create_test_case_report,
    create_test_overview_report,
    create_traceability_matrix,
)
from .schema import Requirement, RiskAssessment, TestCase

F = TypeVar("F", bound=Callable[..., object])


@click.group()
def cli() -> None:
    """Nydok: documentation and specification testing."""


@cli.group()
def report() -> None:
    """Create reports from the nydok results JSON, or from GitLab."""


@dataclass
class _Results:
    """Contents of a results JSON. `test_cases` has a test case once per requirement it covers."""

    test_cases: list[TestCase]
    requirements: list[Requirement]
    risk_assessments: dict[str, RiskAssessment]


def _load_json(path: Path) -> _Results:
    """Read a results JSON, as written by the plugin's `nydok-output` setting."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return _Results(
        test_cases=[TestCase(**test_case) for test_case in data["test_cases"].values()],
        requirements=[
            Requirement(**{**requirement, "file_path": Path(requirement["file_path"])})
            for requirement in data["requirements"].values()
        ],
        risk_assessments={
            _id: RiskAssessment.from_dict(_id, risk_assessment)
            for _id, risk_assessment in data["risk_assessments"].items()
        },
    )


def _output_option(func: F) -> F:
    """Add the `--output` option to a command."""
    return click.option(
        "--output",
        "-o",
        type=click.Path(writable=True),
        default="-",
        help="Output path (default: stdout).",
    )(func)


def _repo_path_option(func: F) -> F:
    """Add the `--repo-path` option to a command."""
    return click.option(
        "--repo-path",
        "-r",
        type=str,
        required=True,
        help="Gitlab repository path. E.g. my-group/my-project.",
    )(func)


def _write(text: str, output: str) -> None:
    """Write a report to file `output`, or to stdout if it is "-"."""
    if output == "-":
        sys.stdout.write(text)
    else:
        Path(output).write_text(text, encoding="utf-8")


@report.command(help="Create traceability matrix.")
@click.argument("result", type=click.Path(exists=True))
@click.option("--base-prefix", type=str, help="Prefix to use as basis (filter).")
@click.option(
    "--categories",
    type=str,
    help="Comma-separated title,prefix pairs, one per extra column. E.g. 'User req.,UR,Design,DR'.",
)
@_output_option
def traceability_matrix(result: str, base_prefix: str | None, categories: str | None, output: str) -> None:
    """Write the traceability matrix of the requirements in a results JSON."""
    category_pairs = None
    if categories:
        parts = categories.split(",")
        if len(parts) % 2 != 0:
            raise click.BadParameter("Categories must be in pairs.", param_hint="--categories")
        category_pairs = list(zip(parts[::2], parts[1::2], strict=True))

    data = _load_json(Path(result))
    text = create_traceability_matrix(
        data.requirements, data.test_cases, base_prefix=base_prefix, categories=category_pairs
    )
    # Only this report ends with a newline on stdout
    _write(text + "\n" if output == "-" else text, output)


@report.command(help="Create risk assessment tables.")
@click.argument("result", type=click.Path(exists=True))
@_output_option
def risk_assessment(result: str, output: str) -> None:
    """Write the risk assessment tables of a results JSON."""
    data = _load_json(Path(result))
    _write(create_risk_report(data.risk_assessments), output)


@report.command(help="Create test overview table.")
@click.argument("result", type=click.Path(exists=True))
@_output_option
def test_overview(result: str, output: str) -> None:
    """Write the test overview table of a results JSON."""
    data = _load_json(Path(result))
    _write(create_test_overview_report(data.test_cases), output)


@report.command(help="Create test case report.")
@click.argument("result", type=click.Path(exists=True))
@_output_option
def test_cases(result: str, output: str) -> None:
    """Write the test case report of a results JSON."""
    data = _load_json(Path(result))
    _write(create_test_case_report(data.requirements, data.test_cases), output)


@report.command(help="Create code review table.")
@_repo_path_option
@click.option(
    "--to-ref",
    "-c",
    type=str,
    default="main",
    help="Git ref for end of commit range. Default: main.",
)
@click.option(
    "--from-ref",
    "-f",
    type=str,
    help="Git ref for start of commit range. Default is all history.",
)
@_output_option
def code_review(repo_path: str, to_ref: str, from_ref: str | None, output: str) -> None:
    """Write the code review report of a GitLab project's commit range."""
    _write(create_codereview_report(repo_path=repo_path, to_ref=to_ref, from_ref=from_ref), output)


@report.command(help="Create pipeline logs report.")
@_repo_path_option
@click.option(
    "--pipeline-id",
    "-p",
    type=click.INT,
    required=True,
    help="Pipeline ID in Gitlab from which to retrieve job logs.",
)
@click.option(
    "--job-names",
    "-j",
    type=str,
    help="Job names in pipeline for only including certain jobs. Default is all jobs.",
)
@_output_option
def pipeline_logs(repo_path: str, pipeline_id: int, job_names: str | None, output: str) -> None:
    """Write the pipeline logs report of a GitLab pipeline."""
    text = create_pipeline_logs_report(
        repo_path=repo_path,
        pipeline_id=pipeline_id,
        job_names=job_names.split(",") if job_names else None,
    )
    _write(text, output)
