from nydok import testcase


@testcase("FR001")
def test_minimal_passing(pytester):
    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase("FR001")
        def test_hello_default():
            assert True

        """
    )
    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Some requirement\n"),
    )
    result = pytester.runpytest_subprocess("-p", "nydok")
    result.assert_outcomes(passed=2)


@testcase(["FR010", "FR011", "FR110"])
def test_io_and_refs(pytester):
    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase("FR001",
            io=[
                ([1, 2], 3),
                ([2, 4, 7], 13),
            ],
            ref_ids=['FR002']
        )
        def test_sum(io=None):
            for i, e in io:
                assert sum(i) == e

        """
    )
    pytester.makefile(".spec.md", ("# Some heading\n\n- FR001: Must sum list of numbers\n"))

    result = pytester.runpytest_subprocess("-p", "nydok")
    result.assert_outcomes(passed=2)


@testcase("FR020", desc="Test changing regex from CLI")
def test_change_regex_cli(pytester):
    pytester.plugins = ["nydok"]

    # create a temporary pytest test file
    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase("FR001")
        def test_nothing():
            assert True

        """
    )
    pytester.makefile(
        ".spec.md",
        """
            # Some heading
            |  ID   | Description                     |
            | ----- | ------------------------------- |
            | FR001 | Support changing regex argument |


        """,
    )
    result = pytester.runpytest_subprocess(
        "--nydok-specs-regex",
        "\\|[\\s]*(?P<req_id>[A-Z]+[0-9]+)[\\s]*\\|[\\s]*(?P<desc>.*)[\\s]*\\|",
        "-s",
        "-p",
        "nydok",
    )
    result.assert_outcomes(passed=2)


@testcase("FR021", desc="Test changing regex from config")
def test_change_regex_config(pytester):
    pytester.plugins = ["nydok"]

    # create a temporary pytest test file
    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase("FR001")
        def test_nothing():
            assert True

        """
    )
    pytester.makefile(
        ".spec.md",
        """
            # Some heading
            |  ID   | Description                          |
            | ----- | ------------------------------------ |
            | FR001 | Support changing regex configuration |


        """,
    )

    pytester.makefile(
        ".ini",
        pytest=(
            "[pytest]\nnydok-specs-regex="
            "\\|[\\s]*(?P<req_id>[A-Z]+[0-9]+)[\\s]*\\|[\\s]*(?P<desc>.*)[\\s]*\\|\n"
        ),
    )
    result = pytester.runpytest_subprocess("-s", "-p", "nydok")
    result.assert_outcomes(passed=2)


@testcase(["FR030"])
def test_one_implementation_must_be_able_to_reference_multiple(pytester):
    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase(["FR001", "FR002"])
        def test_hello_default():
            assert True

        """
    )
    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Requirement 1\n- FR002: Requirement 2\n"),
    )
    result = pytester.runpytest_subprocess("-s", "-p", "nydok")
    result.assert_outcomes(passed=3)


@testcase(["UR032", "FR120"])
def test_each_requirement_must_have_a_test_case(pytester):
    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase(["FR001"])
        def test_hello_default():
            assert True

        """
    )
    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Requirement 1\n- FR002: Requirement 2\n"),
    )
    result = pytester.runpytest_subprocess("-s", "-p", "nydok")
    result.assert_outcomes(passed=2, failed=1)


@testcase("FR100")
def test_two_requirements_referencing_the_same_requirement_id_must(pytester):
    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase(["FR001"])
        def test_hello_default():
            assert True

        """
    )
    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Requirement\n- FR001: Duplicate requirement\n"),
    )
    result = pytester.runpytest_subprocess("-s", "-p", "nydok")

    result.assert_outcomes(passed=2, failed=1)


@testcase("FR200")
def test_two_test_cases_referencing_the_same_requirement_id_must(pytester):
    pytester.plugins = ["nydok"]

    pytester.makepyfile(
        """

        from nydok import testcase

        @testcase(["FR001"])
        def test_hello_default():
            assert True


        @testcase(["FR001"])
        def test_hello_again():
            assert True

        """
    )
    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Requirement\n"),
    )
    result = pytester.runpytest_subprocess("-s", "-p", "nydok")

    result.assert_outcomes(passed=2, failed=1)


JUNIT_XML_TEMPLATE = """
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Mocha Tests" time="2.593" tests="2" failures="0">
  <testsuite name="Root Suite" timestamp="2022-08-23T07:37:17" tests="0" file="cypress/e2e/spec.cy.js" failures="0" time="0">
  </testsuite>
  <testsuite name="Uploading works" timestamp="2022-08-23T07:37:17" tests="2" failures="0" time="2.593">
    <testcase name="{testcase1}" time="1.563" classname="foo">
        {testcase1failure}
    </testcase>
    <testcase name="{testcase2}" time="1.03" classname="is possible to upload multiple files">
        {testcase2failure}
    </testcase>
  </testsuite>
</testsuites>
"""  # noqa: E501


@testcase("FR270", desc="Test loading test results from external sources.")
def test_external_source(pytester):
    pytester.plugins = ["nydok"]

    # Test linking tests to requirements
    pytester.makefile(
        ".junit.xml",
        JUNIT_XML_TEMPLATE.format(
            testcase1="FR001: Foo",
            testcase1failure="",
            testcase2="FR002: Bar",
            testcase2failure="",
        ),
    )

    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Some specification\n- FR002: A different specification\n"),
    )
    result = pytester.runpytest_subprocess("-p", "nydok")
    result.assert_outcomes(passed=4)

    # Test with one JUnit result failing, ensure spec test fails as well
    [f.unlink() for f in pytester.path.glob("*.junit.xml")]

    pytester.makefile(
        ".junit.xml",
        JUNIT_XML_TEMPLATE.format(
            testcase1="FR001: Foo",
            testcase1failure="",
            testcase2="FR002: Bar",
            testcase2failure='<failure message="Expected true to be false." type="AssertionError">Expected true to be false.</failure>',  # noqa: E501
        ),
    )

    result = pytester.runpytest_subprocess("-p", "nydok")
    result.assert_outcomes(passed=2, failed=2)


@testcase("FR280")
def test_external_source_multiple_name(pytester):
    pytester.plugins = ["nydok"]

    # Test multiple with same names, no failures
    pytester.makefile(
        ".junit.xml",
        JUNIT_XML_TEMPLATE.format(
            testcase1="FR001: Foo",
            testcase1failure="",
            testcase2="FR001: Foo",
            testcase2failure="",
        ),
    )

    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Some specification\n"),
    )
    result = pytester.runpytest_subprocess("-p", "nydok")
    result.assert_outcomes(passed=2, failed=0)

    # Test multiple with same name, one failing
    [f.unlink() for f in pytester.path.glob("*.junit.xml")]

    pytester.makefile(
        ".junit.xml",
        JUNIT_XML_TEMPLATE.format(
            testcase1="FR001: Foo",
            testcase1failure="",
            testcase2="FR001: Foo",
            testcase2failure='<failure message="Expected true to be false." type="AssertionError">Expected true to be false.</failure>',  # noqa: E501
        ),
    )

    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Some specification\n"),
    )
    result = pytester.runpytest_subprocess("-p", "nydok")
    result.assert_outcomes(passed=0, failed=2)
    result.stdout.re_match_lines(r".*Expected true to be false.*")

    # Test multiple with same name, both failing, should select first
    [f.unlink() for f in pytester.path.glob("*.junit.xml")]

    pytester.makefile(
        ".junit.xml",
        JUNIT_XML_TEMPLATE.format(
            testcase1="FR001: Foo",
            testcase1failure='<failure message="First time" type="AssertionError">First time.</failure>',  # noqa: E501
            testcase2="FR001: Foo",
            testcase2failure='<failure message="Second time" type="AssertionError">Second time.</failure>',  # noqa: E501
        ),
    )

    pytester.makefile(
        ".spec.md",
        ("# Some heading\n\n- FR001: Some specification\n"),
    )
    result = pytester.runpytest_subprocess("-p", "nydok")
    result.assert_outcomes(passed=0, failed=2)
    result.stdout.re_match_lines(r".*First time.*")
