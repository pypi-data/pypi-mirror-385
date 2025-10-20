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
Configuration management module for KRL Core.

This module provides configuration management with support for environment
variables, YAML files, and validation.

Example:
    >>> from krl_core.config import ConfigManager
    >>> config = ConfigManager()
    >>> api_key = config.get("FRED_API_KEY")
    >>> config.set("cache_dir", "./cache")
"""

from .manager import ConfigManager

__all__ = ["ConfigManager"]
