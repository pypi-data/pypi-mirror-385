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
Custom log formatters for structured logging.

This module provides JSON and text formatters for consistent log output.
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    
    Outputs log records as JSON objects with consistent fields:
    - timestamp: ISO 8601 formatted timestamp
    - level: Log level (INFO, WARNING, ERROR, etc.)
    - name: Logger name
    - message: Log message
    - [additional fields]: Any extra fields passed via extra={} parameter
    
    Example:
        >>> formatter = JSONFormatter()
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(formatter)
        >>> logger = logging.getLogger("myapp")
        >>> logger.addHandler(handler)
        >>> logger.info("User action", extra={"user_id": 123, "action": "login"})
        {"timestamp": "2025-10-19T12:00:00.000Z", "level": "INFO", 
         "name": "myapp", "message": "User action", "user_id": 123, "action": "login"}
    """
    
    # Reserved field names that should not be overridden
    RESERVED_FIELDS = {
        "timestamp", "level", "name", "message", "exc_info", "exc_text",
        "stack_info", "lineno", "filename", "funcName", "pathname", "module"
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.
        
        Args:
            record: LogRecord to format
            
        Returns:
            JSON string representation of the log record
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        
        # Add source location information
        log_data["source"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self._format_traceback(record.exc_info),
            }
        
        # Add any extra fields from the log call
        # Filter out standard LogRecord attributes and reserved fields
        for key, value in record.__dict__.items():
            if (
                key not in self.RESERVED_FIELDS
                and not key.startswith("_")
                and key not in ["args", "msg", "levelno", "created", "msecs", 
                               "relativeCreated", "thread", "threadName", 
                               "processName", "process"]
            ):
                # Convert non-serializable objects to strings
                try:
                    json.dumps(value)  # Test if serializable
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)
        
        # Convert to JSON string
        try:
            return json.dumps(log_data, default=str)
        except Exception as e:
            # Fallback to simple format if JSON serialization fails
            return json.dumps({
                "timestamp": log_data["timestamp"],
                "level": log_data["level"],
                "name": log_data["name"],
                "message": f"Error formatting log: {str(e)}",
                "original_message": str(record.getMessage()),
            })
    
    def _format_traceback(self, exc_info: tuple) -> str:
        """
        Format exception traceback as string.
        
        Args:
            exc_info: Exception info tuple (type, value, traceback)
            
        Returns:
            Formatted traceback string
        """
        if exc_info and exc_info[2]:
            return "".join(traceback.format_exception(*exc_info))
        return ""


class ContextFormatter(logging.Formatter):
    """
    Formatter that adds contextual information to log records.
    
    This formatter can add correlation IDs, request IDs, or other
    contextual information that should be included in all logs.
    
    Example:
        >>> formatter = ContextFormatter(correlation_id="req-123")
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(formatter)
    """
    
    def __init__(
        self,
        fmt: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt: str = "%Y-%m-%d %H:%M:%S",
        **context_fields: Any
    ):
        """
        Initialize context formatter.
        
        Args:
            fmt: Log message format string
            datefmt: Date format string
            **context_fields: Additional fields to add to all log records
        """
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.context_fields = context_fields
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with context fields.
        
        Args:
            record: LogRecord to format
            
        Returns:
            Formatted log string
        """
        # Add context fields to record
        for key, value in self.context_fields.items():
            setattr(record, key, value)
        
        return super().format(record)
