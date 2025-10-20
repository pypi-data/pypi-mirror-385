"""
Logging package for splurge-sql-runner.

Provides centralized logging functionality with timed rotation and security features
to prevent sensitive data exposure using Python's built-in logging module.

Copyright (c) 2025, Jim Schilling

This module is licensed under the MIT License.
"""

from splurge_sql_runner.logging.context import (
    ContextualLogger,
    clear_correlation_id,
    correlation_context,
    generate_correlation_id,
    get_contextual_logger,
    get_correlation_id,
    log_context,
    set_correlation_id,
)
from splurge_sql_runner.logging.core import (
    configure_module_logging,
    get_logger,
    get_logging_config,
    is_logging_configured,
    setup_logging,
)
from splurge_sql_runner.logging.performance import (
    PerformanceLogger,
    log_performance,
    performance_context,
)

# Package domains
__domains__ = ["logging", "core", "context", "performance"]

__all__ = [
    # Core logging
    "setup_logging",
    "get_logger",
    "configure_module_logging",
    "get_logging_config",
    "is_logging_configured",
    # Context and correlation
    "generate_correlation_id",
    "set_correlation_id",
    "get_correlation_id",
    "clear_correlation_id",
    "correlation_context",
    "ContextualLogger",
    "get_contextual_logger",
    "log_context",
    # Performance monitoring
    "PerformanceLogger",
    "log_performance",
    "performance_context",
    # Minimal CLI logging public API
]
