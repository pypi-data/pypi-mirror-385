"""
Scenario Registry - Discovery and management of scenarios

This module provides:
- Automatic discovery of YAML scenario definitions
- Scenario registration and retrieval
- Running scenarios with user parameters
"""

from pathlib import Path
from typing import Dict, List, Optional
import warnings

from .scenario_loader import ScenarioLoader


class ScenarioRegistry:
    """Registry for managing and discovering scenarios

    Scenarios are discovered from:
    1. Global user scenarios (~/.outcomeforge/scenarios/)
    2. Project-level scenarios (.outcomeforge/scenarios/)

    Example:
        >>> registry = ScenarioRegistry(node_registry)
        >>> registry.auto_discover()
        >>> scenarios = registry.list_scenarios()
        >>> result = registry.run_scenario("my_scenario", {"patterns": ["**/*.py"]})
    """

    def __init__(self, node_registry, config_manager=None):
        """Initialize registry with node registry

        Args:
            node_registry: NodeRegistry instance for resolving nodes
            config_manager: Optional ConfigManager instance for configuration
        """
        self.scenarios: Dict[str, dict] = {}
        self.node_registry = node_registry
        self.config_manager = config_manager
        self.loader = ScenarioLoader(node_registry)

        self._scan_dirs: List[Path] = []
        self._setup_scan_dirs()

    def _setup_scan_dirs(self):
        """Setup directories to scan for scenarios"""
        # Add configured search paths
        if self.config_manager:
            config_paths = self.config_manager.get_scenario_search_paths()
            for path in config_paths:
                if path.exists():
                    self._scan_dirs.append(path)

        # Global user scenarios (default location)
        global_scenarios = Path.home() / ".outcomeforge" / "scenarios"
        if global_scenarios.exists() and global_scenarios not in self._scan_dirs:
            self._scan_dirs.append(global_scenarios)

        # Project-level scenarios (default location)
        project_scenarios = Path.cwd() / ".outcomeforge" / "scenarios"
        if project_scenarios.exists() and project_scenarios not in self._scan_dirs:
            self._scan_dirs.append(project_scenarios)

    def auto_discover(self, additional_dirs: Optional[List[str]] = None):
        """Automatically discover all scenarios from configured directories

        Args:
            additional_dirs: Optional list of additional directories to scan

        Example:
            >>> registry.auto_discover()
            >>> registry.auto_discover(additional_dirs=["./custom_scenarios"])
        """
        scan_dirs = self._scan_dirs.copy()

        if additional_dirs:
            scan_dirs.extend([Path(d) for d in additional_dirs])

        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            self._scan_directory(scan_dir)

    def _scan_directory(self, directory: Path):
        """Scan a directory for scenario YAML files

        Args:
            directory: Directory to scan
        """
        for yaml_file in directory.rglob("*.yaml"):
            # Skip files starting with underscore or dot
            if yaml_file.name.startswith(("_", ".")):
                continue

            # Also check .yml extension
            if yaml_file.suffix not in ['.yaml', '.yml']:
                continue

            self._load_scenario_from_file(yaml_file)

        # Also scan for .yml files
        for yml_file in directory.rglob("*.yml"):
            if yml_file.name.startswith(("_", ".")):
                continue
            self._load_scenario_from_file(yml_file)

    def _load_scenario_from_file(self, file_path: Path):
        """Load a scenario from a YAML file

        Args:
            file_path: Path to YAML file
        """
        try:
            scenario_def = self.loader.load_from_yaml(file_path)

            # Validate scenario
            errors = self.loader.validate_scenario(scenario_def)
            if errors:
                warnings.warn(
                    f"Invalid scenario in {file_path}:\n" +
                    "\n".join(f"  - {err}" for err in errors)
                )
                return

            scenario_info = scenario_def.get('scenario', {})
            scenario_id = scenario_info.get('id')

            if not scenario_id:
                warnings.warn(f"Scenario in {file_path} has no id, skipping")
                return

            # Check for duplicate IDs
            if scenario_id in self.scenarios:
                existing_source = self.scenarios[scenario_id]['source']
                warnings.warn(
                    f"Duplicate scenario ID '{scenario_id}': "
                    f"{file_path} (overrides {existing_source})"
                )

            # Register scenario
            self.scenarios[scenario_id] = {
                "definition": scenario_def,
                "source": str(file_path),
                "source_type": "yaml"
            }

        except Exception as e:
            warnings.warn(f"Failed to load scenario from {file_path}: {e}")

    def register_scenario_from_yaml(self, yaml_path: Path):
        """Manually register a scenario from YAML file

        Args:
            yaml_path: Path to YAML file

        Example:
            >>> registry.register_scenario_from_yaml("./my_scenario.yaml")
        """
        self._load_scenario_from_file(yaml_path)

    def register_scenario_from_dict(self, scenario_def: dict, scenario_id: str):
        """Manually register a scenario from dictionary

        Args:
            scenario_def: Scenario definition dictionary
            scenario_id: Unique scenario ID

        Example:
            >>> scenario_def = {
            ...     "scenario": {"id": "test", "name": "Test"},
            ...     "steps": [{"node": "@common/get_files", "name": "get_files"}]
            ... }
            >>> registry.register_scenario_from_dict(scenario_def, "test")
        """
        errors = self.loader.validate_scenario(scenario_def)
        if errors:
            raise ValueError(f"Invalid scenario:\n" + "\n".join(f"  - {err}" for err in errors))

        self.scenarios[scenario_id] = {
            "definition": scenario_def,
            "source": "manual",
            "source_type": "dict"
        }

    def register_from_directory(self, directory: str, recursive: bool = False) -> List[str]:
        """Register all scenarios from a directory

        Args:
            directory: Directory path
            recursive: If True, scan subdirectories recursively

        Returns:
            List of registered scenario IDs

        Raises:
            FileNotFoundError: If directory doesn't exist
            ValueError: If directory is not a directory

        Example:
            >>> registry.register_from_directory("./custom_scenarios", recursive=True)
            ['scenario1', 'scenario2']
        """
        from pathlib import Path

        path = Path(directory).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not path.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        initial_ids = set(self.scenarios.keys())

        if recursive:
            pattern = "**/*.yaml"
        else:
            pattern = "*.yaml"

        for yaml_file in path.glob(pattern):
            if yaml_file.name.startswith("_") or yaml_file.name.startswith("."):
                continue
            try:
                self._load_scenario_from_file(yaml_file)
            except Exception as e:
                warnings.warn(f"Failed to load {yaml_file}: {e}")

        new_ids = [sid for sid in self.scenarios.keys() if sid not in initial_ids]
        return new_ids

    def get_scenario(self, scenario_id: str) -> dict:
        """Get scenario definition by ID

        Args:
            scenario_id: Scenario ID

        Returns:
            Scenario definition dictionary

        Raises:
            ValueError: If scenario not found
        """
        if scenario_id not in self.scenarios:
            raise ValueError(
                f"Scenario not found: {scenario_id}\n"
                f"Available scenarios: {', '.join(self.scenarios.keys())}"
            )

        return self.scenarios[scenario_id]["definition"]

    def list_scenarios(self) -> List[dict]:
        """List all registered scenarios

        Returns:
            List of scenario metadata dictionaries

        Example:
            >>> scenarios = registry.list_scenarios()
            >>> for s in scenarios:
            ...     print(s['id'], s['name'])
        """
        result = []

        for scenario_id, scenario_info in sorted(self.scenarios.items()):
            scenario_def = scenario_info["definition"]
            scenario_meta = scenario_def.get("scenario", {})

            result.append({
                "id": scenario_id,
                "name": scenario_meta.get("name", scenario_id),
                "description": scenario_meta.get("description", ""),
                "author": scenario_meta.get("author", ""),
                "version": scenario_meta.get("version", "1.0.0"),
                "source": scenario_info["source"],
                "source_type": scenario_info["source_type"],
                "parameters": scenario_def.get("parameters", {})
            })

        return result

    def run_scenario(self, scenario_id: str, user_params: Optional[dict] = None) -> dict:
        """Run a scenario with given parameters

        Args:
            scenario_id: Scenario ID to run
            user_params: User-provided parameters

        Returns:
            Shared context dictionary after flow execution

        Raises:
            ValueError: If scenario not found

        Example:
            >>> result = registry.run_scenario("my_scenario", {
            ...     "patterns": ["**/*.py"],
            ...     "model": "gpt-4"
            ... })
            >>> print(result.get("llm_response"))
        """
        scenario_def = self.get_scenario(scenario_id)

        # Build flow
        flow = self.loader.create_flow(scenario_def, user_params)

        # Initialize shared context
        shared_store = user_params.copy() if user_params else {}
        if "project_root" not in shared_store:
            shared_store["project_root"] = str(Path.cwd())

        # Run flow
        result = flow.run(shared_store)

        return result

    def get_scenario_cli_params(self, scenario_id: str) -> dict:
        """Get CLI parameter definitions for a scenario

        This is used to generate Click options for dynamic CLI commands.

        Args:
            scenario_id: Scenario ID

        Returns:
            Dictionary mapping parameter names to their definitions

        Example:
            >>> params = registry.get_scenario_cli_params("my_scenario")
            >>> # params = {
            >>> #     "patterns": {
            >>> #         "type": "list",
            >>> #         "default": ["**/*.py"],
            >>> #         "help": "File patterns to match"
            >>> #     }
            >>> # }
        """
        scenario_def = self.get_scenario(scenario_id)
        return scenario_def.get("parameters", {})
