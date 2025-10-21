"""
Tests for Configuration System (Phase 1.3)

Tests the configuration loading and merging functionality.
"""

import pytest
import sys
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import ConfigManager


class TestConfigManager:
    """Test ConfigManager functionality"""

    def test_default_config(self):
        """Test loading default configuration"""
        config = ConfigManager()
        result = config.load()

        assert 'nodes' in result
        assert 'scenarios' in result
        assert 'llm' in result
        assert 'output' in result

        assert result['llm']['default_model'] == 'claude-3-haiku-20240307'
        assert result['output']['format'] == 'yaml'

    def test_load_global_config(self):
        """Test loading global configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            global_config_path = tmppath / ".outcomeforge" / "config.yaml"
            global_config_path.parent.mkdir(parents=True)
            global_config_path.write_text('''
nodes:
  search_paths:
    - "/custom/nodes"

llm:
  default_model: "gpt-4"
''')

            # Mock Path.home() to return tmppath
            import core.config
            original_home = Path.home
            Path.home = lambda: tmppath

            try:
                config = ConfigManager()
                result = config.load()

                assert result['llm']['default_model'] == 'gpt-4'
                assert '/custom/nodes' in result['nodes']['search_paths']
            finally:
                Path.home = original_home

    def test_load_project_config(self):
        """Test loading project configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            project_config_path = tmppath / ".outcomeforge.yaml"
            project_config_path.write_text('''
nodes:
  search_paths:
    - "./project_nodes"

scenarios:
  search_paths:
    - "./workflows"
''')

            config = ConfigManager(project_dir=tmppath)
            result = config.load()

            assert './project_nodes' in result['nodes']['search_paths']
            assert './workflows' in result['scenarios']['search_paths']

    def test_config_merge_priority(self):
        """Test configuration merge priority: CLI > Project > Global > Default"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            global_config_path = tmppath / ".outcomeforge" / "config.yaml"
            global_config_path.parent.mkdir(parents=True)
            global_config_path.write_text('''
llm:
  default_model: "global-model"
  api_timeout: 90
''')

            project_config_path = tmppath / ".outcomeforge.yaml"
            project_config_path.write_text('''
llm:
  default_model: "project-model"
''')

            import core.config
            original_home = Path.home
            Path.home = lambda: tmppath

            try:
                config = ConfigManager(project_dir=tmppath)

                cli_overrides = {
                    'llm': {
                        'default_model': 'cli-model'
                    }
                }

                result = config.load(cli_overrides=cli_overrides)

                assert result['llm']['default_model'] == 'cli-model'
                assert result['llm']['api_timeout'] == 90
            finally:
                Path.home = original_home

    def test_get_method(self):
        """Test get method with dotted path"""
        config = ConfigManager()
        config.load()

        assert config.get('llm', 'default_model') == 'claude-3-haiku-20240307'
        assert config.get('output', 'format') == 'yaml'
        assert config.get('nonexistent', 'key', default='default_value') == 'default_value'

    def test_get_node_search_paths(self):
        """Test getting node search paths"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            project_config_path = tmppath / ".outcomeforge.yaml"
            project_config_path.write_text('''
nodes:
  search_paths:
    - "./custom_nodes"
    - "~/global_nodes"
''')

            config = ConfigManager(project_dir=tmppath)
            config.load()

            paths = config.get_node_search_paths()
            assert len(paths) == 2
            assert all(isinstance(p, Path) for p in paths)

    def test_get_scenario_search_paths(self):
        """Test getting scenario search paths"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            project_config_path = tmppath / ".outcomeforge.yaml"
            project_config_path.write_text('''
scenarios:
  search_paths:
    - "./workflows"
    - "./scenarios"
''')

            config = ConfigManager(project_dir=tmppath)
            config.load()

            paths = config.get_scenario_search_paths()
            assert len(paths) == 2
            assert all(isinstance(p, Path) for p in paths)

    def test_list_merge(self):
        """Test that lists are extended, not replaced"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            global_config_path = tmppath / ".outcomeforge" / "config.yaml"
            global_config_path.parent.mkdir(parents=True)
            global_config_path.write_text('''
nodes:
  search_paths:
    - "/global/path"
''')

            project_config_path = tmppath / ".outcomeforge.yaml"
            project_config_path.write_text('''
nodes:
  search_paths:
    - "/project/path"
''')

            import core.config
            original_home = Path.home
            Path.home = lambda: tmppath

            try:
                config = ConfigManager(project_dir=tmppath)
                result = config.load()

                paths = result['nodes']['search_paths']
                assert '/global/path' in paths
                assert '/project/path' in paths
            finally:
                Path.home = original_home

    def test_invalid_yaml(self):
        """Test handling of invalid YAML"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            project_config_path = tmppath / ".outcomeforge.yaml"
            project_config_path.write_text('''
invalid: yaml: syntax
    bad: indentation
''')

            config = ConfigManager(project_dir=tmppath)
            result = config.load()

            assert result['llm']['default_model'] == 'claude-3-haiku-20240307'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
