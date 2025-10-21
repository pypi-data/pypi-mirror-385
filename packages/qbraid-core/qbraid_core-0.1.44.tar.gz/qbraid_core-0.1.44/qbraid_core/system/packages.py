# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for serving information about Python packages.

"""
import ast
import logging
import site
import subprocess
import sys
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from typing import Optional, Union

from qbraid_core.config import USER_CONFIG_PATH

from .exceptions import QbraidSystemError
from .executables import (
    get_active_python_path,
    get_python_version_from_cfg,
    get_python_version_from_exe,
    python_paths_equivalent,
)

logger = logging.getLogger(__name__)


def get_venv_site_packages_path(venv_path: Union[str, Path]) -> Path:
    """
    Determines the site-packages directory for a given virtual environment in an OS-agnostic manner.
    Automatically selects the Python version if a single version is present in the 'lib' directory.
    If multiple versions are detected, it attempts to determine the correct version through
    configuration files or the Python executable.

    Args:
        venv_path (Union[str, pathlib.Path]): The path to the virtual environment directory.

    Returns:
        A Path object pointing to the site-packages directory, or None if unable to determine.

    Raises:
        QbraidSystemError: If an error occurs while determining the site-packages path.
    """
    venv_path = Path(venv_path)

    if sys.platform == "win32":
        return venv_path / "Lib" / "site-packages"

    python_dirs = sorted(venv_path.glob("lib/python*"))
    if not python_dirs:
        raise QbraidSystemError("No Python directories found in the virtual environment.")

    if len(python_dirs) == 1:
        return python_dirs[0] / "site-packages"

    python_version = get_python_version_from_cfg(venv_path)
    python_version = python_version or get_python_version_from_exe(venv_path)

    if not python_version:
        raise QbraidSystemError("Unable to determine Python version from the virtual environment.")

    major_minor_version = ".".join(python_version.split(".")[:2])
    lib_python_dir = venv_path / f"lib/python{major_minor_version}"
    return lib_python_dir / "site-packages"


def get_active_site_packages_path(python_path: Optional[Path] = None) -> Path:
    """
    Retrieves the site-packages path of the current Python environment,
    respecting active virtual environments, as well.

    """

    current_python_path = Path(sys.executable)
    shell_python_path = python_path or get_active_python_path()

    if python_paths_equivalent(shell_python_path, current_python_path):
        site_packages_paths = [Path(path) for path in site.getsitepackages()]

    else:
        try:
            result = subprocess.run(
                [shell_python_path, "-c", "import site; print(site.getsitepackages())"],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as err:
            raise QbraidSystemError(
                f"Failed to get user site-packages directory from {shell_python_path}."
            ) from err
        except FileNotFoundError as err:
            raise QbraidSystemError(f"Python executable not found at {shell_python_path}.") from err

        paths = ast.literal_eval(result.stdout.strip())
        site_packages_paths = [Path(path) for path in paths]

    # Common logic for finding the correct site-packages path
    if len(site_packages_paths) == 1:
        return site_packages_paths[0]

    # Base path of the Python environment
    shell_base_path = shell_python_path.parent.parent
    sys_base_path = current_python_path.parent.parent

    base_paths = [shell_base_path]
    if shell_base_path != sys_base_path:
        base_paths.append(sys_base_path)

    # Find the site-packages path that is within the same environment
    for base_path in base_paths:
        for path in site_packages_paths:
            if base_path in path.parents:
                return path

    raise QbraidSystemError("Failed to find site-packages path.")


def get_local_package_path(package: str) -> Path:
    """Retrieves the local path of a package."""
    try:
        site_packages_path = get_active_site_packages_path()
        return site_packages_path / package
    except (PackageNotFoundError, ModuleNotFoundError) as err:
        raise QbraidSystemError(f"{package} not found in the current environment.") from err


def extract_include_sys_site_pkgs_value(file_path: Union[str, Path]) -> Optional[bool]:
    """Extracts the value of the 'include-system-site-packages' setting from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("include-system-site-packages"):
                    parts = line.strip().split("=")
                    if len(parts) == 2:
                        value = parts[1].strip().lower()
                        if value == "true":
                            return True
                        if value == "false":
                            return False
                    break
    except FileNotFoundError as err:
        raise FileNotFoundError("The specified file was not found.") from err
    except Exception as err:
        raise QbraidSystemError("An error occurred while reading the file.") from err

    return None


def set_include_sys_site_pkgs_value(value: bool, file_path: Union[str, Path]) -> None:
    """Sets the value of the 'include-system-site-packages' setting in a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Track whether the target line was found
        found = False
        for i, line in enumerate(lines):
            if line.startswith("include-system-site-packages"):
                lines[i] = f"include-system-site-packages = {str(value).lower()}\n"
                found = True
                break

        if not found:
            raise ValueError(
                "The 'include-system-site-packages' setting was not found in the file."
            )

        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(lines)

    except FileNotFoundError as err:
        raise FileNotFoundError("The specified file was not found.") from err
    except Exception as err:
        raise QbraidSystemError("An error occurred while updating the file") from err


def add_config_path_to_site_packages(site_packages_path: Optional[Union[str, Path]] = None) -> None:
    """
    Adds the parent directory of the USER_CONFIG_PATH to the Python site-packages
    via a .pth file, allowing Python to recognize custom modules located in this directory.

    Raises:
        QbraidSystemError: If the .pth file cannot be written.
    """
    directory_path = str(Path(USER_CONFIG_PATH).parent)

    site_packages_path = site_packages_path or get_active_site_packages_path()

    pth_file = Path(site_packages_path) / "qbraid_config.pth"

    try:
        with open(pth_file, "w", encoding="utf-8") as file:
            file.write(directory_path + "\n")

        logger.debug("Successfully wrote path %s to %s", directory_path, pth_file)
    except Exception as err:
        raise QbraidSystemError(f"Failed to write path to {pth_file}.") from err


def remove_config_path_from_site_packages(
    site_packages_path: Optional[Union[str, Path]] = None,
) -> None:
    """
    Removes the custom .pth file from the Python site-packages directory,
    effectively undoing the addition of a custom module directory to Python's search path.

    Raises:
        FileNotFoundError: If the .pth file does not exist in the site-packages directory.
        QbraidSystemError: For other unforeseen errors that may occur during file deletion.
    """
    site_packages_path = site_packages_path or get_active_site_packages_path()

    pth_file = Path(site_packages_path) / "qbraid_config.pth"

    try:
        if pth_file.exists():
            pth_file.unlink()
            logger.debug("Successfully removed %s", pth_file)
        else:
            raise FileNotFoundError(f"{pth_file} does not exist.")

    except Exception as err:
        raise QbraidSystemError(f"Failed to remove {pth_file}.") from err


__all__ = [
    "add_config_path_to_site_packages",
    "get_active_site_packages_path",
    "get_local_package_path",
    "get_venv_site_packages_path",
    "remove_config_path_from_site_packages",
]
