"""Python-Markdown extension for nydok specifications, enabled in mkdocs.yml as `nydok.markdown_ext:nydok`."""

from .markdown_nydok import NydokExtension

# The name mkdocs.yml refers to
nydok = NydokExtension

__all__ = ["NydokExtension", "nydok"]
