"""Exceptions that fail requirement and test case items."""


class DuplicateRequirementException(Exception):
    """A requirement ID is defined twice, or covered by two test cases."""


class FailedTestCaseException(Exception):
    """The test case covering a requirement failed."""


class MissingTestCaseException(Exception):
    """No test case covers a requirement."""


class RiskPriorityExceedsThresholdException(Exception):
    """A residual risk priority is above the accepted threshold."""
