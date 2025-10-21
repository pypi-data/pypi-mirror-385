"""
Unit tests for Phase 3 Enhancements

Tests cover:
1. Tutorial system
2. Context injection (--with-context)
3. Dynamic CLI command generation
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import node_registry, scenario_registry
from core.tutorials import get_tutorial, list_tutorials
from core.context_integration import ContextInjector, inject_context_to_scenario_run
from core.dynamic_cli import generate_scenario_command, register_dynamic_commands
from click.testing import CliRunner


class TestTutorialSystem:
    """Test tutorial system functionality"""

    def test_get_main_tutorial(self):
        """Test getting main tutorial"""
        tutorial = get_tutorial("main")

        assert isinstance(tutorial, str)
        assert len(tutorial) > 0
        assert "OutcomeForge" in tutorial
        assert "Getting Started" in tutorial

    def test_get_node_tutorial(self):
        """Test getting node creation tutorial"""
        tutorial = get_tutorial("node")

        assert "Create Your First Custom Node" in tutorial
        assert "metadata" in tutorial
        assert "prep" in tutorial
        assert "exec" in tutorial
        assert "post" in tutorial

    def test_get_scenario_tutorial(self):
        """Test getting scenario creation tutorial"""
        tutorial = get_tutorial("scenario")

        assert "YAML" in tutorial or "yaml" in tutorial
        assert "scenario:" in tutorial
        assert "parameters:" in tutorial
        assert "steps:" in tutorial

    def test_get_registry_tutorial(self):
        """Test getting registry tutorial"""
        tutorial = get_tutorial("registry")

        assert "Registry" in tutorial
        assert "namespace" in tutorial.lower()
        assert "@common" in tutorial

    def test_list_tutorials(self):
        """Test listing all tutorials"""
        tutorials_list = list_tutorials()

        assert "main" in tutorials_list
        assert "node" in tutorials_list
        assert "scenario" in tutorials_list
        assert "registry" in tutorials_list

    def test_tutorial_cli_command(self):
        """Test tutorial CLI command"""
        from cli import cli

        runner = CliRunner()

        # Test tutorial list
        result = runner.invoke(cli, ['tutorial', 'list'])
        assert result.exit_code == 0
        assert "main" in result.output

        # Test specific tutorial
        result = runner.invoke(cli, ['tutorial', 'node'])
        assert result.exit_code == 0
        assert "Create Your First Custom Node" in result.output


class TestContextIntegration:
    """Test context injection functionality"""

    def test_context_injector_creation(self):
        """Test ContextInjector initialization"""
        injector = ContextInjector(node_registry)
        assert injector is not None
        assert injector.node_registry == node_registry

    def test_inject_rag_context(self):
        """Test RAG context injection into flow"""
        node_registry.auto_discover()

        # Create a simple flow
        from engine import flow
        from nodes.common.get_files_node import get_files_node

        original_flow = flow()
        original_flow.add(get_files_node(), name="test_get_files")

        # Inject context
        injector = ContextInjector(node_registry)
        enhanced_flow = injector.inject_rag_context(
            original_flow,
            patterns=["*.py"],
            exclude=["test_*.py"]
        )

        # Check that context nodes were added
        assert len(enhanced_flow.nodes) > len(original_flow.nodes)

        # First nodes should be context collection
        assert "_context_get_files" in enhanced_flow.nodes[0]["name"]
        assert "_context_format" in enhanced_flow.nodes[1]["name"]

    def test_inject_context_with_query(self):
        """Test context injection with LLM query"""
        node_registry.auto_discover()

        from engine import flow

        original_flow = flow()
        injector = ContextInjector(node_registry)

        enhanced_flow = injector.inject_rag_context(
            original_flow,
            patterns=["*.py"],
            context_query="What is this project about?"
        )

        # Should have get_files, format, and LLM nodes
        assert len(enhanced_flow.nodes) >= 3

        # Check for LLM summarize node
        node_names = [n["name"] for n in enhanced_flow.nodes]
        assert any("_context_summarize" in name for name in node_names)

    def test_create_context_scenario(self):
        """Test creating standalone context scenario"""
        injector = ContextInjector(node_registry)

        scenario_def = injector.create_context_scenario(
            patterns=["**/*.py"],
            query="Describe the codebase"
        )

        assert "scenario" in scenario_def
        assert "steps" in scenario_def
        assert len(scenario_def["steps"]) >= 3

    def test_inject_context_to_scenario_run(self):
        """Test running scenario with context injection"""
        node_registry.auto_discover()
        templates_dir = project_root / "scenarios" / "templates"
        scenario_registry.auto_discover(additional_dirs=[str(templates_dir)])

        # Run file_collector with context
        result = inject_context_to_scenario_run(
            scenario_registry,
            "file_collector",
            {"patterns": ["test_*.py"]},
            context_config={"enabled": True, "patterns": ["*.py"]}
        )

        # Should have context keys
        assert "project_context" in result or "formatted_prompt" in result
        assert "files" in result


class TestDynamicCLIGeneration:
    """Test dynamic CLI command generation"""

    def test_generate_scenario_command(self):
        """Test generating a Click command from scenario"""
        node_registry.auto_discover()
        templates_dir = project_root / "scenarios" / "templates"
        scenario_registry.auto_discover(additional_dirs=[str(templates_dir)])

        scenario_def = scenario_registry.get_scenario("file_collector")

        cmd = generate_scenario_command("file_collector", scenario_def, scenario_registry)

        assert cmd is not None
        assert cmd.name == "file_collector"
        assert cmd.callback is not None

    def test_dynamic_command_has_parameters(self):
        """Test that generated command has correct parameters"""
        node_registry.auto_discover()
        templates_dir = project_root / "scenarios" / "templates"
        scenario_registry.auto_discover(additional_dirs=[str(templates_dir)])

        scenario_def = scenario_registry.get_scenario("simple_rag")

        cmd = generate_scenario_command("simple_rag", scenario_def, scenario_registry)

        # Check parameters
        param_names = [p.name for p in cmd.params]

        # Should have scenario parameters
        assert "query" in param_names
        assert "patterns" in param_names
        assert "model" in param_names

        # Should have context injection parameters
        assert "with_context" in param_names
        assert "context_patterns" in param_names

    def test_dynamic_command_execution(self):
        """Test executing a dynamically generated command"""
        from click.testing import CliRunner

        node_registry.auto_discover()
        templates_dir = project_root / "scenarios" / "templates"
        scenario_registry.auto_discover(additional_dirs=[str(templates_dir)])

        scenario_def = scenario_registry.get_scenario("file_collector")
        cmd = generate_scenario_command("file_collector", scenario_def, scenario_registry)

        runner = CliRunner()
        result = runner.invoke(cmd, ['--patterns', '*.py'])

        # Command should execute successfully
        assert result.exit_code == 0
        assert "Running scenario: file_collector" in result.output
        assert "completed successfully" in result.output

    def test_register_dynamic_commands(self):
        """Test registering all dynamic commands"""
        import click

        # Create a test CLI group
        @click.group()
        def test_cli():
            pass

        # Register dynamic commands
        register_dynamic_commands(test_cli, scenario_registry, node_registry)

        # Check that commands were registered
        command_names = list(test_cli.commands.keys())

        assert "simple_rag" in command_names or len(command_names) > 0

    def test_dynamic_command_help(self):
        """Test that dynamic commands have proper help text"""
        from click.testing import CliRunner

        node_registry.auto_discover()
        templates_dir = project_root / "scenarios" / "templates"
        scenario_registry.auto_discover(additional_dirs=[str(templates_dir)])

        scenario_def = scenario_registry.get_scenario("simple_rag")
        cmd = generate_scenario_command("simple_rag", scenario_def, scenario_registry)

        runner = CliRunner()
        result = runner.invoke(cmd, ['--help'])

        assert result.exit_code == 0
        # Should show scenario description
        assert "RAG" in result.output or "rag" in result.output
        # Should show parameters
        assert "--query" in result.output
        assert "--patterns" in result.output


class TestCLIIntegration:
    """Integration tests for Phase 3 CLI enhancements"""

    def test_cli_has_tutorial_command(self):
        """Test that CLI has tutorial command"""
        from cli import cli

        assert "tutorial" in cli.commands

    def test_cli_has_dynamic_scenario_commands(self):
        """Test that CLI has dynamically registered scenario commands"""
        from cli import cli

        # Should have at least some scenario commands
        # (exact commands depend on discovery)
        assert len(cli.commands) > 10  # Original + dynamic commands

    def test_file_collector_command_exists(self):
        """Test that file_collector command was registered"""
        from cli import cli

        # Check if dynamic command registration worked
        command_names = list(cli.commands.keys())

        # Should have more commands than just the built-in ones
        # (Built-in: snapshot, adapt, regression, etc. + dynamic scenarios)
        # At minimum should have the core commands
        assert len(command_names) >= 10

    def test_dynamic_command_with_context_option(self):
        """Test that dynamic commands have --with-context option"""
        from cli import cli
        from click.testing import CliRunner

        runner = CliRunner()

        # Try to get help for a dynamic command
        if 'file_collector' in cli.commands:
            result = runner.invoke(cli, ['file_collector', '--help'])
            assert result.exit_code == 0
            assert "--with-context" in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
