"""
Scenario Loader - YAML-based scenario definition and flow construction

This module provides:
- Loading scenarios from YAML files
- Parameter validation and merging
- Building Flow objects from YAML definitions
- Template rendering for dynamic parameters
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from jinja2 import Template


class ScenarioLoader:
    """Load and build scenarios from YAML definitions

    Example YAML structure:
        scenario:
          id: my_scenario
          name: My Scenario
          description: Does something useful

        parameters:
          patterns:
            type: list
            default: ["**/*.py"]
            description: File patterns

        steps:
          - node: "@common/get_files"
            name: get_files
            params:
              patterns: "{{params.patterns}}"

          - node: "@common/call_llm"
            name: analyze
            params:
              model: "gpt-4"
    """

    def __init__(self, node_registry):
        """Initialize loader with node registry

        Args:
            node_registry: NodeRegistry instance for resolving node references
        """
        self.node_registry = node_registry

    def load_from_yaml(self, yaml_path: Path) -> dict:
        """Load scenario definition from YAML file

        Args:
            yaml_path: Path to YAML file

        Returns:
            Scenario definition dictionary

        Raises:
            FileNotFoundError: If YAML file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        if not yaml_path.exists():
            raise FileNotFoundError(f"Scenario file not found: {yaml_path}")

        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data or 'scenario' not in data:
            raise ValueError(f"Invalid scenario file: missing 'scenario' key in {yaml_path}")

        return data

    def load_from_string(self, yaml_content: str) -> dict:
        """Load scenario definition from YAML string

        Args:
            yaml_content: YAML content as string

        Returns:
            Scenario definition dictionary
        """
        data = yaml.safe_load(yaml_content)

        if not data or 'scenario' not in data:
            raise ValueError("Invalid scenario: missing 'scenario' key")

        return data

    def create_flow(self, scenario_def: dict, user_params: Optional[dict] = None):
        """Create a Flow object from scenario definition

        Args:
            scenario_def: Scenario definition from YAML
            user_params: User-provided parameters (overrides defaults)

        Returns:
            Flow object ready to execute

        Example:
            >>> loader = ScenarioLoader(node_registry)
            >>> scenario = loader.load_from_yaml("my_scenario.yaml")
            >>> flow = loader.create_flow(scenario, {"patterns": ["**/*.js"]})
            >>> result = flow.run({"project_root": "."})
        """
        from engine import flow

        f = flow()
        user_params = user_params or {}

        # Merge parameters
        params = self._merge_parameters(
            scenario_def.get('parameters', {}),
            user_params
        )

        # Build context for template rendering
        template_context = {
            'params': params,
            'context': {}
        }

        # Add each step to the flow
        for step_def in scenario_def.get('steps', []):
            # Check condition if present
            condition = step_def.get('condition')
            if condition and not self._eval_condition(condition, params, {}):
                continue

            # Get node reference
            node_id = step_def['node']
            node_name = step_def.get('name', node_id.split('/')[-1])

            # Render parameters
            step_params = step_def.get('params', {})
            rendered_params = self._render_params(step_params, template_context)

            # Get node instance
            try:
                node_instance = self.node_registry.get_node(node_id)
            except ValueError as e:
                raise ValueError(
                    f"Failed to resolve node '{node_id}' in step '{node_name}': {e}"
                )

            # Add to flow
            f.add(node_instance, name=node_name, params=rendered_params)

        return f

    def _merge_parameters(self, param_schema: dict, user_params: dict) -> dict:
        """Merge parameter schema defaults with user-provided values

        Args:
            param_schema: Parameter schema from YAML
            user_params: User-provided parameter values

        Returns:
            Merged parameters dictionary

        Raises:
            ValueError: If required parameter is missing
        """
        result = {}

        for param_name, param_def in param_schema.items():
            if param_name in user_params:
                # User provided value
                result[param_name] = user_params[param_name]
            elif 'default' in param_def:
                # Use default
                result[param_name] = param_def['default']
            elif param_def.get('required', False):
                # Required but not provided
                raise ValueError(f"Required parameter missing: {param_name}")

        # Add any extra user params not in schema
        for param_name, value in user_params.items():
            if param_name not in result:
                result[param_name] = value

        return result

    def _render_params(self, params: dict, template_context: dict) -> dict:
        """Render parameter values using Jinja2 templates

        Supports {{params.xxx}} and {{context.xxx}} placeholders.

        Args:
            params: Parameters dictionary with potential template strings
            template_context: Context for template rendering

        Returns:
            Rendered parameters dictionary

        Example:
            >>> params = {"patterns": "{{params.file_patterns}}"}
            >>> context = {"params": {"file_patterns": ["**/*.py"]}}
            >>> rendered = loader._render_params(params, context)
            >>> # rendered = {"patterns": ["**/*.py"]}
        """
        result = {}

        for key, value in params.items():
            if isinstance(value, str) and "{{" in value and "}}" in value:
                # Render template
                try:
                    template = Template(value)
                    rendered = template.render(**template_context)

                    # Try to evaluate as Python literal (for lists, etc.)
                    try:
                        import ast
                        result[key] = ast.literal_eval(rendered)
                    except (ValueError, SyntaxError):
                        # Keep as string
                        result[key] = rendered
                except Exception as e:
                    raise ValueError(f"Failed to render template for param '{key}': {e}")
            elif isinstance(value, dict):
                # Recursively render nested dict
                result[key] = self._render_params(value, template_context)
            elif isinstance(value, list):
                # Render each item in list
                result[key] = [
                    self._render_params({"item": item}, template_context).get("item", item)
                    if isinstance(item, (dict, str)) else item
                    for item in value
                ]
            else:
                # Use as-is
                result[key] = value

        return result

    def _eval_condition(self, condition: str, params: dict, context: dict) -> bool:
        """Evaluate a condition expression

        Supports simple Python expressions with params and context.

        Args:
            condition: Condition string (e.g., "params.auto_fix and context.critical_issues > 0")
            params: Parameters dictionary
            context: Context dictionary

        Returns:
            True if condition evaluates to true

        Example:
            >>> condition = "params.auto_fix"
            >>> loader._eval_condition(condition, {"auto_fix": True}, {})
            True
        """
        try:
            # Create safe evaluation environment
            eval_env = {
                'params': params,
                'context': context,
                '__builtins__': {
                    # Allow safe built-ins
                    'True': True,
                    'False': False,
                    'None': None,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                }
            }

            return bool(eval(condition, {"__builtins__": eval_env['__builtins__']}, eval_env))
        except Exception as e:
            # If evaluation fails, default to False
            import warnings
            warnings.warn(f"Failed to evaluate condition '{condition}': {e}. Defaulting to False.")
            return False

    def validate_scenario(self, scenario_def: dict) -> List[str]:
        """Validate scenario definition

        Args:
            scenario_def: Scenario definition to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check required top-level keys
        if 'scenario' not in scenario_def:
            errors.append("Missing 'scenario' key")
            return errors

        scenario_info = scenario_def['scenario']

        # Check scenario metadata
        if 'id' not in scenario_info:
            errors.append("Missing 'scenario.id'")

        # Check steps
        if 'steps' not in scenario_def:
            errors.append("Missing 'steps' key")
        else:
            steps = scenario_def['steps']
            if not isinstance(steps, list):
                errors.append("'steps' must be a list")
            else:
                for i, step in enumerate(steps):
                    if 'node' not in step:
                        errors.append(f"Step {i}: missing 'node' key")

        return errors
