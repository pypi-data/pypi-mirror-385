"""
Tests for Registration Commands (Phase 2.1)

Tests the explicit registration functionality for nodes and scenarios.
"""

import pytest
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.registry import NodeRegistry
from core.scenario_registry import ScenarioRegistry


class TestNodeRegistration:
    """Test Node registration functionality"""

    def test_register_from_file(self):
        """Test registering a node from a single file"""
        registry = NodeRegistry()

        test_node = Path(__file__).parent.parent / "nodes" / "common" / "get_files.py"
        if not test_node.exists():
            pytest.skip("Test node file not found")

        registered = registry.register_from_file(str(test_node), "common")
        assert len(registered) > 0
        assert any("get_files" in nid for nid in registered)

    def test_register_from_directory(self):
        """Test registering nodes from a directory"""
        registry = NodeRegistry()

        test_dir = Path(__file__).parent.parent / "nodes" / "common"
        if not test_dir.exists():
            pytest.skip("Test directory not found")

        registered = registry.register_from_directory(str(test_dir), "common", recursive=False)
        assert len(registered) > 0

    def test_register_from_directory_recursive(self):
        """Test registering nodes recursively"""
        registry = NodeRegistry()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            subdir = tmppath / "subdir"
            subdir.mkdir()

            test_node_content = '''
from engine import node

def test_node_node():
    """Test node"""
    metadata = {
        "id": "test_node",
        "namespace": "custom",
        "description": "Test node"
    }
    def prep(params, context):
        return {}
    def exec(params, context):
        return {"result": "success"}
    def post(params, context):
        return {}
    return node(prep, exec, post, metadata=metadata)
'''
            (tmppath / "root_node.py").write_text(test_node_content)
            (subdir / "sub_node.py").write_text(test_node_content.replace("test_node", "sub_node"))

            registered = registry.register_from_directory(str(tmppath), "custom", recursive=True)
            assert len(registered) == 2

    def test_register_from_nonexistent_file(self):
        """Test error handling for nonexistent file"""
        registry = NodeRegistry()

        with pytest.raises(FileNotFoundError):
            registry.register_from_file("/nonexistent/file.py")

    def test_register_from_invalid_file(self):
        """Test error handling for file with no valid nodes"""
        registry = NodeRegistry()

        with tempfile.TemporaryDirectory() as tmpdir:
            invalid_file = Path(tmpdir) / "invalid.py"
            invalid_file.write_text("# This file has no nodes")

            with pytest.raises(ValueError, match="No valid nodes found"):
                registry.register_from_file(str(invalid_file))


class TestScenarioRegistration:
    """Test Scenario registration functionality"""

    def test_register_from_file(self):
        """Test registering a scenario from a single YAML file"""
        node_registry = NodeRegistry()
        node_registry.auto_discover()
        registry = ScenarioRegistry(node_registry)

        test_scenario = Path(__file__).parent.parent / "scenarios" / "templates" / "file_collector.yaml"
        if not test_scenario.exists():
            pytest.skip("Test scenario file not found")

        registry.register_scenario_from_yaml(test_scenario)

        scenarios = registry.list_scenarios()
        assert any(s['id'] == 'file_collector' for s in scenarios)

    def test_register_from_directory(self):
        """Test registering scenarios from a directory"""
        node_registry = NodeRegistry()
        node_registry.auto_discover()
        registry = ScenarioRegistry(node_registry)

        test_dir = Path(__file__).parent.parent / "scenarios" / "templates"
        if not test_dir.exists():
            pytest.skip("Test directory not found")

        registered = registry.register_from_directory(str(test_dir), recursive=False)
        assert len(registered) > 0

    def test_register_from_directory_recursive(self):
        """Test registering scenarios recursively"""
        node_registry = NodeRegistry()
        node_registry.auto_discover()
        registry = ScenarioRegistry(node_registry)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            subdir = tmppath / "subdir"
            subdir.mkdir()

            test_scenario_content = '''
scenario:
  id: test_scenario
  name: Test Scenario
  description: Test scenario

steps:
  - node: "@common/get_files"
    name: get_files
'''
            (tmppath / "root_scenario.yaml").write_text(test_scenario_content)
            (subdir / "sub_scenario.yaml").write_text(test_scenario_content.replace("test_scenario", "sub_scenario"))

            registered = registry.register_from_directory(str(tmppath), recursive=True)
            assert len(registered) == 2

    def test_register_from_nonexistent_directory(self):
        """Test error handling for nonexistent directory"""
        node_registry = NodeRegistry()
        node_registry.auto_discover()
        registry = ScenarioRegistry(node_registry)

        with pytest.raises(FileNotFoundError):
            registry.register_from_directory("/nonexistent/directory")


class TestCLIIntegration:
    """Test CLI integration for registration commands"""

    def test_nodes_register_command_exists(self):
        """Test that nodes register command exists"""
        from cli import cli

        assert 'nodes' in cli.commands
        nodes_group = cli.commands['nodes']
        assert 'register' in nodes_group.commands

    def test_scenarios_register_action_exists(self):
        """Test that scenarios register action exists"""
        from cli import cli

        assert 'scenarios' in cli.commands


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
