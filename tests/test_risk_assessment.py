from pathlib import Path

import yaml

from nydok import testcase


@testcase("FR301")
def test_risk_assessment_basic(pytester):
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

    ra_ok_file: Path = pytester.makefile(
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
        "-s", "-p", "nydok", "--nydok-risk-assessment", ra_ok_file.absolute()
    )

    result.assert_outcomes(passed=2, failed=0)


@testcase(["FR310"])
def test_risk_assessment_missing_metadata(pytester):
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

    ra_data = {
        "RA001": {
            "description": "Risk assessment description.",
            "consequence": "Consequence description.",
            "prior_probability": "low",
            "prior_severity": "low",
            "prior_detectability": "high",
            "mitigation": "Mitigation description.",
            "residual_probability": "low",
            "residual_severity": "low",
            "residual_detectability": "high",
        }
    }

    for key in ra_data["RA001"]:
        ra_fail_data = {
            "RA001": ra_data["RA001"].copy(),
        }
        ra_fail_data["RA001"][key] = ""

        ra_fail_file: Path = pytester.makefile(
            ".yml",
            yaml.safe_dump(ra_fail_data),
        )

        result = pytester.runpytest_subprocess(
            "-p", "nydok", "--nydok-risk-assessment", ra_fail_file.absolute()
        )

        assert any(
            "Error while checking Risk Assessment RA001" in line for line in result.stderr.lines
        )


@testcase(["UR051", "FR320", "FR321"])
def test_residual_risk_priority(pytester):
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

    # Default is low, should pass fine
    result = pytester.runpytest_subprocess(
        "-p", "nydok", "--nydok-risk-assessment", ra_file.absolute()
    )
    assert result.ret == 0

    # Test with medium risk priority
    # high probability, high severity, but high detectability -> medium
    ra_file: Path = pytester.makefile(
        ".yml",
        """
            RA001:
                description: Risk assessment description.
                consequence: Consequence description.
                prior_probability: high
                prior_severity: high
                prior_detectability: high
                mitigation: Mitigation description.
                residual_probability: high
                residual_severity: high
                residual_detectability: high
        """,
    )

    # Default is low, should not pass
    result = pytester.runpytest_subprocess(
        "-p", "nydok", "--nydok-risk-assessment", ra_file.absolute()
    )

    assert result.ret == 3
    assert any(
        (
            "Risk assessment RA001: Residual risk priority 'medium'"
            " exceeds permissable risk priority 'low'"
        )
        in line
        for line in result.outlines
    )

    # Test again with medium threshold, should now pass
    result = pytester.runpytest_subprocess(
        "-p",
        "nydok",
        "--nydok-risk-assessment",
        ra_file.absolute(),
        "--nydok-risk-priority-threshold",
        "medium",
    )

    assert result.ret == 0
    assert not any(
        "Risk assessment RA001: Residual risk priority 'medium' exceeds permissable risk priority"
        in line
        for line in result.outlines
    )


@testcase(["FR330", "FR331"])
def test_risk_assessment_mitigation_requirement_id(pytester):
    pytester.plugins = ["nydok"]
    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase(["FR001", "FR002"])
        def test_hello():
            assert True
        """
    )
    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Specification\n"),
        ("# Some heading\n\n- FR002: Specification\n"),
    )

    ra_file: Path = pytester.makefile(
        ".yml",
        """
        RA001:
                description: Risk assessment description.
                consequence: Consequence description.
                prior_probability: high
                prior_severity: high
                prior_detectability: high
                mitigation: Mitigation description.
                mitigation_requirement_ids: ['FR001', 'FR002']
                residual_probability: low
                residual_severity: low
                residual_detectability: high
        RA002:
                description: Risk assessment description.
                consequence: Consequence description.
                prior_probability: high
                prior_severity: high
                prior_detectability: high
                mitigation: Mitigation description.
                mitigation_requirement_ids: ['FR003']
                residual_probability: low
                residual_severity: low
                residual_detectability: high
        """,
    )

    result = pytester.runpytest_subprocess(
        "-p", "nydok", "--nydok-risk-assessment", ra_file.absolute()
    )

    assert result.ret == 3
    assert any(
        "Risk assessment RA002: mitigation_requirement_id 'FR003' not found" in line
        for line in result.outlines
    )
