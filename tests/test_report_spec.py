import os
import subprocess
from pathlib import Path

from nydok import testcase

SCRIPT_DIR = Path(__file__).parent


@testcase(["FR500", "FR510", "FR520", "FR530"])
def test_traceability_matrix_report(pytester):
    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase(["UR001", "FR001"])
        def test_hello():
            assert True

        """
    )
    pytester.makefile(
        ".spec.md",
        (
            "# Some heading\n\n- UR001: User specification\n- FR001 [UR001]: Functional specification\n"  # noqa: E501
        ),
    )

    ra_file: Path = pytester.makefile(
        ".yml",
        """
            RA001:
                description: Risk assessment description.
                consequence: Consequence description.
                prior_probability: low
                prior_severity: low
                prior_detectability: high
                mitigation: Mitigation description.
                residual_probability: low
                residual_severity: low
                residual_detectability: high
        """,
    )

    result = pytester.runpytest_subprocess(
        "-s",
        "-p",
        "nydok",
        "--nydok-output",
        "nydok.json",
        "--nydok-risk-assessment",
        ra_file.absolute(),
    )

    assert result.ret == 0
    result.assert_outcomes(passed=3, failed=0)

    tm_output_file: Path = pytester.makefile(".md", "")
    subprocess.check_call(
        (
            "nydok report traceability-matrix --categories 'User specification,UR' --base-prefix FR"
            f" --output {tm_output_file.absolute()} nydok.json"
        ),
        shell=True,
    )

    # Checks that result:
    # - Has categories as defined
    # - Filters on prefix as defined
    # - Has correct spec ID and description
    # - Other references are listed correctly
    # - Test case is generated and referenced
    with open(tm_output_file.absolute(), "r") as f:
        with open(SCRIPT_DIR / "snapshots" / "traceability-matrix-report.md", "r") as expected:
            assert expected.read() == f.read()


@testcase("FR550")
def test_risk_assessment_report(pytester):
    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase(["FR001"])
        def test_hello():
            assert True

        """
    )
    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Specification\n"),
    )

    ra_file: Path = pytester.makefile(
        ".yml",
        """
            RA001:
                description: Ipsem lorem dolor sit amet, consectetur adipiscing elit.
                consequence: Morbi laoreet et purus gravida hendrerit.
                prior_probability: high
                prior_severity: medium
                prior_detectability: medium
                mitigation: Praesent a magna condimentum.
                mitigation_requirement_ids: ['FR001']
                residual_probability: low
                residual_severity: medium
                residual_detectability: high
            RA002:
                description: Suspendisse vel ante lobortis, ullamcorper felis non, sodales tellus.
                consequence: Aliquam erat volutpat.
                prior_probability: high
                prior_severity: high
                prior_detectability: medium
                mitigation: Nam ultrices at odio.
                residual_probability: low
                residual_severity: low
                residual_detectability: high
        """,
    )

    result = pytester.runpytest_subprocess(
        "-s",
        "-p",
        "nydok",
        "--nydok-output",
        "nydok.json",
        "--nydok-risk-assessment",
        ra_file.absolute(),
    )

    assert result.ret == 0
    result.assert_outcomes(passed=2, failed=0)

    ra_output_file: Path = pytester.makefile(".md", "")
    subprocess.check_call(
        f"nydok report risk-assessment --output {ra_output_file.absolute()} nydok.json", shell=True
    )

    with open(ra_output_file.absolute(), "r") as f:
        with open(SCRIPT_DIR / "snapshots" / "risk-report.md", "r") as expected:
            assert f.read() == expected.read()


@testcase(["FR600"])
def test_test_overview_report(pytester):
    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """
        from nydok import testcase

        @testcase(["UR001", "FR001"])
        def test_hello():
            assert True

        @testcase(
            ["FR002"],
            desc="Test failure status and description"
        )
        def test_failure():
            assert False

        """
    )
    pytester.makefile(
        ".spec.md",
        (
            "# Some heading\n\n- UR001: User specification\n- FR001 [UR001]: Functional specification\n- FR002 [UR001]: I will fail\n"  # noqa: E501
        ),
    )

    result = pytester.runpytest_subprocess(
        "-s",
        "-p",
        "nydok",
        "--nydok-output",
        "nydok.json",
    )

    assert result.ret == 1  # TESTS_FAILED
    result.assert_outcomes(passed=3, failed=2)

    tr_output_file: Path = pytester.makefile(".md", "")
    subprocess.check_call(
        f"nydok report test-overview --output {tr_output_file.absolute()} nydok.json", shell=True
    )

    with open(tr_output_file.absolute(), "r") as f:
        with open(SCRIPT_DIR / "snapshots" / "test-overview.md", "r") as expected:
            assert expected.read() == f.read()


@testcase(["FR610", "FR611", "FR620", "FR630"])
def test_test_case_report(pytester):
    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """
        from nydok import testcase

        @testcase(["UR001", "FR001"])
        def test_hello():
            assert True

        @testcase(
            ["FR002"],
            desc="Test failure status and description"
        )
        def test_failure():
            assert False

        """
    )
    pytester.makefile(
        ".spec.md",
        (
            "# Some heading\n\n- UR001: User specification\n- FR001 [UR001]: Functional specification\n- FR002 [UR001]: I will fail\n"  # noqa: E501
        ),
    )

    result = pytester.runpytest_subprocess(
        "-s",
        "-p",
        "nydok",
        "--nydok-output",
        "nydok.json",
    )

    assert result.ret == 1  # TESTS_FAILED
    result.assert_outcomes(passed=3, failed=2)

    tr_output_file: Path = pytester.makefile(".md", "")
    subprocess.check_call(
        f"nydok report test-cases --output {tr_output_file.absolute()} nydok.json", shell=True
    )

    with open(tr_output_file.absolute(), "r") as f:
        with open(SCRIPT_DIR / "snapshots" / "test-cases.md", "r") as expected:
            assert expected.read() == f.read()


@testcase(["FR650", "FR651", "FR660", "FR670"])
def test_code_change_report(pytester):
    pytester.plugins = ["nydok"]

    from pytest_httpserver import HTTPServer

    with HTTPServer() as server:
        # For restoring original env afterwards
        _gitlab_url = os.environ.get("GITLAB_URL")
        _gitlab_token = os.environ.get("GITLAB_TOKEN")
        os.environ["GITLAB_TOKEN"] = "test-token"
        os.environ["GITLAB_URL"] = f"http://localhost:{server.port}"

        # Branch commits response
        server.expect_request(
            "/api/v4/projects/repo/repository/commits",
            headers={
                "Authorization": "Bearer test-token",
            },
            query_string="ref_name=v1.0...main&per_page=100",
        ).respond_with_json(
            [
                # MR: Title 4
                {"id": "ec00b4f28b7b494d2c0f7f2e31511f81316c8044"},
                # Not connected to any MR
                {"id": "be5ab2735fff02364d09dca19cde8e61905368a3"},
                # MR: Title 3
                {"id": "f5f2a240d58d415b460911fa759eb25a08d1f427"},
                #
                {"id": "268580c4cecca0c6957a7d0af5f0b3d080a9dcdd"},
            ]
        )

        server.expect_request(
            "/api/v4/projects/repo/merge_requests",
            headers={
                "Authorization": "Bearer test-token",
            },
            query_string="state=merged&per_page=100",
        ).respond_with_json(
            [
                {
                    "title": "Title 4",
                    "merged_at": "2022-06-14T11:08:35Z",
                    "merge_commit_sha": "ec00b4f28b7b494d2c0f7f2e31511f81316c8044",
                    "author": {"name": "Test user"},
                    "reviewers": [{"name": "Test reviewer"}],
                },
                {
                    "title": "Title 3",
                    "merged_at": "2022-05-25T10:27:10Z",
                    "merge_commit_sha": "f5f2a240d58d415b460911fa759eb25a08d1f427",
                    "author": {"name": "Test user"},
                    "reviewers": [{"name": "Test reviewer"}],
                },
                {
                    "title": "Hash is not in commit list, shouldn't be included",
                    "merged_at": "2022-05-23T12:32:00Z",
                    "merge_commit_sha": "ffdcdc86105205703af38a7a0c7ff49d760dcb42",
                    "author": {"name": "Test user"},
                    "reviewers": [{"name": "Test reviewer"}],
                },
            ]
        )

        # Generate report
        cc_output_file: Path = pytester.makefile(".md", "")
        subprocess.check_call(
            (
                "nydok report code-review --to-ref main --from-ref v1.0"
                f" --repo-path repo --output {cc_output_file.absolute()}"
            ),
            shell=True,
        )

    with open(cc_output_file.absolute(), "r") as f:
        with open(SCRIPT_DIR / "snapshots" / "code-change-report.md", "r") as expected:
            assert expected.read() == f.read()

    if _gitlab_token:
        os.environ["GITLAB_TOKEN"] = _gitlab_token
    if _gitlab_url:
        os.environ["GITLAB_URL"] = _gitlab_url


@testcase("FR700")
def test_pipeline_logs(pytester) -> None:
    pytester.plugins = ["nydok"]

    from pytest_httpserver import HTTPServer

    with HTTPServer() as server:
        # For restoring original env afterwards
        _gitlab_url = os.environ.get("GITLAB_URL")
        _gitlab_token = os.environ.get("GITLAB_TOKEN")
        os.environ["GITLAB_TOKEN"] = "test-token"
        os.environ["GITLAB_URL"] = f"http://localhost:{server.port}"

        # Branch commits response
        server.expect_request(
            "/api/v4/projects/repo/pipelines/1/jobs",
            headers={
                "Authorization": "Bearer test-token",
            },
        ).respond_with_json(
            [
                {"id": 1, "status": "success", "name": "job1"},
                {"id": 2, "status": "failure", "name": "job2"},
                {
                    "id": 3,
                    "status": "success",
                    "name": "job_not_included",
                },
            ]
        )

        server.expect_request(
            "/api/v4/projects/repo/jobs/1/trace",
            headers={
                "Authorization": "Bearer test-token",
            },
        ).respond_with_data("TRACE1")

        server.expect_request(
            "/api/v4/projects/repo/jobs/2/trace",
            headers={
                "Authorization": "Bearer test-token",
            },
        ).respond_with_data("TRACE2")

        output_file: Path = pytester.makefile(".md", "")
        subprocess.check_call(
            (
                "nydok report pipeline-logs --pipeline-id 1 --repo-path repo"
                f" --job-names job1,job2 --output {output_file.absolute()}"
            ),
            shell=True,
        )

    with open(output_file.absolute(), "r") as f:
        with open(SCRIPT_DIR / "snapshots" / "pipeline-logs-report.md", "r") as expected:
            assert expected.read() == f.read()

    if _gitlab_token:
        os.environ["GITLAB_TOKEN"] = _gitlab_token
    if _gitlab_url:
        os.environ["GITLAB_URL"] = _gitlab_url
