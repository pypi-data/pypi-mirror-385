"""
Configuration Management System

Manages configuration loading and merging from multiple sources:
1. CLI arguments (highest priority)
2. Project config (.outcomeforge.yaml)
3. Global config (~/.outcomeforge/config.yaml)
4. Default values (lowest priority)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import warnings


class ConfigManager:
    """Configuration manager with hierarchical config merging"""

    DEFAULT_CONFIG = {
        "nodes": {
            "search_paths": []
        },
        "scenarios": {
            "search_paths": []
        },
        "llm": {
            "default_model": "claude-3-haiku-20240307",
            "api_timeout": 60
        },
        "output": {
            "format": "yaml",
            "verbose": False
        }
    }

    def __init__(self, project_dir: Optional[Path] = None):
        """Initialize config manager

        Args:
            project_dir: Project directory to search for .outcomeforge.yaml
                        (defaults to current directory)
        """
        self.project_dir = project_dir or Path.cwd()
        self._config = None

    def load(self, cli_overrides: Optional[Dict] = None) -> Dict[str, Any]:
        """Load and merge configuration from all sources

        Merge priority: CLI > Project > Global > Default

        Args:
            cli_overrides: Configuration from CLI arguments

        Returns:
            Merged configuration dictionary
        """
        # Start with default config
        config = self._deep_copy(self.DEFAULT_CONFIG)

        # Merge global config
        global_config = self._load_global_config()
        if global_config:
            config = self._deep_merge(config, global_config)

        # Merge project config
        project_config = self._load_project_config()
        if project_config:
            config = self._deep_merge(config, project_config)

        # Merge CLI overrides
        if cli_overrides:
            config = self._deep_merge(config, cli_overrides)

        self._config = config
        return config

    def _load_global_config(self) -> Optional[Dict]:
        """Load global configuration from ~/.outcomeforge/config.yaml

        Returns:
            Configuration dictionary or None if file doesn't exist
        """
        global_config_path = Path.home() / ".outcomeforge" / "config.yaml"
        return self._load_yaml_file(global_config_path, "global")

    def _load_project_config(self) -> Optional[Dict]:
        """Load project configuration from .outcomeforge.yaml

        Returns:
            Configuration dictionary or None if file doesn't exist
        """
        project_config_path = self.project_dir / ".outcomeforge.yaml"
        return self._load_yaml_file(project_config_path, "project")

    def _load_yaml_file(self, file_path: Path, config_type: str) -> Optional[Dict]:
        """Load YAML configuration file

        Args:
            file_path: Path to YAML file
            config_type: Type of config (for error messages)

        Returns:
            Configuration dictionary or None if file doesn't exist
        """
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r') as f:
                config = yaml.safe_load(f) or {}
            return config
        except yaml.YAMLError as e:
            warnings.warn(f"Failed to load {config_type} config from {file_path}: {e}")
            return None
        except Exception as e:
            warnings.warn(f"Error reading {config_type} config from {file_path}: {e}")
            return None

    def _deep_copy(self, obj: Any) -> Any:
        """Deep copy a dictionary or list

        Args:
            obj: Object to copy

        Returns:
            Deep copy of object
        """
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries

        Args:
            base: Base dictionary
            override: Override dictionary (takes precedence)

        Returns:
            Merged dictionary
        """
        result = self._deep_copy(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            elif key in result and isinstance(result[key], list) and isinstance(value, list):
                # For lists, extend instead of replace
                result[key] = result[key] + value
            else:
                result[key] = self._deep_copy(value)

        return result

    def get(self, *keys: str, default: Any = None) -> Any:
        """Get configuration value using dotted path

        Args:
            *keys: Configuration key path (e.g., 'llm', 'default_model')
            default: Default value if key doesn't exist

        Returns:
            Configuration value

        Example:
            >>> config.get('llm', 'default_model')
            'claude-3-haiku-20240307'
        """
        if self._config is None:
            self.load()

        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def get_node_search_paths(self) -> List[Path]:
        """Get all node search paths from configuration

        Returns:
            List of Path objects for node search directories
        """
        if self._config is None:
            self.load()

        paths = self._config.get('nodes', {}).get('search_paths', [])
        return [Path(p).expanduser() for p in paths]

    def get_scenario_search_paths(self) -> List[Path]:
        """Get all scenario search paths from configuration

        Returns:
            List of Path objects for scenario search directories
        """
        if self._config is None:
            self.load()

        paths = self._config.get('scenarios', {}).get('search_paths', [])
        return [Path(p).expanduser() for p in paths]


# Global config instance
config_manager = ConfigManager()
