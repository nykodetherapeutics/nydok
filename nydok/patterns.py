"""Default regular expressions for finding requirements and test cases.

Kept free of pytest imports: the Markdown extension uses them when building documentation.
"""

# A requirement in a specification file, e.g. "- FR001 [UR001,UR002]: Description"
DEFAULT_REQ_PATTERN = r"- (?P<req_id>[A-Z]+[0-9]+)( \[(?P<refs>[A-Z,0-9]+)\])?: (?P<desc>.*)"

# The name of a JUnit test case, e.g. "FR001,FR002 [RA001]: Description"
JUNIT_PATTERN = r"(?P<req_id>[A-Z,0-9]+)( \[(?P<refs>[A-Z,0-9]+)\])?: (?P<desc>.*)"
