"""Python-Markdown extension rendering requirement lists as tables, for documentation sites."""

import re
from xml.etree.ElementTree import Element, SubElement

from markdown import Markdown
from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension

from ..patterns import DEFAULT_REQ_PATTERN


class NydokRequirementProcessor(BlockProcessor):
    """Render a block of requirement lines (e.g. `- FR001 [UR001]: Description`) as a table."""

    RE = re.compile(DEFAULT_REQ_PATTERN)

    def test(self, parent: Element, block: str) -> bool:  # noqa: ARG002
        """Check whether a block starts with a requirement."""
        return bool(self.RE.match(block))

    def run(self, parent: Element, blocks: list[str]) -> None:
        """Render the requirements in the first block as a table, dropping its other lines."""
        items = self.get_items(blocks.pop(0))

        req_table = SubElement(parent, "table")
        req_table.attrib["class"] = "nydok-requirements"

        # The references column is only shown if some requirement has references
        has_refs = any(item.get("refs") for item in items)
        for item in items:
            tr = SubElement(req_table, "tr")
            req_td = SubElement(tr, "td")
            req_td.text = item["req_id"]
            req_td.attrib["class"] = "req-id"
            if has_refs:
                ref_td = SubElement(tr, "td")
                ref_td.text = " ".join((item["refs"] or "").split(","))
                ref_td.attrib["class"] = "req-refs"
            desc_td = SubElement(tr, "td")
            desc_td.text = item["desc"]
            desc_td.attrib["class"] = "req-desc"

    def get_items(self, block: str) -> list[dict[str, str | None]]:
        """Parse the requirement lines of a block; `refs` is None for a requirement without references."""
        return [m.groupdict() for line in block.split("\n") if (m := self.RE.match(line))]


class NydokExtension(Extension):
    """Nydok extension for Python-Markdown."""

    # Name set by Python-Markdown's API
    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802
        """Register the requirement processor."""
        md.parser.blockprocessors.register(NydokRequirementProcessor(md.parser), "nydok", 100)
        md.registerExtension(self)
