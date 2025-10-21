# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module defining package version.
"""

import re
from pathlib import Path
from typing import Optional


def _get_version_from_pyproject() -> Optional[str]:
    """
    Read version from pyproject.toml.

    Returns:
        Version string if found, None otherwise.
    """
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if not pyproject_path.exists():
            return None

        content = pyproject_path.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if match:
            return match.group(1)
    except Exception:  # pylint: disable=broad-except
        pass
    return None


__version__ = _get_version_from_pyproject() or "dev"
__version_tuple__ = tuple(int(part) if part.isdigit() else part for part in __version__.split("."))

__all__ = ["__version__", "__version_tuple__"]
