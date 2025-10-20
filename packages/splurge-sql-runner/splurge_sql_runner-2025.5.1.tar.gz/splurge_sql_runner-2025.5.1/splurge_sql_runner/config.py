"""
Simplified configuration management for splurge-sql-runner.

Provides simple dictionary-based configuration with support for
JSON configuration files and environment variables.

Copyright (c) 2025, Jim Schilling

This module is licensed under the MIT License.
"""

import json
import os
from pathlib import Path
from typing import Any

from splurge_sql_runner.config.constants import (
    DEFAULT_CONNECTION_TIMEOUT,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_STATEMENTS_PER_FILE,
)
from splurge_sql_runner.exceptions import ConfigFileError, ConfigValidationError, FileError
from splurge_sql_runner.utils.file_io_adapter import FileIoAdapter

# Module domains
DOMAINS = ["config", "configuration"]

__all__ = ["load_config", "load_json_config"]

# Validation constants
VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
VALID_SECURITY_LEVELS = {"strict", "normal", "permissive"}


def load_config(config_file_path: str | None = None) -> dict[str, Any]:
    """
    Load configuration from environment variables and optional JSON file.

    Environment variables take precedence over JSON file settings.
    Returns a simple dictionary with essential configuration options.

    Args:
        config_file_path: Optional path to JSON configuration file

    Returns:
        Dictionary containing configuration values

    Raises:
        ConfigFileError: If configuration file cannot be read or parsed
        ConfigValidationError: If configuration values are invalid
    """
    config = get_default_config()

    # Load from JSON file if provided
    if config_file_path and Path(config_file_path).exists():
        json_config = load_json_config(config_file_path)
        config.update(json_config)

    # Override with environment variables (highest priority)
    config.update(get_env_config())

    # Validate the final configuration
    _validate_config(config)

    return config


def get_default_config() -> dict[str, Any]:
    """Get default configuration values."""
    return {
        "database_url": "sqlite:///:memory:",
        "max_statements_per_file": DEFAULT_MAX_STATEMENTS_PER_FILE,
        "connection_timeout": DEFAULT_CONNECTION_TIMEOUT,
        "log_level": DEFAULT_LOG_LEVEL,
        "security_level": "normal",
        "enable_verbose": False,
        "enable_debug": False,
    }


def get_env_config() -> dict[str, Any]:
    """Load configuration from environment variables."""
    config = {}

    # Database configuration
    if db_url := os.getenv("SPLURGE_SQL_RUNNER_DB_URL"):
        config["database_url"] = db_url

    # Statement limits
    if max_statements := os.getenv("SPLURGE_SQL_RUNNER_MAX_STATEMENTS_PER_FILE"):
        try:
            config["max_statements_per_file"] = int(max_statements)
        except ValueError:
            pass  # Keep default if invalid

    # Connection timeout
    if timeout := os.getenv("SPLURGE_SQL_RUNNER_CONNECTION_TIMEOUT"):
        try:
            config["connection_timeout"] = float(timeout)
        except ValueError:
            pass  # Keep default if invalid

    # Logging
    if log_level := os.getenv("SPLURGE_SQL_RUNNER_LOG_LEVEL"):
        config["log_level"] = log_level

    # Output options
    if verbose := os.getenv("SPLURGE_SQL_RUNNER_VERBOSE"):
        config["enable_verbose"] = verbose.lower() in ("true", "1", "yes", "on")

    if debug := os.getenv("SPLURGE_SQL_RUNNER_DEBUG"):
        config["enable_debug"] = debug.lower() in ("true", "1", "yes", "on")

    return config


def load_json_config(file_path: str) -> dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        file_path: Path to JSON configuration file

    Returns:
        Dictionary of configuration values from JSON

    Raises:
        ConfigFileError: If file cannot be read or parsed
    """
    try:
        content = FileIoAdapter.read_file(file_path, context_type="config")
        config_data = json.loads(content)
        return _parse_json_config(config_data)
    except FileError as e:
        raise ConfigFileError(f"Failed to read config file: {e}") from e
    except json.JSONDecodeError as e:
        raise ConfigFileError(f"Invalid JSON in config file: {e}") from e
    except Exception as e:
        raise ConfigFileError(f"Failed to read config file: {e}") from e


def _parse_json_config(config_data: dict[str, Any]) -> dict[str, Any]:
    """Parse JSON configuration data into simplified config dictionary."""
    config = {}

    # Database configuration
    if "database" in config_data and isinstance(config_data["database"], dict):
        db_config = config_data["database"]
        if "url" in db_config:
            config["database_url"] = db_config["url"]
        if "connection" in db_config and isinstance(db_config["connection"], dict):
            conn_config = db_config["connection"]
            if "timeout" in conn_config:
                config["connection_timeout"] = conn_config["timeout"]

    # Application settings
    if "max_statements_per_file" in config_data:
        config["max_statements_per_file"] = config_data["max_statements_per_file"]

    if "enable_verbose_output" in config_data:
        config["enable_verbose"] = config_data["enable_verbose_output"]

    if "enable_debug_mode" in config_data:
        config["enable_debug"] = config_data["enable_debug_mode"]

    # Logging configuration
    if "logging" in config_data and isinstance(config_data["logging"], dict):
        log_config = config_data["logging"]
        if "level" in log_config:
            config["log_level"] = log_config["level"]

    # Security configuration
    if "security_level" in config_data:
        security_level = config_data["security_level"]
        if security_level in ["strict", "normal", "permissive"]:
            config["security_level"] = security_level

    return config


def _validate_config(config: dict[str, Any]) -> None:
    """
    Validate configuration values.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ConfigValidationError: If any configuration value is invalid
    """
    errors: list[str] = []

    # Validate database_url
    if not isinstance(config.get("database_url"), str) or not config["database_url"]:
        errors.append("database_url must be a non-empty string")

    # Validate max_statements_per_file
    max_stmts = config.get("max_statements_per_file")
    if not isinstance(max_stmts, int) or max_stmts <= 0:
        errors.append("max_statements_per_file must be a positive integer")

    # Validate connection_timeout
    timeout = config.get("connection_timeout")
    if not isinstance(timeout, int | float) or timeout <= 0:
        errors.append("connection_timeout must be a positive number")

    # Validate log_level
    log_level = config.get("log_level", "").upper()
    if log_level and log_level not in VALID_LOG_LEVELS:
        errors.append(f"log_level must be one of {VALID_LOG_LEVELS}")

    # Validate security_level
    security_level = config.get("security_level")
    if security_level and security_level not in VALID_SECURITY_LEVELS:
        errors.append(f"security_level must be one of {VALID_SECURITY_LEVELS}")

    # Validate enable_verbose and enable_debug
    if not isinstance(config.get("enable_verbose"), bool):
        errors.append("enable_verbose must be a boolean")

    if not isinstance(config.get("enable_debug"), bool):
        errors.append("enable_debug must be a boolean")

    if errors:
        raise ConfigValidationError(
            f"Configuration validation failed: {'; '.join(errors)}",
            context={"errors": errors, "config_keys": list(config.keys())},
        )


def save_config(config: dict[str, Any], file_path: str) -> None:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dictionary to save
        file_path: Path where to save the configuration file

    Raises:
        ConfigFileError: If file cannot be written
    """
    from splurge_safe_io import SafeTextFileWriter

    try:
        writer = SafeTextFileWriter(file_path=file_path, encoding="utf-8")
        writer.write(json.dumps(config, indent=2, ensure_ascii=False))
        writer.close()
    except Exception as e:
        raise ConfigFileError(f"Failed to save config file: {e}") from e
