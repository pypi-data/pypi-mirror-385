# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for serving information about system executables.

"""
import logging
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Union

from qbraid_core.system.versions import is_valid_semantic_version

logger = logging.getLogger(__name__)


def _extract_python_version(python_exe: str) -> Union[int, None]:
    """
    Extracts the major version number from a Python version string.

    Args:
        s (str): The string from which to extract the major version number.

    Returns:
        int or None: The major version number if present, otherwise None.
    """
    match = re.search(r"python\s*-?(\d+)(?:\.\d*)?$", python_exe)
    return int(match.group(1)) if match else None


def python_paths_equivalent(path1: Union[str, Path], path2: Union[str, Path]) -> bool:
    """
    Determines if two Python path strings refer to the same version of Python,
    ignoring any minor version numbers and only considering major version equivalency.

    Args:
        path1 (Union[str, Path]): First Python path.
        path2 (Union[str, Path]): Second Python path.

    Returns:
        bool: True if paths are considered equivalent, otherwise False.
    """

    if sys.platform == "win32":
        return str(path1) == str(path2)

    def normalize_python_path(path: Union[str, Path]) -> tuple:
        path = str(path)  # Convert Path to string if needed
        version = _extract_python_version(path)
        normalized_path = re.sub(r"python-?\d+(\.\d+)?$", "python", path)
        return version, normalized_path

    # Normalize both paths
    version1, normalized_path1 = normalize_python_path(path1)
    version2, normalized_path2 = normalize_python_path(path2)

    # Check if paths are equivalent
    paths_equal = normalized_path1 == normalized_path2
    versions_equal = version1 == version2 if version1 and version2 else True

    return paths_equal and versions_equal


def get_active_python_path(verify: bool = False) -> Path:
    """Retrieves the path of the currently active Python interpreter."""
    current_python_path = Path(sys.executable)
    shell_python_path = None

    # Choose command based on operating system
    cmd = ["where", "python"] if sys.platform == "win32" else ["which", "python"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        first_path = result.stdout.strip().splitlines()[0]
        shell_python_path = Path(first_path) if first_path else None
    except subprocess.CalledProcessError as err:
        logger.error("Failed to locate Python interpreter with `which python`: %s", err)

        return current_python_path
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("Unexpected error: %s", err)

        return current_python_path

    if shell_python_path is None:
        return current_python_path

    if verify and not is_valid_python(shell_python_path):
        return current_python_path

    return shell_python_path


def is_exe(fpath: Union[str, Path]) -> bool:
    """
    Return true if fpath is a file we have access to that is executable.

    Args:
        fpath (Union[str, Path]): The file path to check.

    Returns:
        bool: True if the file exists, is not a directory, and is executable; False otherwise.
    """
    try:
        path = Path(fpath)

        if not path.exists() or not path.is_file():
            return False

        # Check access rights
        accessmode = os.F_OK
        if not os.access(path, accessmode):
            return False

        # Check executability based on OS
        if platform.system() == "Windows":
            # On Windows, an executable usually has .exe, .bat, or .cmd extension
            if path.suffix.lower() in [".exe", ".bat", ".cmd"]:
                return True
        else:
            # On Unix-like systems, check the executable flags
            accessmode |= os.X_OK
            if os.access(path, accessmode):
                return any(
                    path.stat().st_mode & x for x in (stat.S_IXUSR, stat.S_IXGRP, stat.S_IXOTH)
                )

    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("Error checking if file is executable: %s", err)

    return False


def is_valid_python(python_path: Union[str, Path]) -> bool:
    """Return true if python_path is a valid Python executable."""
    python_path_str = str(
        python_path
    )  # Ensure python_path is a string for shutil.which and subprocess

    if shutil.which(python_path_str) is None:
        return False

    if sys.platform != "win32" and not is_exe(python_path_str):
        return False

    try:
        output = subprocess.check_output([python_path_str, "--version"], stderr=subprocess.STDOUT)
        return "Python" in output.decode()
    except subprocess.CalledProcessError:
        return False


def get_python_version_from_exe(venv_path: Path) -> Optional[str]:
    """
    Gets the Python version used in the specified virtual environment by executing
    the Python binary within the venv's bin (or Scripts) directory.

    Args:
        venv_path (Path): The path to the virtual environment directory.

    Returns:
        A string representing the Python version (e.g., '3.11.7'), or None if an error occurs.
    """
    # NOTE: coalesce into a unified version extractor

    # Adjust the path to the Python executable depending on the operating system
    python_executable = venv_path / ("Scripts" if sys.platform == "win32" else "bin") / "python"

    try:
        # Run the Python executable with '--version' and capture the output
        result = subprocess.run(
            [str(python_executable), "--version"],
            capture_output=True,
            text=True,
            check=True,
        )

        # Python version info could be in stdout or stderr
        version_output = result.stdout or result.stderr

        # Python 3.11.7 --> 3.11.7
        return version_output.split()[1]

    except subprocess.CalledProcessError as err:
        logger.warning("An error occurred while trying to get the Python version: %s", err)
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.warning("Unexpected error: %s", err)

    return None


def get_python_version_from_cfg(venv_path: Path) -> Optional[str]:
    """
    Reads a pyvenv.cfg file within a given virtual environment directory and extracts
    the major and minor Python version.

    Args:
        venv_path (pathlib.Path): The path to the virtual environment directory.

    Returns:
        A string representing the Python version (e.g., '3.11.7'), or None if
        the version cannot be determined or the pyvenv.cfg file does not exist.
    """
    # NOTE: coalesce into a unified version extractor

    pyvenv_cfg_path = venv_path / "pyvenv.cfg"
    if not pyvenv_cfg_path.exists():
        logger.warning("pyvenv.cfg file not found in the virtual environment: %s", venv_path)
        return None

    try:
        with open(pyvenv_cfg_path, "r", encoding="utf-8") as file:
            for line in file.readlines():
                if line.startswith("version ="):
                    version_full = line.strip().split("=")[1].strip()
                    version_parts = version_full.split(".")
                    return f"{version_parts[0]}.{version_parts[1]}"
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.warning("An error occurred while reading %s: %s", pyvenv_cfg_path, err)

    return None


def get_python_version(executable: Optional[Path] = None) -> str:
    """
    Retrieves the semantic version of the Python executable or the default
    system Python if unspecified.

    Args:
        executable (Optional[Path]): Path to a Python executable or None for system Python.

    Returns:
        str: Semantic version of the Python executable.

    Raises:
        ValueError: If executable is invalid or version is not semantic.
        RuntimeError: If subprocess fails to retrieve the version.
    """

    # NOTE: coalesce into a unified version extractor

    if executable is None or str(executable) == sys.executable:
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    if shutil.which(executable) is None:
        raise ValueError(f"Python executable not found: {executable}")

    if sys.platform != "win32" and not is_exe(executable):
        raise ValueError(f"Invalid Python executable: {executable}")

    try:
        version_result = subprocess.run(
            [str(executable), "--version"], stdout=subprocess.PIPE, text=True, check=True
        )
    except subprocess.CalledProcessError as err:
        raise RuntimeError(f"Failed to get Python version for {executable}") from err

    output = version_result.stdout.strip()
    if not output.lower().startswith("python"):
        raise ValueError(f"Invalid Python executable: {executable}")

    version = output.split()[-1]

    if not is_valid_semantic_version(version):
        raise ValueError(f"Invalid Python version: {version}")

    return version


def is_notebook_environment(python_path: Path) -> bool:
    """
    Check if the specified Python environment has Jupyter Notebook and ipykernel installed.

    Args:
        python_path (Path): The path to the Python executable.

    Returns:
        bool: True if both packages are installed, False otherwise.
    """
    try:
        subprocess.run(
            [str(python_path), "-c", "import notebook; import ipykernel"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def check_python_env(env_path: Path) -> tuple[Optional[str], Optional[Path]]:
    """Check a single environment for the required Python executable and packages."""
    python_path = env_path / ("Scripts" if sys.platform == "win32" else "bin") / "python"
    if not python_path.exists() or not is_notebook_environment(python_path):
        return None, None
    try:
        version = get_python_version(python_path)
        return version, python_path
    except (ValueError, RuntimeError):
        return None, None


def parallel_check_envs(env_paths: list[Path]) -> dict[str, Path]:
    """Check environments in parallel using multiple threads."""
    python_executables = {}
    with ThreadPoolExecutor() as executor:
        future_to_path = {executor.submit(check_python_env, path): path for path in env_paths}
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                version, python_path = future.result()
                if version and python_path:
                    python_executables[version] = python_path
            except Exception as err:  # pylint: disable=broad-exception-caught
                logger.error("%s generated an exception: %s", path, err)
    return python_executables


def get_python_executables(unique_versions: bool = True) -> dict[str, dict[str, Path]]:
    """
    Retrieves Python executables from system and Conda environments that
    have Jupyter Notebook and ipykernel installed. Optionally filters out
    duplicate Python versions across system and Conda environments.

    Args:
        unique_versions (bool): If True, duplicate Python versions are excluded.
            If False, includes all executables, regardless of duplicates.

    Returns:
        dict[str, dict[str, Path]]: Maps 'system' and 'conda' to dictionaries
            of Python versions and executable paths.
    """
    python_executables: dict[str, dict[str, Path]] = {"system": {}, "conda": {}}

    sys_python_path = Path(sys.executable)
    try:
        sys_python_version = get_python_version(sys_python_path)
        python_executables["system"][sys_python_version] = sys_python_path
    except (ValueError, RuntimeError) as err:
        logger.error("Error getting system Python version: %s", err)

    try:
        result = subprocess.run(
            ["conda", "env", "list"], stdout=subprocess.PIPE, text=True, check=True
        )
        lines = result.stdout.strip().split("\n") if result.stdout else []
    except Exception as err:  # pylint: disable=broad-exception-caught
        logging.error("Error getting Conda environments: %s", err)
        lines = []

    try:
        env_paths = [
            Path(line.split()[-1])
            for line in lines
            if line and not line.startswith("#") and len(line.split()) > 1
        ]

        conda_executables = parallel_check_envs(env_paths)
    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.error("Error getting Conda Python executables: %s", err)
        conda_executables = {}

    if unique_versions:
        try:
            seen_versions = set(python_executables["system"].keys())
            seen_versions = {".".join(version.split(".")[:2]) for version in seen_versions}
            for version, path in conda_executables.items():
                major_minor = ".".join(version.split(".")[:2])
                if major_minor not in seen_versions:
                    python_executables["conda"][version] = path
                    seen_versions.add(major_minor)
        except Exception as err:  # pylint: disable=broad-exception-caught
            logger.error("Error filtering unique Python versions: %s", err)

    else:
        python_executables["conda"] = conda_executables

    return python_executables


__all__ = [
    "get_active_python_path",
    "get_python_version_from_cfg",
    "get_python_version_from_exe",
    "is_exe",
    "is_valid_python",
    "python_paths_equivalent",
]
