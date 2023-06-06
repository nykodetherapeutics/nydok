import json
import sys
from pathlib import Path

import click

from .report import (
    create_codereview_report,
    create_pipeline_logs_report,
    create_risk_report,
    create_test_overview_report,
    create_test_case_report,
    create_traceability_matrix,
)
from .schema import Requirement, RiskAssessment, TestCase


@click.group()
def cli():
    pass


@cli.group()
def report():
    pass


def _load_json(path: Path):
    data = json.loads(path.read_text())
    return {
        "test_cases": {_id: TestCase(**test_case) for _id, test_case in data["test_cases"].items()},
        "requirements": {
            _id: Requirement(**requirement) for _id, requirement in data["requirements"].items()
        },
        "risk_assessments": {
            _id: RiskAssessment.from_dict(_id, risk_assessment)
            for _id, risk_assessment in data["risk_assessments"].items()
        },
    }


@report.command(help="Create traceability matrix.")
@click.argument("result", type=click.Path(exists=True))
@click.option("--base-prefix", type=str, help="Prefix to use as basis (filter).")
@click.option(
    "--categories",
    type=str,
    help="Categories for traceability (title,prefix). Repeat for multiple.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    default="-",
    help="Output path (default: stdout).",
)
def traceability_matrix(result, base_prefix, categories, output):

    if categories:
        assert len(categories.split(",")) % 2 == 0, "Categories must be in pairs."
        categories = list(zip(categories.split(",")[::2], categories.split(",")[1::2]))

    data = _load_json(Path(result))
    report = create_traceability_matrix(
        data["requirements"].values(),
        data["test_cases"].values(),
        base_prefix=base_prefix,
        categories=categories,
    )
    if output == "-":
        sys.stdout.write(report + "\n")
    else:
        Path(output).write_text(report)


@report.command(help="Create risk assessment tables.")
@click.argument("result", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    default="-",
    help="Output path (default: stdout).",
)
def risk_assessment(result, output):

    data = _load_json(Path(result))
    report = create_risk_report(data["risk_assessments"])

    if output == "-":
        sys.stdout.write(report)
    else:
        Path(output).write_text(report)


@report.command(help="Create test overview table.")
@click.argument("result", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    default="-",
    help="Output path (default: stdout).",
)
def test_overview(result, output):

    data = _load_json(Path(result))
    report = create_test_overview_report(
        data["requirements"].values(),
        data["test_cases"].values(),
    )
    if output == "-":
        sys.stdout.write(report)
    else:
        Path(output).write_text(report)


@report.command(help="Create test case report.")
@click.argument("result", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    default="-",
    help="Output path (default: stdout).",
)
def test_cases(result, output):

    data = _load_json(Path(result))
    report = create_test_case_report(
        data["requirements"].values(),
        data["test_cases"].values(),
    )
    if output == "-":
        sys.stdout.write(report)
    else:
        Path(output).write_text(report)


@report.command(help="Create code review table.")
@click.option(
    "--repo-path",
    "-r",
    type=str,
    required=True,
    help="Gitlab repository path. E.g. my-group/my-project.",
)
@click.option(
    "--to-ref",
    "-c",
    type=str,
    default="main",
    help="Git ref for end of commit range. Default is default branch configured for repository.",
)
@click.option(
    "--from-ref",
    "-f",
    type=str,
    help="Git ref for start of commit range. Default is all history.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    default="-",
    help="Output path (default: stdout).",
)
def code_review(repo_path, to_ref, from_ref, output):

    report = create_codereview_report(
        repo_path=repo_path,
        to_ref=to_ref,
        from_ref=from_ref,
    )
    if output == "-":
        sys.stdout.write(report)
    else:
        Path(output).write_text(report)


@report.command(help="Create pipeline logs report.")
@click.option(
    "--repo-path",
    "-r",
    type=str,
    required=True,
    help="Gitlab repository path. E.g. my-group/my-project.",
)
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
@click.option(
    "--output",
    "-o",
    type=click.Path(writable=True),
    default="-",
    help="Output path (default: stdout).",
)
def pipeline_logs(repo_path, pipeline_id, job_names, output):

    job_names = job_names.split(",") if job_names else None

    report = create_pipeline_logs_report(
        repo_path=repo_path, pipeline_id=pipeline_id, job_names=job_names
    )
    if output == "-":
        sys.stdout.write(report)
    else:
        Path(output).write_text(report)
