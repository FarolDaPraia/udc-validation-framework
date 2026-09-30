"""
Filter Configuration Manager
Handles dynamic filter loading and management from JSON config
"""

import json
from pathlib import Path
from typing import Dict


class FilterConfig:
    """Load and manage filter configurations from JSON."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = "config/filters.json"

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Filter config not found: {config_path}")

        with open(config_file) as f:
            self.config = json.load(f)

    def get_filter(self, filter_name: str) -> Dict:
        """
        Get a specific filter configuration.

        Args:
            filter_name: Name of the filter to retrieve

        Returns:
            Filter configuration dict

        Raises:
            ValueError: If filter not found
        """
        if filter_name not in self.config['filters']:
            raise ValueError(
                f"Filter '{filter_name}' not found. "
                f"Available: {list(self.config['filters'].keys())}"
            )
        return self.config['filters'][filter_name]

    def list_filters(self) -> Dict[str, Dict]:
        """List all available filters."""
        return self.config['filters']

    def get_enabled_filters(self) -> Dict[str, Dict]:
        """Get only enabled filters."""
        return {
            name: config
            for name, config in self.config['filters'].items()
            if config.get('enabled', False)
        }

    def enable_filter(self, filter_name: str) -> None:
        """Enable a filter."""
        if filter_name not in self.config['filters']:
            raise ValueError(f"Filter '{filter_name}' not found")
        self.config['filters'][filter_name]['enabled'] = True

    def disable_filter(self, filter_name: str) -> None:
        """Disable a filter."""
        if filter_name not in self.config['filters']:
            raise ValueError(f"Filter '{filter_name}' not found")
        self.config['filters'][filter_name]['enabled'] = False
