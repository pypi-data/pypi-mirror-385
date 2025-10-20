# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: MIT

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under MIT License (see LICENSE file for details)
#
# This file is part of the KRL platform.
# For more information, visit: https://krlabs.dev
#
# KRL™ is a trademark of KR-Labs Foundation.

"""
Structured logging implementation with JSON formatting.

This module provides a configured logger that outputs structured JSON logs
for better parsing and analysis in production environments.
"""

import logging
import sys
from typing import Optional

from .formatters import JSONFormatter


# Global logger configuration
_loggers = {}
_default_level = logging.INFO
_default_format = "json"  # "json" or "text"


def setup_logging(
    level: int = logging.INFO,
    format_type: str = "json",
    log_file: Optional[str] = None,
) -> None:
    """
    Configure global logging settings.
    
    Args:
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        format_type: Output format - "json" for structured JSON or "text" for human-readable
        log_file: Optional file path to write logs to (in addition to stdout)
        
    Example:
        >>> from krl_core.logging import setup_logging
        >>> import logging
        >>> setup_logging(level=logging.DEBUG, format_type="json")
    """
    global _default_level, _default_format
    _default_level = level
    _default_format = format_type
    
    # Clear existing loggers to apply new configuration
    _loggers.clear()


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Get a configured logger instance with structured logging.
    
    Args:
        name: Logger name (typically __name__ of the calling module)
        level: Optional logging level override (uses global default if not specified)
        
    Returns:
        Configured logger instance with JSON formatting
        
    Example:
        >>> from krl_core.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("User logged in", extra={"user_id": 123, "ip": "192.168.1.1"})
        {"timestamp": "2025-10-19T...", "level": "INFO", "name": "my_module", 
         "message": "User logged in", "user_id": 123, "ip": "192.168.1.1"}
    """
    # Return cached logger if it exists
    if name in _loggers:
        return _loggers[name]
    
    # Create new logger
    logger = logging.getLogger(name)
    logger.setLevel(level if level is not None else _default_level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level if level is not None else _default_level)
    
    # Set formatter based on format type
    if _default_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False
    
    # Cache logger
    _loggers[name] = logger
    
    return logger


def get_child_logger(parent_logger: logging.Logger, child_name: str) -> logging.Logger:
    """
    Create a child logger from a parent logger.
    
    Args:
        parent_logger: Parent logger instance
        child_name: Name for the child logger (will be appended to parent name)
        
    Returns:
        Child logger instance
        
    Example:
        >>> parent = get_logger("myapp")
        >>> child = get_child_logger(parent, "database")
        >>> child.info("Connected")  # Logs with name "myapp.database"
    """
    child_logger_name = f"{parent_logger.name}.{child_name}"
    return get_logger(child_logger_name)


def set_level(logger: logging.Logger, level: int) -> None:
    """
    Set logging level for a logger and all its handlers.
    
    Args:
        logger: Logger instance to modify
        level: New logging level (e.g., logging.DEBUG, logging.INFO)
        
    Example:
        >>> logger = get_logger(__name__)
        >>> set_level(logger, logging.DEBUG)  # Enable debug logging
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
