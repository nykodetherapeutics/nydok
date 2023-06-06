import subprocess
from pathlib import Path

from nydok import testcase

JUNIT_XML_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Mocha Tests" time="2.593" tests="2" failures="0">
  <testsuite name="Root Suite" timestamp="2022-08-23T07:37:17" tests="0" file="cypress/e2e/spec.cy.js" failures="0" time="0">
  </testsuite>
  <testsuite name="Uploading works" timestamp="2022-08-23T07:37:17" tests="2" failures="0" time="2.593">
    <testcase name="{name}" time="1.563" classname="foo" failure="false" error="false" success="{result}">
    </testcase>
  </testsuite>
</testsuites>
"""  # noqa: E501


@testcase(
    [
        "UR001",
        "UR010",
        "UR020",
        "UR030",
        "UR031",
        "UR033",
        "UR040",
        "UR045",
        "UR050",
        "UR070",
        "UR080",
    ]
)
def test_base_urs(pytester):
    """Test that requirements in URS are covered.

    Simple smoke tests testing that functionality is present and running through.
    """

    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase(["FR001", "FR003"],
            io=[
                ([1, 2], 3),
                ([2, 4, 7], 13),
            ],
            ref_ids=['UR001']
        )
        def test_sum(io=None):
            for i, e in io:
                assert sum(i) == e

        """
    )
    pytester.makefile(
        ".spec.md",
        (
            "# Some heading\n\n- FR001: Must sum list of numbers\n- FR002 [UR002]: External test result\n- FR003: Yet another test\n"  # noqa: E501
        ),
    )

    pytester.makefile(".junit.xml", JUNIT_XML_TEMPLATE.format(name="FR002: Foo", result="true"))

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
                mitigation_requirement_ids: ["FR001"]
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
    # 3 spec tests, 1 python test and 1 external test
    result.assert_outcomes(passed=5)

    # Traceability matrix
    tm_output_file: Path = pytester.makefile(".md", "")
    subprocess.check_call(
        (
            "nydok report traceability-matrix --categories 'User specification,UR' --base-prefix FR"
            f" --output {tm_output_file.absolute()} nydok.json"
        ),
        shell=True,
    )

    # Risk assessment report
    ra_output_file: Path = pytester.makefile(".md", "")
    subprocess.check_call(
        f"nydok report risk-assessment --output {ra_output_file.absolute()} nydok.json",
        shell=True,
    )

    # Test cases report
    tr_output_file: Path = pytester.makefile(".md", "")
    subprocess.check_call(
        f"nydok report test-cases --output {tr_output_file.absolute()} nydok.json",
        shell=True,
    )


@testcase(["UR060", "UR090"])
def test_skip():
    # Skip testing URS since it relies on external API
    # Functionality is tested in test_report_spec.py
    pass
