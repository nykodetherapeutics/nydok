import re
from typing import Dict, List, Optional, Set, Tuple

from .gitlab import fetch_mergerequests, get_commits_for_ref, get_pipeline_logs
from .schema import Requirement, RiskAssessment, TestCase


def _render_md_table(header, rows, max_col_width=100):
    def _md_table_row(cols: List[str], col_widths: List[int]):

        return " | ".join(
            # Pad each entry with col_widths
            [
                "{h:<{w}}".format(
                    h=cols[i],
                    w=col_widths[i],
                )
                for i in range(0, len(cols))
            ]
        )

    # Find max col size per column
    max_col_size: List[int] = []
    for idx in range(0, len(header)):
        max_col_size.append(min(max([len(r[idx]) for r in [header] + rows]), max_col_width))

    result = ""
    result += _md_table_row(header, max_col_size) + "\n"
    result += (
        _md_table_row(["-" * max_col_size[i] for i in range(0, len(header))], max_col_size) + "\n"
    )
    for row in rows:
        result += _md_table_row(row, max_col_size) + "\n"

    return result


def _get_ids_for_req(req: Requirement, req_impl: Optional[TestCase] = None) -> Set[str]:
    ref_ids: Set[str] = set()
    if req.ref_ids:
        ref_ids.update(req.ref_ids)
    if req_impl and req_impl.ref_ids:
        ref_ids.update(req_impl.ref_ids)

    return ref_ids


def _traverse_ids_for_req(
    req: Requirement,
    candidate_reqs: List[Requirement],
    candidate_impl: List[TestCase],
    prefix: str,
    seen: Optional[Set[str]] = None,
) -> Set[str]:
    result: Set[str] = set()

    if seen is None:
        seen = set()

    req_impl = next((i for i in candidate_impl if req.id in i.ids), None)
    ref_ids = _get_ids_for_req(req, req_impl)
    for _id in ref_ids:

        # Ensure no cycles, or we'll be stuck in an infinite loop
        if _id in seen:
            raise RuntimeError(f"Circular reference detected, {_id} has already been seen")
        seen.add(_id)

        if _id.startswith(prefix):
            result.add(_id)
        else:
            # Traverse referenced (child) requirements to search for more matches
            if referenced_req := next((r for r in candidate_reqs if r.id == _id), None):
                result.update(
                    _traverse_ids_for_req(
                        referenced_req, candidate_reqs, candidate_impl, prefix, seen
                    )
                )
    return result


def create_traceability_matrix(
    reqs: List[Requirement],
    test_cases: List[TestCase],
    categories: Optional[List[Tuple[str, str]]] = None,
    base_prefix: Optional[str] = None,
    max_col_width=100,
) -> str:
    """Creates a traceability matrix in markdown format.

    If categories is provided, the matrix will contain additional columns,
    one for each category, linking the different requirements together
    through their references.

    Args:
        reqs: Requirements to include.
        test_cases: TestCases for the Requirements
        categories: List of tuples, containing title and prefix that defines a category.
                    If none, all requirements are listed.
        base_prefix: Which requirement prefix to base the matrix upon. Required if
                     categories is provided.
        max_col_width: Maximum width of each column in the table.


    Returns:
        Traceability matrix table in Markdown format.
    """
    header = ["ID", "Description", "References", "Test case"]

    if categories:
        header = [c[0] for c in categories] + header

    rows: List[List[str]] = []
    for req in sorted(reqs, key=lambda x: x.id):
        # If base_prefix is given, table only relates to matching requirements
        if base_prefix and not req.id.startswith(base_prefix):
            continue

        req_test_case = next((i for i in test_cases if req.id in i.ids), None)

        category_entries: List[str] = []
        used_prefix_ids: Set[str] = set()
        if categories:
            for _, prefix in categories:
                prefix_ids = _traverse_ids_for_req(req, reqs, test_cases, prefix)
                if prefix_ids:
                    category_entries.append(", ".join(sorted(prefix_ids)))
                    used_prefix_ids.update(prefix_ids)
                else:
                    category_entries.append("-")

        rows.append(
            category_entries
            + [
                str(req.id),
                req.desc,
                # Remove the used prefixes from the list of references
                ", ".join(sorted(_get_ids_for_req(req, req_test_case) - used_prefix_ids)),
                str(
                    req_test_case.testcase_id if req_test_case and req_test_case.testcase_id else ""
                ),
            ]
        )

    report = _render_md_table(header, rows, max_col_width=max_col_width)

    return report


def create_test_overview_report(
    reqs: List[Requirement],
    test_cases: List[TestCase],
) -> str:

    report = ""

    # TestCases are repeated if duplicated IDs, use first one
    report_test_cases: Dict[str, TestCase] = {}
    for test_case in sorted(test_cases, key=lambda x: x.testcase_id):
        if test_case.testcase_id not in report_test_cases:
            report_test_cases[test_case.testcase_id] = test_case

    # Print summary table
    report += (
        _render_md_table(
            ["Test case", "Description", "Passed"],
            [
                [
                    tc.testcase_id,
                    tc.desc,
                    "Pass" if tc.passed else "**Fail**",
                ]
                for tc in report_test_cases.values()
            ],
        )
        + "\n\n"
    )

    return report


def create_test_case_report(
    reqs: List[Requirement],
    test_cases: List[TestCase],
) -> str:

    report = ""

    # TestCases are repeated if duplicated IDs, use first one
    report_test_cases: Dict[str, TestCase] = {}
    for test_case in sorted(test_cases, key=lambda x: x.testcase_id):
        if test_case.testcase_id not in report_test_cases:
            report_test_cases[test_case.testcase_id] = test_case

    # Print individual test cases
    for test_case in report_test_cases.values():
        impl_reqs = [s for s in reqs if s.id in test_case.ids]

        testdata_table = ""
        if test_case.io:

            rows: List[List[str]] = list()
            for io_entry in test_case.io:
                rows.append([str(io_entry[0]), str(io_entry[1])])

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
      <th class="nydok-risk-id" rowspan="3" style="text-align: center;">{_id}</th>
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
"""  # noqa: E501


def create_risk_report(
    risk_assessments: Dict[str, RiskAssessment],
) -> str:
    """
    Create a risk report from a list of risk assessments as a HTML table.

    The table is sorted by risk assessment ID.

    Args:
        risk_assessments: A dictionary of risk assessments, given their ID.

    Returns:
        A HTML table with the risk assessments.
    """
    report = ""

    def get_risk_item(item: str, desc: bool = False, _class: str = "", colspan: str = "1") -> str:
        """Creates a <td> for a risk item.

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

        color_item_index = (
            list(reversed(color_index)).index(item) if desc else color_index.index(item)
        )
        font_color, background_color = color[color_item_index]
        item_class = color_classes[color_item_index]

        item_classes = ["nydok-risk-score", f"nydok-risk-score-{item_class}"]
        if _class:
            item_classes.append(_class)

        style = (
            f"color: {font_color}; background-color: {background_color}; "
            f"text-align: center; min-width: 65px;"
        )
        return (
            f'<td colspan={colspan} class="{" ".join(item_classes)}"'
            f' style="{style}">{item.capitalize()}</td>'
        )

    if risk_assessments:
        report += '<table class="nydok-risk-assessment">'
        for ra in sorted(risk_assessments.values(), key=lambda x: x.id):

            mitigation_text = ra.mitigation

            # Add requirement ids to mitigation text if present
            if ra.mitigation_requirement_ids:
                if not mitigation_text.endswith("."):
                    mitigation_text += "."
                mitigation_text += (
                    " Mitigation requirement IDs: "
                    + ", ".join(sorted(ra.mitigation_requirement_ids))
                    + "."
                )

            report += RISK_ITEM_TEMPLATE.format(
                _id=ra.id,
                description=ra.description,
                consequence=ra.consequence,
                mitigation=mitigation_text,
                prior_probability=get_risk_item(ra.prior_probability, _class="nydok-risk-prior"),
                prior_severity=get_risk_item(ra.prior_severity, _class="nydok-risk-prior"),
                prior_detectability=get_risk_item(
                    ra.prior_detectability, desc=True, _class="nydok-risk-prior"
                ),
                prior_risk_priority=get_risk_item(
                    ra.prior_risk_priority, colspan="3", _class="nydok-risk-prior"
                ),
                residual_probability=get_risk_item(
                    ra.residual_probability, _class="nydok-risk-residual"
                ),
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
    to_ref: Optional[str] = None,
    from_ref: Optional[str] = None,
) -> str:
    """Create a report of code changes and their approval status since a given commit.

    Args:
        repo_path: Path to the repository to generate the report for.
        to_ref: The commit to generate the report for. If not given, repository
            HEAD is used.
        from_ref: The commit to generate the report from. If not given, all
            commits up until `to_ref` are considered.

    Returns:
        A markdown formatted string containing the report.
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


def create_pipeline_logs_report(
    repo_path: str, pipeline_id: int, job_names: Optional[List[str]] = None
) -> str:

    logs = get_pipeline_logs(repo_path, pipeline_id, job_names=job_names)

    def ansi_to_plain(ansi):
        return re.sub(r"\x1B\[[0-9;]*[ABCDEFGHJKSTfmnsulh]", "", ansi)

    report = ""
    for job_name, job_log in sorted(logs.items()):

        job_log = ansi_to_plain(job_log.replace("\n", "<br>"))
        report += f"## {job_name}\n\n"
        report += f'<div class="codehilite"><pre><code>\n{job_log}\n</code></pre></div>\n\n'

    return report
