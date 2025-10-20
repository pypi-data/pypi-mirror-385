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
KRL Core Utilities
==================

Shared foundation utilities for the KR-Labs analytics platform.

This package provides common utilities, configuration management, logging,
caching, and base classes used across all KRL packages.

Modules:
    - logging: Structured logging with JSON formatting
    - config: Configuration management (environment variables, YAML)
    - cache: File-based and Redis caching with TTL support
    - api: Base HTTP client with retry logic and rate limiting
    - utils: Common utilities (dates, validators, decorators)

Example:
    >>> from krl_core import get_logger, ConfigManager, FileCache
    >>> logger = get_logger(__name__)
    >>> config = ConfigManager()
    >>> cache = FileCache(cache_dir="./cache")
"""

__version__ = "0.1.0"
__author__ = "KR-Labs Foundation"
__email__ = "support@krlabs.dev"
__license__ = "MIT"
__copyright__ = "Copyright © 2025 KR-Labs Foundation. All rights reserved."
__url__ = "https://github.com/KR-Labs/krl-open-core"
__description__ = "Shared foundation utilities for the KR-Labs analytics platform"

# Version info
VERSION = (0, 1, 0)

# Import main exports
# Note: Actual implementations will be added in subsequent commits
# For now, we define the public API interface

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    # Logging
    "get_logger",
    "setup_logging",
    # Config
    "ConfigManager",
    # Cache
    "Cache",
    "FileCache",
    "RedisCache",
]

# Import main exports
from .logging import get_logger, setup_logging
from .config import ConfigManager
from .cache import Cache, FileCache, RedisCache
