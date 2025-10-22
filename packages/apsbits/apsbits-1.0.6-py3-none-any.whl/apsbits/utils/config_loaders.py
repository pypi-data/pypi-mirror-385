"""
Configuration management for the instrument.

This module serves as the single source of truth for instrument configuration.
It loads and validates the configuration from the iconfig.yml file and provides
access to the configuration throughout the application.
"""

import logging
import pathlib
from pathlib import Path
from typing import Any
from typing import Optional

import tomli  # type: ignore
import yaml

logger = logging.getLogger(__name__)

# Global configuration instance
_iconfig: dict[str, Any] = {}


def load_config(config_path: Optional[Path] = None) -> dict[str, Any]:
    """
    Load configuration from a YAML or TOML file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        The loaded configuration dictionary.

    Raises:
        ValueError: If config_path is None or if the file extension is not supported.
        FileNotFoundError: If the configuration file does not exist.
    """
    global _iconfig

    if config_path is None:
        raise ValueError("config_path must be provided")

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    try:
        with open(config_path, "rb") as f:
            if config_path.suffix.lower() == ".yml":
                config = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".toml":
                config = tomli.load(f)
            else:
                raise ValueError(
                    f"Unsupported configuration file format: {config_path.suffix}. "
                    "Supported formats: .yml, .toml"
                )

            if config is None:
                logger.warning(
                    "Configuration file %s is empty, using empty configuration",
                    config_path,
                )
                config = {}

            _iconfig.update(config)

            _iconfig["ICONFIG_PATH"] = str(config_path)
            _iconfig["INSTRUMENT_PATH"] = str(config_path.parent)
            _iconfig["INSTRUMENT_FOLDER"] = str(config_path.parent.name)

            return _iconfig
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", config_path)
        raise
    except PermissionError:
        logger.error("Permission denied reading configuration file: %s", config_path)
        raise
    except yaml.YAMLError as e:
        logger.error(
            "YAML parsing error in configuration file %s: %s", config_path, str(e)
        )
        raise
    except tomli.TOMLDecodeError as e:
        logger.error(
            "TOML parsing error in configuration file %s: %s", config_path, str(e)
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error loading configuration from %s: %s (type: %s)",
            config_path,
            str(e),
            type(e).__name__,
        )
        raise


def get_config() -> dict[str, Any]:
    """
    Get the current configuration.

    Returns:
        The current configuration dictionary.
    """
    return _iconfig


def update_config(updates: dict[str, Any]) -> None:
    """
    Update the current configuration.

    Args:
        updates: Dictionary of configuration updates.
    """
    _iconfig.update(updates)


def load_config_yaml(config_obj) -> dict:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        The loaded configuration dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
    """

    if config_obj is None:
        raise ValueError("config_path must be provided")

    try:
        # If it's a path, open it first
        if isinstance(config_obj, (str, pathlib.Path)):
            config_path = pathlib.Path(config_obj)
            if not config_path.exists():
                raise FileNotFoundError(
                    f"YAML configuration file not found: {config_path}"
                )
            with open(config_path, "r") as f:
                content = f.read()
        # Otherwise assume it's a file-like object
        else:
            content = config_obj.read()

        if not content.strip():
            logger.warning("YAML configuration is empty")
            return {}

        iconfig = yaml.load(content, yaml.Loader)
        return iconfig if iconfig is not None else {}
    except FileNotFoundError:
        logger.error("YAML configuration file not found: %s", config_obj)
        raise
    except PermissionError:
        logger.error("Permission denied reading YAML configuration: %s", config_obj)
        raise
    except yaml.YAMLError as e:
        logger.error("YAML parsing error in configuration: %s", str(e))
        raise
    except Exception as e:
        logger.error(
            "Unexpected error loading YAML configuration: %s (type: %s)",
            str(e),
            type(e).__name__,
        )
        raise


def validate_instrument_path(
    instrument_path: Optional[Path] = None,
    expected_files: Optional[list[str]] = None,
    expected_dirs: Optional[list[str]] = None,
) -> tuple[bool, str]:
    """
    Validate if the provided instrument path is correct by checking for expected files
    and directories.

    Args:
        instrument_path: Path to the instrument directory. If None, uses the path from
            the current config.
        expected_files: List of files that should exist in the instrument directory.
        expected_dirs: List of directories that should exist in the instrument
            directory.

    Returns:
        A tuple containing (is_valid, message) where is_valid is a boolean indicating if
        the path is valid, and message is a description of the validation result.
    """
    if instrument_path is None:
        if "INSTRUMENT_PATH" not in _iconfig:
            return False, "No instrument path found in configuration"
        instrument_path = Path(_iconfig["INSTRUMENT_PATH"])

    # Default expected files and directories if none provided
    if expected_files is None:
        expected_files = ["iconfig.yml", "iconfig.toml"]
    if expected_dirs is None:
        expected_dirs = ["src", "tests"]

    # Check if the path exists and is a directory
    if not instrument_path.exists():
        return False, f"Instrument path does not exist: {instrument_path}"

    if not instrument_path.is_dir():
        return False, f"Instrument path is not a directory: {instrument_path}"

    # Check for expected files
    missing_files = []
    for file in expected_files:
        if not (instrument_path / file).exists():
            missing_files.append(file)

    if missing_files:
        return (
            False,
            f"Missing expected files in instrument path: {', '.join(missing_files)}",
        )

    # Check for expected directories
    missing_dirs = []
    for directory in expected_dirs:
        if (
            not (instrument_path / directory).exists()
            or not (instrument_path / directory).is_dir()
        ):
            missing_dirs.append(directory)

    if missing_dirs:
        return (
            False,
            f"Missing expected directories in instrument path: "
            f"{', '.join(missing_dirs)}",
        )

    return True, f"Instrument path is valid: {instrument_path}"
