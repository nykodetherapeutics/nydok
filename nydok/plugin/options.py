"""Access to nydok's settings, each given as a command line option or an ini setting."""

import pytest


def get_option(config: pytest.Config, name: str) -> str | None:
    """Return setting `name` from the command line, else from the ini file."""
    return config.getoption(name) or config.getini(name) or None
