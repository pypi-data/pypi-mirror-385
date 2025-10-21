"""
Tests for Template Creation (Phase 4.2 and 4.1)

Tests the Node and Scenario template generation functionality.
"""

import pytest
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.template_generator import NodeTemplateGenerator, ScenarioTemplateGenerator


class TestNodeTemplateGenerator:
    """Test Node template generation"""

    def test_generator_initialization(self):
        """Test NodeTemplateGenerator can be initialized"""
        generator = NodeTemplateGenerator()
        assert generator is not None
        assert generator.TEMPLATE_DIR.exists()

    def test_list_templates(self):
        """Test listing available node templates"""
        generator = NodeTemplateGenerator()
        templates = generator.list_templates()

        assert isinstance(templates, dict)
        assert 'function' in templates
        assert 'class' in templates
        assert len(templates) == 2

    def test_generate_function_node(self):
        """Test generating function-based node"""
        generator = NodeTemplateGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = generator.generate(
                name="test_func_node",
                namespace="custom",
                node_type="function",
                description="Test function node",
                output_dir=tmpdir
            )

            assert Path(output).exists()
            content = Path(output).read_text()

            # Verify key elements
            assert "def test_func_node_node():" in content
            assert '"id": "test_func_node"' in content
            assert '"namespace": "custom"' in content
            assert '"description": "Test function node"' in content
            assert "def prep(params, context):" in content
            assert "def exec(params, context):" in content
            assert "def post(params, context):" in content

    def test_generate_class_node(self):
        """Test generating class-based node"""
        generator = NodeTemplateGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = generator.generate(
                name="test_class_node",
                namespace="custom",
                node_type="class",
                description="Test class node",
                output_dir=tmpdir
            )

            assert Path(output).exists()
            content = Path(output).read_text()

            # Verify key elements
            assert "class TestClassNode(Node):" in content
            assert '"id": "test_class_node"' in content
            assert "def __init__(self, max_retries=3" in content
            assert "def _process(self, params, context):" in content

    def test_prevent_overwrite(self):
        """Test that generator prevents overwriting existing files"""
        generator = NodeTemplateGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first file
            output1 = generator.generate(
                name="duplicate_node",
                namespace="custom",
                node_type="function",
                description="First",
                output_dir=tmpdir
            )
            assert Path(output1).exists()

            # Try to create same file again
            with pytest.raises(FileExistsError):
                generator.generate(
                    name="duplicate_node",
                    namespace="custom",
                    node_type="function",
                    description="Second",
                    output_dir=tmpdir
                )

    def test_invalid_node_type(self):
        """Test error handling for invalid node type"""
        generator = NodeTemplateGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Unknown node type"):
                generator.generate(
                    name="test_node",
                    namespace="custom",
                    node_type="invalid_type",
                    description="Test",
                    output_dir=tmpdir
                )


class TestScenarioTemplateGenerator:
    """Test Scenario template generation"""

    def test_generator_initialization(self):
        """Test ScenarioTemplateGenerator can be initialized"""
        generator = ScenarioTemplateGenerator()
        assert generator is not None
        assert generator.TEMPLATE_DIR.exists()

    def test_list_templates(self):
        """Test listing available scenario templates"""
        generator = ScenarioTemplateGenerator()
        templates = generator.list_templates()

        assert isinstance(templates, dict)
        assert 'rag-query' in templates
        assert 'file-process' in templates
        assert 'analyze-report' in templates
        assert 'gate-check' in templates
        assert 'snapshot-restore' in templates
        assert 'custom' in templates
        assert len(templates) == 6

    def test_generate_rag_query_scenario(self):
        """Test generating RAG query scenario"""
        generator = ScenarioTemplateGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = generator.generate(
                name="test_rag",
                template="rag-query",
                description="Test RAG scenario",
                output_dir=tmpdir
            )

            assert Path(output).exists()
            content = Path(output).read_text()

            # Verify key elements
            assert "id: test_rag" in content
            assert "name: Test Rag" in content
            assert "description: Test RAG scenario" in content
            assert "@common/get_files" in content
            assert "@common/files_to_prompt" in content
            assert "@common/call_llm" in content

    def test_generate_custom_scenario(self):
        """Test generating custom blank scenario"""
        generator = ScenarioTemplateGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            output = generator.generate(
                name="my_workflow",
                template="custom",
                description="Custom workflow",
                output_dir=tmpdir
            )

            assert Path(output).exists()
            content = Path(output).read_text()

            # Verify structure
            assert "id: my_workflow" in content
            assert "name: My Workflow" in content
            assert "# TODO: Define your parameters" in content
            assert "# TODO: Add your workflow steps" in content

            # Verify parameter binding examples are preserved
            assert "{{params.param_name}}" in content
            assert "{{step_name.output_key}}" in content

    def test_generate_all_templates(self):
        """Test generating all available templates"""
        generator = ScenarioTemplateGenerator()
        templates = ['rag-query', 'file-process', 'analyze-report',
                    'gate-check', 'snapshot-restore', 'custom']

        with tempfile.TemporaryDirectory() as tmpdir:
            for template in templates:
                output = generator.generate(
                    name=f"test_{template.replace('-', '_')}",
                    template=template,
                    description=f"Test {template}",
                    output_dir=tmpdir
                )

                assert Path(output).exists()
                content = Path(output).read_text()
                assert "scenario:" in content
                assert "steps:" in content

    def test_prevent_overwrite(self):
        """Test that generator prevents overwriting existing files"""
        generator = ScenarioTemplateGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first file
            output1 = generator.generate(
                name="duplicate_scenario",
                template="custom",
                description="First",
                output_dir=tmpdir
            )
            assert Path(output1).exists()

            # Try to create same file again
            with pytest.raises(FileExistsError):
                generator.generate(
                    name="duplicate_scenario",
                    template="custom",
                    description="Second",
                    output_dir=tmpdir
                )

    def test_invalid_template(self):
        """Test error handling for invalid template"""
        generator = ScenarioTemplateGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Unknown template"):
                generator.generate(
                    name="test_scenario",
                    template="invalid_template",
                    description="Test",
                    output_dir=tmpdir
                )


class TestCLIIntegration:
    """Test CLI integration for template creation commands"""

    def test_nodes_create_command_exists(self):
        """Test that nodes create command exists"""
        from cli import cli

        # Check if nodes group exists
        assert 'nodes' in cli.commands
        nodes_group = cli.commands['nodes']

        # Check if create command exists in nodes group
        assert 'create' in nodes_group.commands

    def test_scenarios_create_action_exists(self):
        """Test that scenarios create action exists"""
        from cli import cli

        # Check if scenarios command exists
        assert 'scenarios' in cli.commands


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
