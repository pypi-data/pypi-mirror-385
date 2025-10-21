"""
Helper functions for template generation display and validation
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional


def visualize_workflow(yaml_path: str) -> str:
    """Generate a visual representation of a workflow from YAML

    Args:
        yaml_path: Path to the scenario YAML file

    Returns:
        str: Formatted workflow visualization
    """
    try:
        import yaml
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return f"WARNING: Could not parse workflow: {e}"

    steps = data.get('steps', [])
    if not steps:
        return "WARNING: No workflow steps found"

    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("Workflow Visualization")
    lines.append("=" * 80)

    # Show parameters
    params = data.get('parameters', {})
    if params:
        lines.append("\nParameters:")
        for param_name, param_def in params.items():
            required = "required" if param_def.get('required') else "optional"
            default = param_def.get('default', 'N/A')
            param_type = param_def.get('type', 'any')
            lines.append(f"  * {param_name} ({param_type}, {required})")
            if default != 'N/A':
                lines.append(f"    Default: {default}")

    # Show workflow steps
    lines.append("\nWorkflow Steps:")
    for i, step in enumerate(steps, 1):
        node = step.get('node', 'unknown')
        name = step.get('name', f'step_{i}')
        params = step.get('params', {})

        # Arrow for flow
        if i == 1:
            lines.append(f"\n  Step {i}: {name}")
        else:
            lines.append(f"  |")
            lines.append(f"  v")
            lines.append(f"  Step {i}: {name}")

        lines.append(f"    Node: {node}")

        if params:
            lines.append(f"    Params:")
            for pk, pv in params.items():
                lines.append(f"      - {pk}: {pv}")

    # Output
    lines.append(f"\n  |")
    lines.append(f"  v")
    lines.append(f"  [Complete]")
    lines.append("\n" + "=" * 80)

    return "\n".join(lines)


def visualize_node_structure(py_path: str) -> str:
    """Generate a visual representation of a node's structure

    Args:
        py_path: Path to the Python node file

    Returns:
        str: Formatted structure visualization
    """
    try:
        with open(py_path, 'r') as f:
            content = f.read()
    except Exception as e:
        return f"WARNING: Could not read file: {e}"

    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("Node Structure")
    lines.append("=" * 80)

    # Extract key components
    has_metadata = 'metadata = {' in content
    has_prep = 'def prep(' in content
    has_exec = 'def exec(' in content
    has_post = 'def post(' in content

    # Count TODOs
    todo_count = content.count('TODO')

    lines.append("\nComponents:")

    if has_metadata:
        lines.append("  [x] Metadata")

        # Extract metadata details
        if '"id":' in content or "'id':" in content:
            lines.append("    |-- id")
        if '"namespace":' in content or "'namespace':" in content:
            lines.append("    |-- namespace")
        if '"params_schema":' in content or "'params_schema':" in content:
            lines.append("    |-- params_schema")
        if '"input_keys":' in content or "'input_keys':" in content:
            lines.append("    |-- input_keys")
        if '"output_keys":' in content or "'output_keys':" in content:
            lines.append("    +-- output_keys")

    lines.append("\nFunctions:")
    if has_prep:
        lines.append("  [x] prep()   - Input validation and setup")
    if has_exec:
        lines.append("  [x] exec()   - Main business logic")
    if has_post:
        lines.append("  [x] post()   - Cleanup and finalization")

    if todo_count > 0:
        lines.append(f"\nReady to implement: {todo_count} TODO items found")
    else:
        lines.append(f"\n[OK] No TODOs - Implementation complete")

    lines.append("\n" + "=" * 80)

    return "\n".join(lines)


def validate_node_file(py_path: str) -> Tuple[bool, List[str], List[str]]:
    """Validate a Python node file

    Args:
        py_path: Path to the Python node file

    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    try:
        with open(py_path, 'r') as f:
            content = f.read()
    except Exception as e:
        errors.append(f"Could not read file: {e}")
        return False, errors, warnings

    # Syntax validation
    try:
        ast.parse(content)
    except SyntaxError as e:
        errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        return False, errors, warnings

    # Structure validation
    required_components = [
        ('metadata = {', 'Missing metadata definition'),
        ('def prep(', 'Missing prep() function'),
        ('def exec(', 'Missing exec() function'),
        ('def post(', 'Missing post() function'),
        ('node(prep=', 'Missing node() decorator call')
    ]

    for pattern, error_msg in required_components:
        if pattern not in content:
            errors.append(error_msg)

    # Check for common issues
    if 'from engine import node' not in content and 'from core.engine import node' not in content:
        warnings.append("Missing 'from engine import node' import")

    # Check if metadata has required fields
    if '"id"' not in content and "'id'" not in content:
        warnings.append("Metadata missing 'id' field")

    if '"namespace"' not in content and "'namespace'" not in content:
        warnings.append("Metadata missing 'namespace' field")

    is_valid = len(errors) == 0

    return is_valid, errors, warnings


def validate_scenario_file(yaml_path: str) -> Tuple[bool, List[str], List[str]]:
    """Validate a scenario YAML file

    Args:
        yaml_path: Path to the scenario YAML file

    Returns:
        Tuple of (is_valid, errors, warnings)
    """
    errors = []
    warnings = []

    try:
        import yaml
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        errors.append(f"YAML syntax error: {e}")
        return False, errors, warnings
    except Exception as e:
        errors.append(f"Could not read file: {e}")
        return False, errors, warnings

    # Structure validation
    if not isinstance(data, dict):
        errors.append("YAML root must be a dictionary")
        return False, errors, warnings

    # Check required sections
    if 'scenario' not in data:
        errors.append("Missing 'scenario' section")
    else:
        scenario = data['scenario']
        if 'id' not in scenario:
            errors.append("Scenario missing 'id' field")
        if 'name' not in scenario:
            warnings.append("Scenario missing 'name' field")

    if 'steps' not in data:
        errors.append("Missing 'steps' section")
    else:
        steps = data['steps']
        if not isinstance(steps, list):
            errors.append("'steps' must be a list")
        elif len(steps) == 0:
            warnings.append("No workflow steps defined")
        else:
            # Validate each step
            for i, step in enumerate(steps, 1):
                if 'node' not in step:
                    errors.append(f"Step {i} missing 'node' field")

    # Check parameters section
    if 'parameters' in data:
        params = data['parameters']
        if not isinstance(params, dict):
            warnings.append("'parameters' should be a dictionary")

    is_valid = len(errors) == 0

    return is_valid, errors, warnings


def display_validation_result(is_valid: bool, errors: List[str], warnings: List[str]) -> str:
    """Format validation results for display

    Args:
        is_valid: Whether validation passed
        errors: List of error messages
        warnings: List of warning messages

    Returns:
        str: Formatted validation result
    """
    lines = []
    lines.append("\n" + "─" * 80)
    lines.append("Validation Results")
    lines.append("─" * 80)

    if is_valid:
        lines.append("[OK] Syntax validation passed")
        lines.append("[OK] Structure validation passed")
    else:
        lines.append("[FAIL] Validation failed")

    if errors:
        lines.append(f"\nErrors ({len(errors)}):")
        for error in errors:
            lines.append(f"  * {error}")

    if warnings:
        lines.append(f"\nWarnings ({len(warnings)}):")
        for warning in warnings:
            lines.append(f"  * {warning}")

    if is_valid and not warnings:
        lines.append("\n[SUCCESS] File is ready to use!")

    lines.append("─" * 80)

    return "\n".join(lines)


def get_enhanced_next_steps(
    file_type: str,
    name: str,
    namespace: str,
    output_file: str,
    template_type: Optional[str] = None
) -> str:
    """Generate enhanced next steps guidance

    Args:
        file_type: 'node' or 'scenario'
        name: The name/id
        namespace: The namespace (for nodes)
        output_file: Path to the created file
        template_type: Template type used

    Returns:
        str: Formatted next steps guidance
    """
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("Next Steps")
    lines.append("=" * 80)

    if file_type == 'node':
        lines.append("\n[Step 1] Implement the node logic:")
        lines.append(f"   Edit: {output_file}")
        lines.append("   * Fill in params_schema with your parameters")
        lines.append("   * Define input_keys (data from context)")
        lines.append("   * Define output_keys (data to context)")
        lines.append("   * Implement prep() for validation")
        lines.append("   * Implement exec() for main logic")
        lines.append("   * Implement post() for cleanup (optional)")

        lines.append("\n[Step 2] Register the node:")
        lines.append(f"   nodecraft nodes register {output_file}")

        lines.append("\n[Step 3] Test the node:")
        lines.append(f"   nodecraft nodes show @{namespace}/{name}")

        lines.append("\n[Step 4] Use in a scenario:")
        lines.append("   Add to your scenario YAML:")
        lines.append(f"   steps:")
        lines.append(f"     - node: \"@{namespace}/{name}\"")
        lines.append(f"       name: my_step")
        lines.append(f"       params:")
        lines.append(f"         # your parameters here")

        lines.append("\n[Quick Test]")
        lines.append(f"   nodecraft scenarios create --name test_{name} --template custom")
        lines.append(f"   # Then edit the YAML to add @{namespace}/{name}")

    elif file_type == 'scenario':
        lines.append("\n[Step 1] Customize the workflow:")
        lines.append(f"   Edit: {output_file}")
        lines.append("   * Adjust parameters in 'parameters' section")
        lines.append("   * Modify workflow steps in 'steps' section")
        lines.append("   * Add/remove nodes as needed")
        lines.append("   * Configure node parameters")

        lines.append("\n[Step 2] View available nodes:")
        lines.append("   nodecraft nodes list")
        lines.append("   nodecraft nodes show <node_id>")

        lines.append("\n[Step 3] Test the scenario:")
        lines.append(f"   nodecraft scenarios show {name}")

        lines.append("\n[Step 4] Run the scenario:")
        lines.append(f"   nodecraft scenarios run {name} --params '{{...}}'")

        lines.append("\n[Example]")
        lines.append('   nodecraft scenarios run {name} --params \'{"key": "value"}\'')

    lines.append("\n" + "=" * 80)

    return "\n".join(lines)


def preview_template(template_type: str, template_category: str) -> str:
    """Preview a template's content structure

    Args:
        template_type: The template name (e.g., 'function', 'rag-query')
        template_category: 'node' or 'scenario'

    Returns:
        str: Template preview
    """
    if template_category == 'node':
        from core.template_generator import NodeTemplateGenerator
        generator = NodeTemplateGenerator()

        # Get template path
        template_file = generator.TEMPLATES.get(template_type)
        if not template_file:
            return f"WARNING: Unknown template: {template_type}"

        template_path = generator.TEMPLATE_DIR / template_file

    elif template_category == 'scenario':
        from core.template_generator import ScenarioTemplateGenerator
        generator = ScenarioTemplateGenerator()

        # Get template path
        template_file = generator.TEMPLATES.get(template_type)
        if not template_file:
            return f"WARNING: Unknown template: {template_type}"

        template_path = generator.TEMPLATE_DIR / template_file
    else:
        return f"WARNING: Unknown category: {template_category}"

    try:
        with open(template_path, 'r') as f:
            content = f.read()
    except Exception as e:
        return f"WARNING: Could not read template: {e}"

    lines = []
    lines.append("\n" + "=" * 80)
    lines.append(f"Template Preview: {template_type}")
    lines.append("=" * 80)

    # Show first 30 lines or entire file if shorter
    content_lines = content.split('\n')
    preview_lines = content_lines[:30]

    lines.append("\n" + "\n".join(preview_lines))

    if len(content_lines) > 30:
        lines.append(f"\n... ({len(content_lines) - 30} more lines)")

    lines.append("\n" + "=" * 80)
    lines.append(f"Total lines: {len(content_lines)}")
    lines.append("=" * 80)

    return "\n".join(lines)
