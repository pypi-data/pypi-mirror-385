# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for saving/loading configuration to/from the qbraidrc file.

"""
import configparser
import os
from pathlib import Path
from typing import Optional

from .exceptions import ConfigError

DEFAULT_CONFIG_SECTION = "default"
DEFAULT_ENDPOINT_URL = "https://api.qbraid.com/api"
DEFAULT_ORGANIZATION = "qbraid"
DEFAULT_WORKSPACE = "qbraid"
SUPPORTED_WORKSPACES = {"qbraid", "aws"}
DEFAULT_CONFIG_PATH = Path.home() / ".qbraid" / "qbraidrc"
USER_CONFIG_PATH = os.getenv("QBRAID_CONFIG_FILE", str(DEFAULT_CONFIG_PATH))


def load_config(filepath: str = USER_CONFIG_PATH) -> configparser.ConfigParser:
    """Load the configuration from the file."""
    config_path = Path(filepath)
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
    except (FileNotFoundError, PermissionError, configparser.Error) as err:
        raise ConfigError(f"Failed to load configuration from {config_path}.") from err

    return config


def save_config(config: configparser.ConfigParser, filepath: str = USER_CONFIG_PATH) -> None:
    """Save configuration to qbraidrc file."""
    try:
        config_file = Path(filepath)
        config_path = config_file.parent

        config_path.mkdir(parents=True, exist_ok=True)
        with (config_file).open("w", encoding="utf-8") as configfile:
            config.write(configfile)
    except Exception as err:
        raise ConfigError(f"Failed to save configuration to {config_file}.") from err


def update_config_option(
    config: configparser.ConfigParser, section: str, option: str, value: Optional[str]
) -> configparser.ConfigParser:
    """Updates the configuration option if the value is provided and different from the current one.

    Args:
        section (str): The section in the config file.
        option (Optional[str]): The option name to be set or updated.
        value (Optional[str]): The new value for the option.
        config (configparser.ConfigParser): The configuration parser object.

    Returns:
        configparser.ConfigParser: The updated configuration object.

    Raises:
        ValueError: If the option value fails to be cast to a string.
    """
    if value is None:
        return config

    try:
        value = str(value)
    except TypeError as err:
        raise ValueError(f"Invalid value for option {option}.") from err

    if not config.has_option(section, option) or config.get(section, option) != value:
        config.set(section, option, value)

    return config
