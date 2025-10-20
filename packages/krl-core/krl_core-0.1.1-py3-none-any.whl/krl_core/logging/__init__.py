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
Structured logging module for KRL Core.

This module provides structured logging with JSON formatting, contextual information,
and correlation ID tracking for distributed systems.

Example:
    >>> from krl_core.logging import get_logger
    >>> logger = get_logger(__name__)
    >>> logger.info("Processing started", extra={"user_id": 123, "batch_size": 100})
"""

from .logger import get_logger, setup_logging

__all__ = ["get_logger", "setup_logging"]
