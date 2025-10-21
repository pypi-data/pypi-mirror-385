"""
Unit tests for Scenario Registry (Phase 2)

Tests cover:
1. ScenarioLoader YAML parsing and validation
2. ScenarioLoader Flow construction
3. ScenarioRegistry auto-discovery
4. Scenario execution
5. Parameter merging and template rendering
6. CLI integration
"""

import pytest
import sys
from pathlib import Path
import tempfile
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core import node_registry, scenario_registry
from core.scenario_loader import ScenarioLoader
from core.scenario_registry import ScenarioRegistry


class TestScenarioLoader:
    """Test ScenarioLoader functionality"""

    def test_load_from_yaml_file(self):
        """Test loading scenario from YAML file"""
        # Use one of the template files
        templates_dir = project_root / "scenarios" / "templates"
        simple_rag_file = templates_dir / "simple_rag.yaml"

        loader = ScenarioLoader(node_registry)
        scenario_def = loader.load_from_yaml(simple_rag_file)

        assert 'scenario' in scenario_def
        assert scenario_def['scenario']['id'] == 'simple_rag'
        assert 'parameters' in scenario_def
        assert 'steps' in scenario_def

    def test_load_from_string(self):
        """Test loading scenario from YAML string"""
        yaml_content = """
scenario:
  id: test_scenario
  name: Test Scenario

parameters:
  test_param:
    type: str
    default: test_value

steps:
  - node: "@common/get_files"
    name: get_files
"""
        loader = ScenarioLoader(node_registry)
        scenario_def = loader.load_from_string(yaml_content)

        assert scenario_def['scenario']['id'] == 'test_scenario'
        assert 'test_param' in scenario_def['parameters']

    def test_validate_scenario_valid(self):
        """Test validation of valid scenario"""
        scenario_def = {
            'scenario': {
                'id': 'test',
                'name': 'Test'
            },
            'steps': [
                {'node': '@common/get_files', 'name': 'get_files'}
            ]
        }

        loader = ScenarioLoader(node_registry)
        errors = loader.validate_scenario(scenario_def)

        assert len(errors) == 0

    def test_validate_scenario_missing_id(self):
        """Test validation catches missing scenario ID"""
        scenario_def = {
            'scenario': {
                'name': 'Test'
            },
            'steps': []
        }

        loader = ScenarioLoader(node_registry)
        errors = loader.validate_scenario(scenario_def)

        assert len(errors) > 0
        assert any('id' in err for err in errors)

    def test_validate_scenario_missing_steps(self):
        """Test validation catches missing steps"""
        scenario_def = {
            'scenario': {
                'id': 'test',
                'name': 'Test'
            }
        }

        loader = ScenarioLoader(node_registry)
        errors = loader.validate_scenario(scenario_def)

        assert len(errors) > 0
        assert any('steps' in err for err in errors)

    def test_merge_parameters(self):
        """Test parameter merging with defaults"""
        loader = ScenarioLoader(node_registry)

        param_schema = {
            'param1': {'type': 'str', 'default': 'default1'},
            'param2': {'type': 'int', 'default': 42},
            'param3': {'type': 'str', 'required': True}
        }

        user_params = {
            'param1': 'custom1',
            'param3': 'required_value'
        }

        merged = loader._merge_parameters(param_schema, user_params)

        assert merged['param1'] == 'custom1'  # User value
        assert merged['param2'] == 42          # Default value
        assert merged['param3'] == 'required_value'  # Required value

    def test_merge_parameters_missing_required(self):
        """Test that missing required parameter raises error"""
        loader = ScenarioLoader(node_registry)

        param_schema = {
            'required_param': {'type': 'str', 'required': True}
        }

        user_params = {}

        with pytest.raises(ValueError, match="Required parameter missing"):
            loader._merge_parameters(param_schema, user_params)

    def test_render_params_simple(self):
        """Test simple parameter template rendering"""
        loader = ScenarioLoader(node_registry)

        params = {
            'model': '{{params.model_name}}',
            'static_value': 'static'
        }

        template_context = {
            'params': {'model_name': 'gpt-4'},
            'context': {}
        }

        rendered = loader._render_params(params, template_context)

        assert rendered['model'] == 'gpt-4'
        assert rendered['static_value'] == 'static'

    def test_create_flow(self):
        """Test creating a Flow from scenario definition"""
        # Auto-discover nodes first
        node_registry.auto_discover()

        loader = ScenarioLoader(node_registry)

        scenario_def = {
            'scenario': {'id': 'test'},
            'parameters': {
                'patterns': {'type': 'list', 'default': ['**/*.py']}
            },
            'steps': [
                {
                    'node': '@common/get_files',
                    'name': 'get_files',
                    'params': {
                        'patterns': '{{params.patterns}}'
                    }
                }
            ]
        }

        flow = loader.create_flow(scenario_def, {'patterns': ['*.txt']})

        # Check that flow was created
        assert flow is not None
        assert len(flow.nodes) == 1
        assert flow.nodes[0]['name'] == 'get_files'


class TestScenarioRegistry:
    """Test ScenarioRegistry functionality"""

    def test_auto_discover_templates(self):
        """Test auto-discovery of template scenarios"""
        registry = ScenarioRegistry(node_registry)
        templates_dir = project_root / "scenarios" / "templates"

        registry.auto_discover(additional_dirs=[str(templates_dir)])

        scenarios = registry.list_scenarios()
        assert len(scenarios) > 0

        # Check for known templates
        scenario_ids = [s['id'] for s in scenarios]
        assert 'simple_rag' in scenario_ids
        assert 'file_collector' in scenario_ids

    def test_list_scenarios(self):
        """Test listing scenarios with metadata"""
        registry = ScenarioRegistry(node_registry)
        templates_dir = project_root / "scenarios" / "templates"
        registry.auto_discover(additional_dirs=[str(templates_dir)])

        scenarios = registry.list_scenarios()

        # Check metadata structure
        for scenario in scenarios:
            assert 'id' in scenario
            assert 'name' in scenario
            assert 'description' in scenario
            assert 'version' in scenario
            assert 'source' in scenario

    def test_get_scenario(self):
        """Test getting a specific scenario"""
        registry = ScenarioRegistry(node_registry)
        templates_dir = project_root / "scenarios" / "templates"
        registry.auto_discover(additional_dirs=[str(templates_dir)])

        scenario_def = registry.get_scenario('simple_rag')

        assert scenario_def['scenario']['id'] == 'simple_rag'
        assert 'parameters' in scenario_def
        assert 'steps' in scenario_def

    def test_get_scenario_not_found(self):
        """Test getting non-existent scenario raises error"""
        registry = ScenarioRegistry(node_registry)

        with pytest.raises(ValueError, match="Scenario not found"):
            registry.get_scenario('nonexistent_scenario')

    def test_register_scenario_from_dict(self):
        """Test manual registration from dictionary"""
        registry = ScenarioRegistry(node_registry)

        scenario_def = {
            'scenario': {
                'id': 'test_manual',
                'name': 'Test Manual'
            },
            'steps': [
                {'node': '@common/get_files', 'name': 'get_files'}
            ]
        }

        registry.register_scenario_from_dict(scenario_def, 'test_manual')

        # Verify registration
        scenarios = registry.list_scenarios()
        scenario_ids = [s['id'] for s in scenarios]
        assert 'test_manual' in scenario_ids

    def test_register_scenario_from_yaml_file(self):
        """Test manual registration from YAML file"""
        registry = ScenarioRegistry(node_registry)

        # Create temporary YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
scenario:
  id: test_temp
  name: Test Temporary

steps:
  - node: "@common/get_files"
    name: get_files
""")
            temp_file = f.name

        try:
            registry.register_scenario_from_yaml(Path(temp_file))

            scenarios = registry.list_scenarios()
            scenario_ids = [s['id'] for s in scenarios]
            assert 'test_temp' in scenario_ids
        finally:
            os.unlink(temp_file)


class TestScenarioExecution:
    """Test actual scenario execution"""

    def test_run_file_collector_scenario(self):
        """Test running the file_collector scenario"""
        # Setup
        node_registry.auto_discover()
        registry = ScenarioRegistry(node_registry)
        templates_dir = project_root / "scenarios" / "templates"
        registry.auto_discover(additional_dirs=[str(templates_dir)])

        # Run scenario
        result = registry.run_scenario('file_collector', {
            'patterns': ['*.py'],
            'extensions': []
        })

        # Check results
        assert 'files' in result
        assert isinstance(result['files'], list)
        assert len(result['files']) > 0  # Should find at least some Python files

    def test_run_simple_rag_scenario_without_llm(self):
        """Test simple_rag scenario setup (without actual LLM call)"""
        # Setup
        node_registry.auto_discover()
        registry = ScenarioRegistry(node_registry)
        templates_dir = project_root / "scenarios" / "templates"
        registry.auto_discover(additional_dirs=[str(templates_dir)])

        # This test will fail at LLM call if API key not set,
        # but we can test that the flow is constructed correctly
        # by catching the expected error

        try:
            result = registry.run_scenario('simple_rag', {
                'patterns': ['test_*.py'],
                'query': 'What is this test file about?'
            })
            # If we get here, LLM call succeeded (API key is set)
            assert 'llm_response' in result or 'formatted_prompt' in result
        except Exception as e:
            # Expected if API key not set - that's OK for this test
            # We're just testing that the scenario flow is constructed
            error_msg = str(e).lower()
            assert 'api' in error_msg or 'key' in error_msg or 'llm' in error_msg


def test_cli_scenarios_integration():
    """Integration test for scenarios CLI commands"""
    from click.testing import CliRunner
    from cli import cli

    runner = CliRunner()

    # Test 'scenarios list'
    result = runner.invoke(cli, ['scenarios', 'list'])
    assert result.exit_code == 0
    assert 'simple_rag' in result.output
    assert 'Total:' in result.output

    # Test 'scenarios show'
    result = runner.invoke(cli, ['scenarios', 'show', 'file_collector'])
    assert result.exit_code == 0
    assert 'Parameters:' in result.output
    assert 'patterns' in result.output


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
