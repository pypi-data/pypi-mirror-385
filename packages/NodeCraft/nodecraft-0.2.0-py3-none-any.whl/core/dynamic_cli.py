"""
Dynamic CLI Command Generation

Automatically generates Click commands from registered scenarios,
enabling users to run scenarios directly without the 'scenarios run' prefix.

Example:
    Instead of:  outcomeforge scenarios run simple_rag --params '{"query": "..."}'
    Use:         outcomeforge simple_rag --query "..."
"""

import click
from typing import Dict, Any, List


def generate_scenario_command(scenario_id: str, scenario_def: dict, scenario_registry):
    """Generate a Click command for a scenario

    Args:
        scenario_id: Scenario ID
        scenario_def: Scenario definition dictionary
        scenario_registry: ScenarioRegistry instance

    Returns:
        Click command function

    Example:
        >>> cmd = generate_scenario_command("simple_rag", scenario_def, registry)
        >>> cli.add_command(cmd)
    """
    scenario_info = scenario_def.get('scenario', {})
    parameters = scenario_def.get('parameters', {})

    # Create command function
    @click.command(name=scenario_id)
    @click.option('--with-context', is_flag=True, help='Inject RAG context before execution')
    @click.option('--context-patterns', multiple=True, help='File patterns for context')
    @click.option('--context-query', type=str, help='Query to ask about the context')
    @click.pass_context
    def scenario_command(ctx, with_context, context_patterns, context_query, **kwargs):
        # This docstring will be set dynamically
        pass

    # Set docstring from scenario description
    description = scenario_info.get('description', 'Run scenario')
    example_usage = f"\n\nExample:\n  outcomeforge {scenario_id}"

    # Add parameter info to docstring
    if parameters:
        param_docs = "\n\nParameters:"
        for param_name, param_def in parameters.items():
            param_type = param_def.get('type', 'str')
            default = param_def.get('default', 'N/A')
            desc = param_def.get('description', '')
            param_docs += f"\n  --{param_name} ({param_type}) [default: {default}]"
            if desc:
                param_docs += f"\n    {desc}"
        description += param_docs

    scenario_command.__doc__ = description + example_usage

    # Dynamically add parameter options to the command
    for param_name, param_def in reversed(list(parameters.items())):
        param_type = param_def.get('type', 'str')
        default = param_def.get('default')
        required = param_def.get('required', False)
        help_text = param_def.get('description', '')

        # Convert type string to Python type
        if param_type == 'int':
            click_type = int
        elif param_type == 'float':
            click_type = float
        elif param_type == 'bool':
            # Boolean parameters are flags
            option = click.option(
                f'--{param_name}',
                is_flag=True,
                default=default if default is not None else False,
                help=help_text
            )
            scenario_command = option(scenario_command)
            continue
        elif param_type == 'list':
            # List parameters use multiple=True
            option = click.option(
                f'--{param_name}',
                multiple=True,
                default=default,
                help=help_text + " (can specify multiple times)"
            )
            scenario_command = option(scenario_command)
            continue
        else:
            click_type = str

        # Add option
        option = click.option(
            f'--{param_name}',
            type=click_type,
            default=default,
            required=required and default is None,
            help=help_text
        )
        scenario_command = option(scenario_command)

    # Replace the callback with actual execution logic
    def execute_scenario(with_context, context_patterns, context_query, **user_params):
        """Execute the scenario with provided parameters"""
        click.echo(f"Running scenario: {scenario_id}")
        click.echo(f"Parameters: {user_params}")

        # Handle context injection
        if with_context:
            click.echo("Context injection: ENABLED")
            if context_patterns:
                click.echo(f"Context patterns: {', '.join(context_patterns)}")
            if context_query:
                click.echo(f"Context query: {context_query}")
            click.echo()

            from core.context_integration import inject_context_to_scenario_run

            context_config = {
                "enabled": True,
                "patterns": list(context_patterns) if context_patterns else None,
                "query": context_query
            }

            result = inject_context_to_scenario_run(
                scenario_registry,
                scenario_id,
                user_params,
                context_config=context_config
            )
        else:
            click.echo()
            result = scenario_registry.run_scenario(scenario_id, user_params)

        # Display results
        click.echo("\nScenario completed successfully!")
        click.echo("\nResults:")
        click.echo("-" * 80)

        for key, value in result.items():
            if key.startswith("_"):
                continue
            if isinstance(value, (str, int, float, bool)):
                click.echo(f"{key}: {value}")
            elif isinstance(value, list):
                click.echo(f"{key}: {len(value)} items")

        if "llm_response" in result:
            click.echo("\nLLM Response:")
            click.echo("-" * 80)
            click.echo(result["llm_response"])

    scenario_command.callback = execute_scenario

    return scenario_command


def register_dynamic_commands(cli_group, scenario_registry, node_registry):
    """Register all discovered scenarios as dynamic CLI commands

    Args:
        cli_group: Click Group to add commands to
        scenario_registry: ScenarioRegistry instance
        node_registry: NodeRegistry instance

    Example:
        >>> from click import Group
        >>> cli = Group()
        >>> register_dynamic_commands(cli, scenario_registry, node_registry)
    """
    # Auto-discover nodes and scenarios
    try:
        node_registry.auto_discover()

        # Add templates directory
        try:
            import outcomeforge
            from pathlib import Path
            templates_dir = Path(outcomeforge.__file__).parent / "scenarios" / "templates"
        except (ImportError, AttributeError):
            from pathlib import Path
            import sys
            templates_dir = Path(sys.argv[0]).parent / "scenarios" / "templates"

        if templates_dir.exists():
            scenario_registry.auto_discover(additional_dirs=[str(templates_dir)])

        # Generate commands for each scenario
        for scenario_id, scenario_info in scenario_registry.scenarios.items():
            scenario_def = scenario_info["definition"]

            # Skip scenarios that start with underscore (internal)
            if scenario_id.startswith("_"):
                continue

            # Generate and add command
            try:
                cmd = generate_scenario_command(scenario_id, scenario_def, scenario_registry)
                cli_group.add_command(cmd)
            except Exception as e:
                import warnings
                warnings.warn(f"Failed to generate command for scenario '{scenario_id}': {e}")

    except Exception as e:
        import warnings
        warnings.warn(f"Failed to register dynamic commands: {e}")


def create_dynamic_cli():
    """Create a CLI with dynamically registered scenario commands

    This is a convenience function for creating a full CLI with
    all scenarios automatically registered as commands.

    Returns:
        Click Group with dynamic commands

    Example:
        >>> cli = create_dynamic_cli()
        >>> if __name__ == '__main__':
        ...     cli()
    """
    from core import node_registry, scenario_registry

    @click.group()
    def dynamic_cli():
        """OutcomeForge with dynamic scenario commands"""
        pass

    register_dynamic_commands(dynamic_cli, scenario_registry, node_registry)

    return dynamic_cli
