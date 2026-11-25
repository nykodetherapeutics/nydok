"""Markdown and HTML reports built from nydok's results JSON and from GitLab."""

import re

from .gitlab import fetch_mergerequests, get_commits_for_ref, get_pipeline_logs
from .schema import Requirement, RiskAssessment, TestCase


def _render_md_table(header: list[str], rows: list[list[str]], max_col_width: int = 100) -> str:
    """Render a Markdown table, padding each column to its widest cell, up to `max_col_width`."""

    def _md_table_row(cols: list[str], col_widths: list[int]) -> str:
        """Render one table row, padding each cell to its column's width."""
        return " | ".join(f"{col:<{width}}" for col, width in zip(cols, col_widths, strict=True))

    max_col_size = [min(max(len(r[idx]) for r in [header, *rows]), max_col_width) for idx in range(len(header))]

    result = ""
    result += _md_table_row(header, max_col_size) + "\n"
    result += _md_table_row(["-" * max_col_size[i] for i in range(0, len(header))], max_col_size) + "\n"
    for row in rows:
        result += _md_table_row(row, max_col_size) + "\n"

    return result


def _get_ids_for_req(req: Requirement, req_impl: TestCase | None = None) -> set[str]:
    """Collect the IDs a requirement references, itself or through its test case."""
    ref_ids: set[str] = set()
    if req.ref_ids:
        ref_ids.update(req.ref_ids)
    if req_impl and req_impl.ref_ids:
        ref_ids.update(req_impl.ref_ids)

    return ref_ids


def _traverse_ids_for_req(
    req: Requirement,
    candidate_reqs: list[Requirement],
    candidate_impl: list[TestCase],
    prefix: str,
    path: frozenset[str] = frozenset(),
) -> set[str]:
    """Find the IDs with a prefix that a requirement references, directly or through other requirements.

    Args:
        req: The requirement.
        candidate_reqs: All requirements, to follow references through.
        candidate_impl: All test cases, whose references count as their requirements'.
        prefix: Prefix of the IDs to find, e.g. "UR".
        path: The IDs followed to reach `req`. Only those make a cycle: an ID reached along
            several paths (e.g. FR1 -> UR1 and FR1 -> FR2 -> UR1) is not one.

    Returns:
        The IDs found.

    Raises:
        RuntimeError: The references are circular.
    """
    result: set[str] = set()

    req_impl = next((i for i in candidate_impl if req.id in i.ids), None)
    ref_ids = _get_ids_for_req(req, req_impl)
    for _id in ref_ids:
        # Ensure no cycles, or we'll be stuck in an infinite loop
        if _id in path:
            raise RuntimeError(f"Circular reference detected, {_id} has already been seen")

        if _id.startswith(prefix):
            result.add(_id)
        else:
            # Traverse referenced (child) requirements to search for more matches
            if referenced_req := next((r for r in candidate_reqs if r.id == _id), None):
                result.update(
                    _traverse_ids_for_req(referenced_req, candidate_reqs, candidate_impl, prefix, path | {_id})
                )
    return result


def create_traceability_matrix(
    reqs: list[Requirement],
    test_cases: list[TestCase],
    categories: list[tuple[str, str]] | None = None,
    base_prefix: str | None = None,
    max_col_width: int = 100,
) -> str:
    """Create a traceability matrix in Markdown format.

    If categories are given, the matrix has an extra column per category, listing the IDs with
    the category's prefix that each requirement references, directly or through other requirements.

    Args:
        reqs: Requirements to include.
        test_cases: Test cases of the requirements.
        categories: (title, prefix) of each extra column. None for no extra columns.
        base_prefix: Only list the requirements with this prefix. None to list all.
        max_col_width: Widest padding of a column.

    Returns:
        Traceability matrix table in Markdown format.
    """
    header = ["ID", "Description", "References", "Test case"]

    if categories:
        header = [*(c[0] for c in categories), *header]

    rows: list[list[str]] = []
    for req in sorted(reqs, key=lambda x: x.id):
        # If base_prefix is given, table only relates to matching requirements
        if base_prefix and not req.id.startswith(base_prefix):
            continue

        req_test_case = next((i for i in test_cases if req.id in i.ids), None)

        category_entries: list[str] = []
        used_prefix_ids: set[str] = set()
        if categories:
            for _, prefix in categories:
                prefix_ids = _traverse_ids_for_req(req, reqs, test_cases, prefix)
                if prefix_ids:
                    category_entries.append(", ".join(sorted(prefix_ids)))
                    used_prefix_ids.update(prefix_ids)
                else:
                    category_entries.append("-")

        rows.append(
            [
                *category_entries,
                str(req.id),
                req.desc,
                # Remove the used prefixes from the list of references
                ", ".join(sorted(_get_ids_for_req(req, req_test_case) - used_prefix_ids)),
                str(req_test_case.testcase_id if req_test_case and req_test_case.testcase_id else ""),
            ]
        )

    return _render_md_table(header, rows, max_col_width=max_col_width)


def _unique_test_cases(test_cases: list[TestCase]) -> dict[str, TestCase]:
    """Give the first test case with each test case ID, sorted by ID; ones without an ID are left out."""
    with_id = [(tc.testcase_id, tc) for tc in test_cases if tc.testcase_id]
    report_test_cases: dict[str, TestCase] = {}
    for testcase_id, test_case in sorted(with_id, key=lambda x: x[0]):
        report_test_cases.setdefault(testcase_id, test_case)
    return report_test_cases


def create_test_overview_report(test_cases: list[TestCase]) -> str:
    """Create a Markdown table of the test cases, with description and pass or fail, ordered by ID."""
    return (
        _render_md_table(
            ["Test case", "Description", "Passed"],
            [
                [testcase_id, tc.desc, "Pass" if tc.passed else "**Fail**"]
                for testcase_id, tc in _unique_test_cases(test_cases).items()
            ],
        )
        + "\n\n"
    )


def create_test_case_report(reqs: list[Requirement], test_cases: list[TestCase]) -> str:
    """Create a Markdown section per test case, with its requirements, test data and source code."""
    report = ""

    report_test_cases = _unique_test_cases(test_cases)

    # Print individual test cases
    for test_case in report_test_cases.values():
        impl_reqs = [s for s in reqs if s.id in test_case.ids]

        testdata_table = ""
        if test_case.io:
            rows = [[str(io_input), str(io_output)] for io_input, io_output in test_case.io]
            testdata_table = _render_md_table(["Input", "Output"], rows)

        report += f"## {test_case.testcase_id}{': ' + test_case.desc if test_case.desc else ''}\n\n"

        report += _render_md_table(["ID", "Description"], [[req.id, req.desc] for req in impl_reqs])
        report += "\n\n"

        if testdata_table:
            report += f"### Test data:\n\n{testdata_table}\n"

        if test_case.func_src:
            report += "### Test case implementation:\n\n"
            report += f"```python\n{test_case.func_src}```\n\n"

    return report


RISK_ITEM_TEMPLATE = """
  <thead>
    <tr>
      <th class="nydok-risk-id" rowspan="2" style="text-align: center;">{_id}</th>
      <th class="nydok-risk-header nydok-risk-prior" colspan="3" style="text-align: center;">Prior</th>
      <th class="nydok-risk-header nydok-risk-residual" colspan="3" style="text-align: center;">Residual</th>
    </tr>
    <tr>
      <th class="nydok-risk-category nydok-risk-prior" style="text-align: center;">Prob.</th>
      <th class="nydok-risk-category nydok-risk-prior" style="text-align: center;">Severity</th>
      <th class="nydok-risk-category nydok-risk-prior" style="text-align: center;">Detect.</th>
      <th class="nydok-risk-category nydok-risk-residual" style="text-align: center;">Prob.</th>
      <th class="nydok-risk-category nydok-risk-residual" style="text-align: center;">Severity</th>
      <th class="nydok-risk-category nydok-risk-residual" style="text-align: center;">Detect.</th>
    </tr>
    <tr>
        {prior_probability}
        {prior_severity}
        {prior_detectability}
        {residual_probability}
        {residual_severity}
        {residual_detectability}
    </tr>
    <tr>
        <th>Risk priority</th>
        {prior_risk_priority}
        {residual_risk_priority}
    </tr>
  </thead>
  <tbody>
    <tr>
      <th class="nydok-risk-text-header" style="padding: 10px;">Description</th>
      <td class="nydok-risk-text" style="padding: 10px;" colspan="6">{description}</td>
    </tr>
    <tr>
      <th class="nydok-risk-text-header" style="padding: 10px;">Consequence</th>
      <td class="nydok-risk-text" style="padding: 10px;" colspan="6">{consequence}</td>
    </tr>
    <tr>
      <th class="nydok-risk-text-header" style="padding: 10px;">Mitigation</th>
      <td class="nydok-risk-text" style="padding: 10px;" colspan="6">{mitigation}</td>
    </tr>
  </tbody>
"""


def create_risk_report(
    risk_assessments: dict[str, RiskAssessment],
) -> str:
    """Create an HTML table of the risk assessments, sorted by ID ("" if there are none)."""
    report = ""

    def get_risk_item(item: str, desc: bool = False, _class: str = "", colspan: str = "1") -> str:
        """Create a <td> for a risk item.

        Args:
            item: 'low', 'medium' or 'high'.
            desc: Whether color scale is descending, e.g. 'high' is green. Defaults to False.
            _class: HTML class to add to row. Defaults to "".
            colspan: HTML colspan attribute value. Defaults to "1".

        Returns:
            A HTML string with <td> element.
        """
        assert item in ["low", "medium", "high"]

        color = [
            # (font color, background color)
            ("#3CA03F", "#C6EFCE"),
            ("#9C6500", "#FFEB9C"),
            ("#FF2020", "#FFC7CE"),
        ]
        color_classes = ["green", "orange", "red"]

        # Used to lookup index of item in above color lists
        color_index = ["low", "medium", "high"]

        color_item_index = list(reversed(color_index)).index(item) if desc else color_index.index(item)
        font_color, background_color = color[color_item_index]
        item_class = color_classes[color_item_index]

        item_classes = ["nydok-risk-score", f"nydok-risk-score-{item_class}"]
        if _class:
            item_classes.append(_class)

        style = f"color: {font_color}; background-color: {background_color}; text-align: center; min-width: 65px;"
        return f'<td colspan={colspan} class="{" ".join(item_classes)}" style="{style}">{item.capitalize()}</td>'

    if risk_assessments:
        report += '<table class="nydok-risk-assessment">'
        for ra in sorted(risk_assessments.values(), key=lambda x: x.id):
            mitigation_text = ra.mitigation

            # Add requirement ids to mitigation text if present
            if ra.mitigation_requirement_ids:
                if not mitigation_text.endswith("."):
                    mitigation_text += "."
                mitigation_text += (
                    " Mitigation requirement IDs: " + ", ".join(sorted(ra.mitigation_requirement_ids)) + "."
                )

            report += RISK_ITEM_TEMPLATE.format(
                _id=ra.id,
                description=ra.description,
                consequence=ra.consequence,
                mitigation=mitigation_text,
                prior_probability=get_risk_item(ra.prior_probability, _class="nydok-risk-prior"),
                prior_severity=get_risk_item(ra.prior_severity, _class="nydok-risk-prior"),
                prior_detectability=get_risk_item(ra.prior_detectability, desc=True, _class="nydok-risk-prior"),
                prior_risk_priority=get_risk_item(ra.prior_risk_priority, colspan="3", _class="nydok-risk-prior"),
                residual_probability=get_risk_item(ra.residual_probability, _class="nydok-risk-residual"),
                residual_severity=get_risk_item(ra.residual_severity, _class="nydok-risk-residual"),
                residual_detectability=get_risk_item(
                    ra.residual_detectability, desc=True, _class="nydok-risk-residual"
                ),
                residual_risk_priority=get_risk_item(
                    ra.residual_risk_priority, colspan="3", _class="nydok-risk-residual"
                ),
            )
        report += "</table>"

    return report


def create_codereview_report(
    repo_path: str,
    to_ref: str | None = None,
    from_ref: str | None = None,
) -> str:
    """Create a report of the merge requests merged in a commit range, with their approvers.

    Args:
        repo_path: GitLab path of the project, e.g. "my-group/my-project".
        to_ref: Git ref ending the commit range. If not given, the repository's default branch.
        from_ref: Git ref starting the commit range (excluded). If not given, all history up to
            `to_ref`.

    Returns:
        The report, in Markdown.
    """
    # Get commits from to_ref so we can figure out which merge requests
    # were merged into the commit range. If a from_ref is given, only merge requests
    # merged since the from_ref are considered.

    commits = get_commits_for_ref(repo_path, to_ref, from_ref=from_ref)

    since_prev_text = f" since version {from_ref}" if from_ref else ""
    report = f"## Approved code changes{since_prev_text}\n\n"

    mrs = fetch_mergerequests(repo_path)

    # Filter the merge requests against the commits
    to_include_mrs = [mr for mr in mrs if mr["merge_commit_sha"] in set(commits)]

    report += _render_md_table(
        ["Commit", "Title", "Date", "Author", "Approver(s)"],
        [
            [
                mr["merge_commit_sha"][:7],
                mr["title"],
                mr["merged_at"][:10],
                mr["author"],
                mr["approved_by"],
            ]
            for mr in to_include_mrs
        ],
    )

    return report


# ANSI escape sequences, e.g. terminal colours
RE_ANSI = re.compile(r"\x1B\[[0-9;]*[ABCDEFGHJKSTfmnsulh]")


def create_pipeline_logs_report(repo_path: str, pipeline_id: int, job_names: list[str] | None = None) -> str:
    """Create a Markdown section per job in a GitLab pipeline, with the job's log."""
    logs = get_pipeline_logs(repo_path, pipeline_id, job_names=job_names)

    report = ""
    for job_name, job_log in sorted(logs.items()):
        job_log = RE_ANSI.sub("", job_log.replace("\n", "<br>"))
        report += f"## {job_name}\n\n"
        report += f'<div class="codehilite"><pre><code>\n{job_log}\n</code></pre></div>\n\n'

    return report
