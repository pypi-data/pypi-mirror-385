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
Configuration manager implementation.

Provides ConfigManager class for managing application configuration
from multiple sources (environment variables, YAML files, defaults).
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from dotenv import load_dotenv


class ConfigManager:
    """
    Configuration manager for application settings.
    
    Manages configuration from multiple sources with priority:
    1. Explicitly set values (highest priority)
    2. Environment variables
    3. Configuration files (YAML)
    4. Default values (lowest priority)
    
    Example:
        >>> config = ConfigManager()
        >>> config.load_from_file("config.yaml")
        >>> api_key = config.get("API_KEY", default="default_key")
        >>> config.set("timeout", 30)
    """
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None, load_env: bool = True):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to YAML configuration file
            load_env: Whether to load .env file automatically
        """
        self._config: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        
        # Load .env file if it exists
        if load_env:
            load_dotenv()
        
        # Load config file if provided
        if config_file:
            self.load_from_file(config_file)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Checks in order: explicit config, environment variables, defaults.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Example:
            >>> config = ConfigManager()
            >>> timeout = config.get("TIMEOUT", default=30)
        """
        # Check explicitly set config
        if key in self._config:
            return self._config[key]
        
        # Check environment variables
        env_value = os.getenv(key)
        if env_value is not None:
            return self._parse_env_value(env_value)
        
        # Check defaults
        if key in self._defaults:
            return self._defaults[key]
        
        return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value explicitly.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Example:
            >>> config = ConfigManager()
            >>> config.set("API_URL", "https://api.example.com")
        """
        self._config[key] = value
    
    def set_default(self, key: str, value: Any) -> None:
        """
        Set default value for a configuration key.
        
        Default values have lowest priority and are only used if the key
        is not found in explicit config or environment variables.
        
        Args:
            key: Configuration key
            value: Default value
            
        Example:
            >>> config = ConfigManager()
            >>> config.set_default("TIMEOUT", 30)
        """
        self._defaults[key] = value
    
    def load_from_file(self, file_path: Union[str, Path]) -> None:
        """
        Load configuration from YAML file.
        
        Args:
            file_path: Path to YAML configuration file
            
        Raises:
            FileNotFoundError: If file does not exist
            yaml.YAMLError: If file is not valid YAML
            
        Example:
            >>> config = ConfigManager()
            >>> config.load_from_file("config.yaml")
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(path, "r") as f:
            file_config = yaml.safe_load(f) or {}
        
        if not isinstance(file_config, dict):
            raise ValueError(f"Configuration file must contain a dictionary: {file_path}")
        
        # Merge with existing config (explicit config takes precedence)
        self._config = {**file_config, **self._config}
    
    def load_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Load configuration from dictionary.
        
        Args:
            config_dict: Dictionary of configuration values
            
        Example:
            >>> config = ConfigManager()
            >>> config.load_from_dict({"API_KEY": "abc123", "TIMEOUT": 30})
        """
        if not isinstance(config_dict, dict):
            raise ValueError("Configuration must be a dictionary")
        
        # Merge with existing config
        self._config = {**config_dict, **self._config}
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.
        
        Returns merged configuration from all sources.
        
        Returns:
            Dictionary of all configuration values
            
        Example:
            >>> config = ConfigManager()
            >>> all_config = config.get_all()
            >>> print(all_config)
        """
        # Start with defaults
        result = self._defaults.copy()
        
        # Add environment variables (only those already accessed or in config)
        for key in list(result.keys()) + list(self._config.keys()):
            env_value = os.getenv(key)
            if env_value is not None:
                result[key] = self._parse_env_value(env_value)
        
        # Add explicit config (highest priority)
        result.update(self._config)
        
        return result
    
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key: Configuration key to check
            
        Returns:
            True if key exists in any config source
            
        Example:
            >>> config = ConfigManager()
            >>> if config.has("API_KEY"):
            ...     api_key = config.get("API_KEY")
        """
        return (
            key in self._config
            or os.getenv(key) is not None
            or key in self._defaults
        )
    
    def delete(self, key: str) -> None:
        """
        Delete configuration key from explicit config.
        
        Note: This only removes the key from explicit config, not from
        environment variables or defaults.
        
        Args:
            key: Configuration key to delete
            
        Example:
            >>> config = ConfigManager()
            >>> config.set("TEMP_KEY", "value")
            >>> config.delete("TEMP_KEY")
        """
        if key in self._config:
            del self._config[key]
    
    def clear(self) -> None:
        """
        Clear all explicitly set configuration.
        
        Note: This only clears explicit config, not environment variables
        or defaults.
        
        Example:
            >>> config = ConfigManager()
            >>> config.clear()  # Remove all explicit config
        """
        self._config.clear()
    
    def _parse_env_value(self, value: str) -> Any:
        """
        Parse environment variable value.
        
        Attempts to convert string values to appropriate types:
        - "true"/"false" -> bool
        - Numbers -> int or float
        - Otherwise -> str
        
        Args:
            value: String value from environment variable
            
        Returns:
            Parsed value with appropriate type
        """
        # Handle boolean values
        if value.lower() in ("true", "yes", "1"):
            return True
        if value.lower() in ("false", "no", "0"):
            return False
        
        # Handle numeric values
        try:
            # Try integer first
            if "." not in value:
                return int(value)
            # Try float
            return float(value)
        except ValueError:
            # Not a number, return as string
            return value
    
    def __repr__(self) -> str:
        """String representation of ConfigManager."""
        return f"ConfigManager(config_keys={len(self._config)}, default_keys={len(self._defaults)})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        all_config = self.get_all()
        return f"ConfigManager with {len(all_config)} configuration values"
