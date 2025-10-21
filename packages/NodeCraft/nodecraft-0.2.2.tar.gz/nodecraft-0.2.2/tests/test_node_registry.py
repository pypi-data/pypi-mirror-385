"""
Unit tests for Node Registry (Phase 1)

Tests cover:
1. NodeRegistry auto-discovery
2. Node loading from files
3. Node metadata extraction
4. get_node() functionality
5. list_nodes() filtering
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.registry import NodeRegistry


class TestNodeRegistry:
    """Test NodeRegistry core functionality"""

    def test_auto_discover_finds_nodes(self):
        """Test that auto_discover finds nodes from common directory"""
        registry = NodeRegistry()
        registry.auto_discover()

        nodes = registry.list_nodes()
        assert len(nodes) > 0, "Should discover at least some nodes"

        # Check for known nodes
        node_ids = [n['full_id'] for n in nodes]
        assert '@common/get_files' in node_ids, "Should find get_files node"
        assert '@common/call_llm' in node_ids, "Should find call_llm node"

    def test_list_nodes_namespace_filter(self):
        """Test filtering nodes by namespace"""
        registry = NodeRegistry()
        registry.auto_discover()

        # Filter by common namespace
        common_nodes = registry.list_nodes(namespace='common')
        assert all(n['namespace'] == 'common' for n in common_nodes)

        # Custom namespace (may be empty)
        custom_nodes = registry.list_nodes(namespace='custom')
        assert all(n['namespace'] == 'custom' for n in custom_nodes)

    def test_get_node_returns_valid_instance(self):
        """Test that get_node returns a valid node instance"""
        registry = NodeRegistry()
        registry.auto_discover()

        # Get a known node
        node_instance = registry.get_node('@common/get_files')

        # For function-based nodes, it should be a dict with prep, exec, post
        assert isinstance(node_instance, dict)
        assert 'prep' in node_instance
        assert 'exec' in node_instance
        assert 'post' in node_instance

    def test_get_node_with_invalid_id_raises_error(self):
        """Test that get_node raises ValueError for invalid node ID"""
        registry = NodeRegistry()
        registry.auto_discover()

        with pytest.raises(ValueError, match="Node not found"):
            registry.get_node('@nonexistent/node')

    def test_node_metadata_extraction(self):
        """Test that node metadata is correctly extracted"""
        registry = NodeRegistry()
        registry.auto_discover()

        nodes = registry.list_nodes()
        get_files_node = next(n for n in nodes if n['full_id'] == '@common/get_files')

        # Check metadata fields
        assert get_files_node['id'] == 'get_files'
        assert get_files_node['namespace'] == 'common'
        assert 'description' in get_files_node
        assert 'params_schema' in get_files_node
        assert 'input_keys' in get_files_node
        assert 'output_keys' in get_files_node

        # Check specific metadata values
        assert 'patterns' in get_files_node['params_schema']
        assert 'files' in get_files_node['output_keys']

    def test_node_params_schema_structure(self):
        """Test that params_schema has correct structure"""
        registry = NodeRegistry()
        registry.auto_discover()

        nodes = registry.list_nodes()
        call_llm_node = next(n for n in nodes if n['full_id'] == '@common/call_llm')

        params = call_llm_node['params_schema']
        assert 'model' in params
        assert params['model']['type'] == 'str'
        assert 'default' in params['model']
        assert 'description' in params['model']

    def test_manual_registration(self):
        """Test manual node registration"""
        registry = NodeRegistry()

        def my_test_node():
            """A test node"""
            from engine import node

            def prep(ctx, params):
                return {}

            def exec(prep_result, params):
                return "test"

            def post(ctx, prep_result, exec_result, params):
                ctx["test_output"] = exec_result
                return "default"

            return node(prep=prep, exec=exec, post=post)

        # Register manually
        registry.register_function_node_manually(
            my_test_node,
            "my_test",
            namespace="test",
            metadata={"description": "A test node"}
        )

        # Verify registration
        nodes = registry.list_nodes(namespace="test")
        assert len(nodes) == 1
        assert nodes[0]['id'] == 'my_test'

        # Verify can get node
        node_instance = registry.get_node('@test/my_test')
        assert node_instance is not None


class TestNodeExecution:
    """Test that discovered nodes can actually be executed"""

    def test_get_files_node_execution(self):
        """Test that get_files node can be executed"""
        registry = NodeRegistry()
        registry.auto_discover()

        node_instance = registry.get_node('@common/get_files')

        # Create a minimal context
        ctx = {"project_root": str(Path.cwd())}
        params = {"patterns": ["*.py"], "exclude": []}

        # Execute node phases
        prep_result = node_instance['prep'](ctx, params)
        assert 'patterns' in prep_result

        exec_result = node_instance['exec'](prep_result, params)
        assert isinstance(exec_result, list)

        post_result = node_instance['post'](ctx, prep_result, exec_result, params)
        assert 'files' in ctx
        assert isinstance(ctx['files'], list)

    def test_files_to_prompt_node_execution(self):
        """Test that files_to_prompt node can be executed"""
        registry = NodeRegistry()
        registry.auto_discover()

        node_instance = registry.get_node('@common/files_to_prompt')

        # Create test context with some files
        test_file = Path(__file__)
        ctx = {"files": [str(test_file)]}
        params = {"format": "xml", "cxml": False}

        # Execute
        prep_result = node_instance['prep'](ctx, params)
        exec_result = node_instance['exec'](prep_result, params)
        post_result = node_instance['post'](ctx, prep_result, exec_result, params)

        # Check results
        assert exec_result['success'] is True
        assert 'formatted_text' in exec_result
        assert '<document>' in exec_result['formatted_text']
        assert 'formatted_prompt' in ctx


def test_cli_integration():
    """Integration test for CLI commands"""
    from click.testing import CliRunner
    from cli import cli

    runner = CliRunner()

    # Test 'nodes list'
    result = runner.invoke(cli, ['nodes', 'list'])
    assert result.exit_code == 0
    assert '@common/get_files' in result.output
    assert 'Total:' in result.output

    # Test 'nodes show'
    result = runner.invoke(cli, ['nodes', 'show', '@common/get_files'])
    assert result.exit_code == 0
    assert 'Parameters:' in result.output
    assert 'patterns' in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
