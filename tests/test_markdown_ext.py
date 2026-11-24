import markdown

from nydok import testcase


def _render(text: str) -> str:
    # Loaded by the name used in mkdocs.yml. Newlines between tags dropped, to compare rows.
    return markdown.markdown(text, extensions=["nydok.markdown_ext:nydok"]).replace("\n", "")


@testcase("FR290")
def test_requirements_table():
    html = _render("# Heading\n\n- FR001: First requirement\n- FR002: Second requirement\n")

    assert '<table class="nydok-requirements">' in html
    assert (
        '<tr><td class="req-id">FR001</td><td class="req-desc">First requirement</td></tr>'
        '<tr><td class="req-id">FR002</td><td class="req-desc">Second requirement</td></tr>'
    ) in html
    assert "req-refs" not in html


@testcase("FR291")
def test_requirements_table_references():
    html = _render("- FR001 [UR001,UR002]: First requirement\n- FR002: Second requirement\n")

    assert (
        '<tr><td class="req-id">FR001</td><td class="req-refs">UR001 UR002</td>'
        '<td class="req-desc">First requirement</td></tr>'
        '<tr><td class="req-id">FR002</td><td class="req-refs"></td><td class="req-desc">Second requirement</td></tr>'
    ) in html
