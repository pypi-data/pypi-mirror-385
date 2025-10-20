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

"""Version information for krl-core."""

# Version as tuple
VERSION = (0, 1, 1)

# Version as string
__version__ = "0.1.1"

# Version info
__version_info__ = {
    "major": 0,
    "minor": 1,
    "patch": 1,
    "release": "alpha",
    "build": "20251019",
}


def get_version() -> str:
    """
    Get the version string.
    
    Returns:
        str: Version string in format 'MAJOR.MINOR.PATCH'
    """
    return __version__


def get_version_info() -> dict:
    """
    Get detailed version information.
    
    Returns:
        dict: Dictionary with version components
    """
    return __version_info__.copy()
