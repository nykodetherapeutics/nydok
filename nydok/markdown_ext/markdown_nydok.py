import re
import xml.etree.ElementTree as etree

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension


class NydokRequirementProcessor(BlockProcessor):
    """Process nydok requirements in format:

    - FR001 [UR001]: The system must be able to do something
    """

    REQ_PATTERN = r"- (?P<req_id>[A-Z]+[0-9]+)( \[(?P<refs>[A-Z,0-9]+)\])?: (?P<desc>.*)"

    def __init__(self, parser):
        super().__init__(parser)
        self.RE = re.compile(self.REQ_PATTERN)

    def test(self, parent, block):
        return bool(self.RE.match(block))

    def run(self, parent, blocks):

        # Check fr multiple items in one block.
        items = self.get_items(blocks.pop(0))

        # This is a new list so create parent with appropriate tag.
        req_table = etree.SubElement(parent, "table")
        req_table.attrib["class"] = "nydok-requirements"

        # Loop through items in block, recursively parsing each with the
        # appropriate parent.

        has_refs = any(item.get("refs") for item in items)
        for item in items:
            # New item. Create li and parse with it as parent
            tr = etree.SubElement(req_table, "tr")
            req_td = etree.SubElement(tr, "td")
            req_td.text = item["req_id"]
            req_td.attrib["class"] = "req-id"
            if has_refs:
                ref_td = etree.SubElement(tr, "td")
                ref_td.text = " ".join(item["refs"].split(","))
                ref_td.attrib["class"] = "req-refs"
            desc_td = etree.SubElement(tr, "td")
            desc_td.text = item["desc"]
            desc_td.attrib["class"] = "req-desc"

    def get_items(self, block):
        """Break a block into list items."""
        items = []
        for line in block.split("\n"):
            m = self.RE.match(line)
            if m:
                items.append(m.groupdict())
        return items


class NydokExtension(Extension):
    """Nydok extension for Python-Markdown."""

    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(NydokRequirementProcessor(md.parser), "nydok", 100)
        md.registerExtension(self)
