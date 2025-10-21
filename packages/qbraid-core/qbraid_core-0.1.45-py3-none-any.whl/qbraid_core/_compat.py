# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for emitting and disabling warnings at top level.

"""
import warnings

from ._import import LazyLoader
from ._version import __version__
from .exceptions import QbraidException

versions = LazyLoader("versions", globals(), "qbraid_core.system.versions")


def _warn_new_version(local: str, latest: str) -> bool:
    """Returns True if you should warn user about updated package version,
    False otherwise."""
    if not local or local == "dev" or not latest:
        return False

    installed_major, installed_minor = map(int, local.split(".")[:2])
    latest_major, latest_minor = map(int, latest.split(".")[:2])

    return (installed_major, installed_minor) < (latest_major, latest_minor)


def check_version(package: str) -> None:
    """Emits UserWarning if updated package version exists."""
    try:
        local_version = (
            __version__ if package == "qbraid_core" else versions.get_local_package_version(package)
        )
        latest_version = versions.get_latest_package_version(package)

        if _warn_new_version(local_version, latest_version):
            warnings.warn(
                f"You are using {package} version {local_version}, however, version "
                f"{latest_version} is available. To avoid compatibility issues, consider "
                "upgrading.",
                UserWarning,
            )
    except QbraidException:
        pass
