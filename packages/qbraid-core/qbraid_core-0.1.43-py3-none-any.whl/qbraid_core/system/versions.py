# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for extracting version information from package metadata.

"""
import importlib.metadata
import json
import logging
import operator
import pathlib
import re
import subprocess
import sys
from typing import Any, Optional, Union

import requests
from packaging.version import InvalidVersion, Version, parse

from qbraid_core.exceptions import QbraidChainedException

from .exceptions import InvalidVersionError, QbraidSystemError, VersionNotFoundError

if sys.version_info >= (3, 11):
    import tomllib

    MODE = "rb"  # pylint: disable=invalid-name
else:
    try:
        import toml as tomllib

        MODE = "r"  # pylint: disable=invalid-name
    except ImportError:
        tomllib = None
        MODE = "r"  # pylint: disable=invalid-name


logger = logging.getLogger(__name__)


def is_valid_semantic_version(v: str) -> bool:
    """
    Returns True if given string represents a valid
    semantic version, False otherwise.

    """
    try:
        Version(v)
        return True
    except ImportError:
        # Fallback to regex matching if packaging is not installed
        semantic_version_pattern = re.compile(
            r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
            r"(-([0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*))?"
            r"(\+([0-9A-Za-z-]+(\.[0-9A-Za-z-]+)*))?$"
        )
        return bool(semantic_version_pattern.match(v))
    except InvalidVersion:
        return False


def _get_version_from_json(package_json_path: Union[str, pathlib.Path]) -> str:
    """Get the version from the package.json file."""
    try:
        with open(package_json_path, "r", encoding="utf-8") as file:
            pkg_json = json.load(file)
            return pkg_json["version"]
    except (FileNotFoundError, KeyError, IOError) as err:
        raise VersionNotFoundError("Unable to find or read package.json") from err


def _simple_toml_version_extractor(file_path: Union[str, pathlib.Path]) -> str:
    """
    Extract the version from a pyproject.toml file using simple string processing.
    This function assumes the version is under [project] and is labeled as version = "x.y.z".
    It is a very basic and fragile implementation and not recommended for general TOML parsing.
    """
    version_pattern = re.compile(r'^version\s*=\s*"([^"]+)"$', re.M)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        match = version_pattern.search(content)
        if match:
            return match.group(1)
        raise ValueError("Version key not found in the TOML content.")
    except FileNotFoundError as err:
        raise VersionNotFoundError("The specified TOML file does not exist.") from err
    except IOError as err:
        raise VersionNotFoundError("An error occurred while reading the TOML file.") from err


def _get_version_from_toml(pyproject_toml_path: Union[str, pathlib.Path]) -> str:
    """Get the version from the pyproject.toml file."""
    if tomllib is None:
        return _simple_toml_version_extractor(pyproject_toml_path)

    try:
        with open(pyproject_toml_path, MODE) as file:
            pyproject_toml = tomllib.load(file)
            return pyproject_toml["project"]["version"]
    except (FileNotFoundError, KeyError, IOError) as err:
        raise VersionNotFoundError("Unable to find or read pyproject.toml") from err


def extract_version(
    file_path: Union[str, pathlib.Path], shorten_prerelease: bool = False, check: bool = False
) -> str:
    """Extract the version from a given package.json or pyproject.toml file.

    Args:
        file_path (Union[str, pathlib.Path]): Path to the package metadata file.
        shorten_prerelease (bool): Whether to shorten the prerelease version.
        check (bool): Whether to check if the version is a valid semantic version.

    Returns:
        str: The version extracted from the file.


    Raises:
        TypeError: If the shorten_prerelease or check arguments are not booleans.
        ValueError: If the file type is not supported.
        InvalidVersionError: If the version is not a valid semantic version.
        VersionNotFoundError: If the version is not found in the file.
    """
    if not isinstance(shorten_prerelease, bool):
        raise TypeError("shorten_prerelease must be a boolean.")

    if not isinstance(check, bool):
        raise TypeError("check must be a boolean.")

    file_path = pathlib.Path(file_path)

    if file_path.suffix == ".json":
        version = _get_version_from_json(file_path)
    elif file_path.suffix == ".toml":
        version = _get_version_from_toml(file_path)
    else:
        raise ValueError(
            "Unsupported file type. Only package.json and pyproject.toml are supported."
        )

    if shorten_prerelease:
        version = version.replace("-alpha.", "a").replace("-beta.", "b").replace("-rc.", "rc")

    if check and not is_valid_semantic_version(version):
        raise InvalidVersionError(f"Invalid semantic version: {version}")

    return version


def find_largest_version(version_list: list[str]) -> str:
    """
    Returns the largest semantic version number from a list of version strings.

    Args:
        version_list (list of str): A list of version strings.

    Returns:
        str: The largest version string from the list.
    """
    parsed_versions = [parse(v) for v in version_list]
    largest_version = max(parsed_versions)
    return str(largest_version)


def get_latest_package_version(package: str, prerelease: bool = False) -> str:
    """Retrieves the latest version of package from PyPI."""
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException as err:
        raise VersionNotFoundError(
            f"Failed to retrieve latest {package} version from PyPI."
        ) from err

    data = response.json()

    if not prerelease:
        try:
            return data["info"]["version"]
        except KeyError as err:
            raise QbraidSystemError(
                f"Failed to extract version from {package} package metadata."
            ) from err

    try:
        all_versions = list(data["releases"].keys())
    except KeyError as err:
        raise QbraidSystemError(
            f"Failed to extract version from {package} package metadata."
        ) from err

    if len(all_versions) == 0:
        raise VersionNotFoundError(f"No versions found for {package}")

    latest_version = find_largest_version(all_versions)
    return latest_version


def package_has_match_on_pypi(
    name: str, op: Optional[str] = None, version: Optional[str] = None
) -> bool:
    """
    Check if a version of the package matches the given condition on PyPI.

    Args:
        package_name (str): Name of the package on PyPI.
        op (str, optional): Operator as a string (==, >=, <=, >, <, ~=). Defaults to None.
        version (str, optional): Version string to compare, e.g., "2.2". Defaults to None.

    Returns:
        bool: True if a matching version exists or the package exists (when op/version are None).
    """
    operators = {
        "==": operator.eq,
        ">=": operator.ge,
        "<=": operator.le,
        ">": operator.gt,
        "<": operator.lt,
        "~=": lambda v, r: v.major == r.major and v.minor == r.minor and v >= r,
    }

    if op:
        if op not in operators:
            raise ValueError(f"Unsupported operator: {op}")

        if not version:
            raise ValueError("Version must be provided when operator is specified.")

    url = f"https://pypi.org/pypi/{name}/json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            logger.debug("Package '%s' not found on PyPI.", name)
            return False

        response_json: dict[str, Any] = response.json()
        releases: list[str] = list(response_json.get("releases", {}).keys())

        if not version:
            return bool(releases)

        if not op:
            if len(version.split(".")) == 2:
                op = "~="
            elif len(version.split(".")) == 1:
                op = "~="
                version = f"{version}.0"
            else:
                op = "=="

        matching_versions = [v for v in releases if operators[op](parse(v), parse(version))]

        return bool(matching_versions)

    except Exception as err:  # pylint: disable=broad-exception-caught
        logger.debug("An error occurred: %s", err)
        return False


def get_local_package_version(
    package: str, python_path: Optional[Union[str, pathlib.Path]] = None
) -> str:
    """Retrieves the local version of a package."""
    if python_path:
        try:
            result = subprocess.run(
                [
                    str(python_path),
                    "-c",
                    f"import importlib.metadata; print(importlib.metadata.version('{package}'))",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as err:
            raise QbraidSystemError(f"{package} not found in the current environment.") from err
        except FileNotFoundError as err:
            raise QbraidSystemError(f"Python executable not found at {python_path}.") from err

    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError as err:
        raise QbraidSystemError(f"{package} not found in the current environment.") from err


def bump_version(version: Union[str, Version], bump_type: str) -> str:
    """
    Bumps the specified version component of a semantic version.

    Args:
        version (Version): The version object to be bumped.
        bump_type (str): The type of version bump to perform;
            'major', 'minor', 'patch', or 'prerelease'.

    Returns:
        str: The new version after applying the specified bump.

    Raises:
        ValueError: If an invalid bump type is specified.
    """
    if isinstance(version, str):
        version = parse(version)

    major, minor, patch = version.major, version.minor, version.micro

    if bump_type == "major":
        return f"{major + 1}.0.0"
    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    if bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if bump_type == "prerelease":
        if version.pre:
            pre_type, pre_num = version.pre[0], version.pre[1]
            return f"{version.base_version}-{pre_type}.{pre_num + 1}"
        return f"{version.base_version}-a.0"
    raise ValueError(f"Invalid bump type specified: {bump_type}")


def get_bumped_version(latest: str, local: str) -> str:
    """Compare latest and local versions and return the bumped version."""
    latest_version = parse(latest)
    local_version = parse(local)

    if local_version.base_version > latest_version.base_version:
        return f"{local_version.base_version}-a.0"
    if local_version.base_version == latest_version.base_version:
        if latest_version.is_prerelease and latest_version.pre is not None:
            if local_version.is_prerelease and local_version.pre is not None:
                if local_version.pre[0] == latest_version.pre[0]:
                    if local_version.pre[1] > latest_version.pre[1]:
                        raise InvalidVersionError(
                            "Local version prerelease is newer than latest version."
                        )
                    return bump_version(latest_version, "prerelease")
                if local_version.pre[0] < latest_version.pre[0]:
                    return bump_version(latest_version, "prerelease")
                return f"{local_version.base_version}-{local_version.pre[0]}.0"
            raise InvalidVersionError("Latest version is prerelease but local version is not.")
        if local_version.is_prerelease and local_version.pre is not None:
            return f"{local_version.base_version}-{local_version.pre[0]}.0"
        if local_version == latest_version:
            return f"{local_version.base_version}-a.0"
        raise InvalidVersionError(
            "Local version base is equal to latest, but no clear upgrade path found."
        )
    raise InvalidVersionError("Latest version base is greater than local, cannot bump.")


def compare_versions(version1: Optional[str], version2: Optional[str]) -> str:
    """
    Compare two semantic version strings and return the greater one.

    Args:
        version1 (Optional[str]): The first semantic version string.
        version2 (Optional[str]): The second semantic version string.

    Returns:
        str: The greater of the two versions. If both versions are None, None is returned.
             If one version is None and the other isn't, a defined value is returned.

    Raises:
        ValueError: If both versions are None.
    """
    if version1 is None and version2 is None:
        raise ValueError("Both versions are None.")

    if version1 is None and version2 is not None:
        return version2
    if version2 is None and version1 is not None:
        return version1

    if version1 is None or version2 is None:
        raise ValueError("One of the versions is None. Should not be possible to reach here.")

    v1 = parse(version1)
    v2 = parse(version2)

    if v1 > v2:
        return version1
    if v2 > v1:
        return version2

    logger.debug("Versions %s and %s are equal.", version1, version2)
    return version1


def get_prelease_version(
    project_root: Union[pathlib.Path, str], package_name: str, shorten: bool = True
) -> str:
    """
    Determine the bumped version of a package based on local and latest versions. Prioritizes
    `package.json` for version extraction, and if unsuccessful, falls back to `pyproject.toml`.

    Args:
        project_root (Union[pathlib.Path, str]): Path to the project root directory.
        package_name (str): Name of the package to check.
        shorten (bool): Flag to determine if prerelease versions should be shortened.

    Returns:
        str: The bumped version string.

    Raises:
        FileNotFoundError: If no suitable package metadata file is found or readable.
        QbraidSystemError: If version extraction fails from both metadata files.
        QbraidChainedException: If version extraction fails from both metadata files.
    """
    project_root = pathlib.Path(project_root)
    package_json_path = project_root / "package.json"
    pyproject_toml_path = project_root / "pyproject.toml"

    v_local = None
    last_exception = None

    if package_json_path.exists():
        try:
            v_local = extract_version(package_json_path, shorten_prerelease=shorten)
        except (ValueError, VersionNotFoundError) as err:
            last_exception = err

    if v_local is None and pyproject_toml_path.exists():
        try:
            v_local = extract_version(pyproject_toml_path, shorten_prerelease=shorten)
        except (ValueError, VersionNotFoundError) as err:
            if last_exception:
                # pylint: disable-next=raise-missing-from
                raise QbraidChainedException(
                    "Failed to extract version from package.json and pyproject.toml",
                    [last_exception, err],
                )
            raise QbraidSystemError("Failed to extract version from pyproject.toml") from err

    if v_local is None:
        if last_exception:
            raise QbraidSystemError(
                "Failed to extract version from package.json"
            ) from last_exception
        raise FileNotFoundError("No package metadata file found.")

    v_latest_pre = get_latest_package_version(package_name, prerelease=True)
    v_latest_stable = get_latest_package_version(package_name, prerelease=False)
    v_latest = compare_versions(v_latest_pre, v_latest_stable)
    return get_bumped_version(v_latest, v_local)


def update_version_in_pyproject(file_path: Union[str, pathlib.Path], new_version: str) -> None:
    """
    Update the version number in a pyproject.toml file.

    Args:
        file_path (Union[str, pathlib.Path]): Path to the pyproject.toml file.
        new_version (str): The new version number to set.

    Raises:
        FileNotFoundError: If the pyproject.toml file does not exist.
        KeyError: If the 'project.version' key is not found in the file.
    """
    file_path = pathlib.Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    updated = False
    lines = []
    in_project_section = False

    version_regex = re.compile(r'(\s*version\s*=\s*["\'])([^"\']+)(["\']\s*)')

    with file_path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip() == "[project]":
                in_project_section = True
            elif line.strip().startswith("[") and in_project_section:
                in_project_section = False

            if in_project_section and version_regex.search(line):
                match = version_regex.search(line)
                if match:
                    start, _, end = match.groups()
                    formatted_line = f"{start}{new_version}{end}"
                    lines.append(formatted_line)
                    updated = True
            else:
                lines.append(line)

    if not updated:
        raise KeyError("The 'project.version' key was not found in the pyproject.toml.")

    with file_path.open("w", encoding="utf-8") as file:
        file.writelines(lines)


__all__ = [
    "extract_version",
    "bump_version",
    "get_bumped_version",
    "get_latest_package_version",
    "get_local_package_version",
    "is_valid_semantic_version",
    "compare_versions",
    "get_prelease_version",
    "update_version_in_pyproject",
]
