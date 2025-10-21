# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module containing generic system utilities i.e. not specific to qBraid.

"""
import datetime
from pathlib import Path
from typing import Optional, Union


def _datetime_to_str(datetime_obj: "datetime.datetime") -> str:
    """Converts datetime object to ISO 8601 string."""
    return datetime_obj.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_current_utc_datetime() -> datetime.datetime:
    """Returns the current UTC date and time."""
    if not hasattr(datetime, "UTC"):
        return datetime.datetime.utcnow()
    return datetime.datetime.now(datetime.UTC)


def get_current_utc_datetime_as_string() -> str:
    """Returns the current UTC datetime as an ISO 8601 formatted string."""
    current_utc_datetime = get_current_utc_datetime()
    return _datetime_to_str(current_utc_datetime)


def replace_str(target: str, replacement: str, file_path: Union[str, Path]) -> None:
    """Replace all instances of string in file."""
    file_path = Path(file_path)

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    content = content.replace(target, replacement)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)


def echo_log(message: str, log_file_path: Optional[Union[Path, str]] = None) -> None:
    """Write message to log file."""
    if log_file_path is None:
        home_dir = Path.home()
        log_file_path = home_dir / ".qbraid" / "log.txt"
    else:
        log_file_path = Path(log_file_path)

    log_file_path.parent.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")


__all__ = ["get_current_utc_datetime_as_string", "replace_str", "echo_log"]
