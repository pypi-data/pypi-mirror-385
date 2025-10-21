# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module managing configuration paths visible to qBraid environments.

"""
import logging
from pathlib import Path
from typing import Callable

from qbraid_core.system.exceptions import QbraidSystemError
from qbraid_core.system.magic import add_magic_file, remove_magic_file
from qbraid_core.system.packages import (
    add_config_path_to_site_packages,
    get_active_site_packages_path,
    get_venv_site_packages_path,
    remove_config_path_from_site_packages,
)

from .paths import get_default_envs_paths
from .validate import is_valid_slug

logger = logging.getLogger(__name__)


def _operate_on_all_envs(operation: Callable[[Path], None]) -> None:
    """
    Helper function to perform a given operation on all valid qBraid environments.

    Args:
        operation (Callable[[Path], None]): A function that takes a site-packages path and
            performs an operation. Log any errors that occur during the operation.
    """
    qbraid_env_paths: list[Path] = get_default_envs_paths()
    active_site_packages = get_active_site_packages_path()
    hit_active = False

    for env_path in qbraid_env_paths:
        for entry in env_path.iterdir():
            if entry.is_dir() and is_valid_slug(entry.name):
                try:
                    site_packages_path = get_venv_site_packages_path(entry / "pyenv")
                    hit_active = hit_active or site_packages_path == active_site_packages
                    operation(site_packages_path)
                except QbraidSystemError as err:
                    logger.debug(
                        "Failed to apply magic config at path %s: %s", site_packages_path, err
                    )

    if not hit_active:
        try:
            operation(active_site_packages)
        except QbraidSystemError as err:
            logger.debug("Failed to apply magic config at path %s: %s", site_packages_path, err)


def add_magic_config() -> None:
    """
    Add config path file to all qBraid environments site packages directories,
    and add qbraid_magic file to qBraid config path.

    """
    _operate_on_all_envs(add_config_path_to_site_packages)
    add_magic_file()


def remove_magic_config() -> None:
    """
    Remove config path file from all qBraid environments site packages directories,
    and remove qbraid_magic file from qBraid config path.
    """
    _operate_on_all_envs(remove_config_path_from_site_packages)
    remove_magic_file()
