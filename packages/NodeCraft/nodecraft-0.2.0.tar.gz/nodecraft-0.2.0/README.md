# NodeCraft

A modular framework for building composable AI workflows with a "building blocks" design philosophy.

## Overview

NodeCraft provides a pluggable Node and Scenario system that allows you to discover, create, and compose reusable AI workflow components. Think of it as building blocks for AI-powered code analysis and automation.

## Key Features

- Node-based architecture with automatic discovery
- YAML-based scenario definition
- Template-based Node and Scenario creation
- Configuration file system for team collaboration
- Dynamic CLI generation from scenarios
- Built-in scenarios for common tasks

## Installation

```bash
# Install from PyPI
pip install NodeCraft

# Set up API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

After installation, the `nodecraft` command is available globally.

## Quick Start

### Discover Available Nodes and Scenarios

```bash
# List all available nodes
nodecraft nodes list

# Show node details
nodecraft nodes show @common/get_files

# List all scenarios
nodecraft scenarios list

# Show scenario details
nodecraft scenarios show simple_rag
```

### Create New Nodes and Scenarios

```bash
# Create a function-based node
nodecraft nodes create --name my_analyzer

# Create a class-based node with retry logic
nodecraft nodes create --name api_caller --type class

# Create a scenario from template
nodecraft scenarios create --name my_workflow --template rag-query

# View available templates
nodecraft scenarios create --name test --template custom --dry-run
```

### Register Custom Nodes and Scenarios

```bash
# Register a single node
nodecraft nodes register ./custom_nodes/my_node.py

# Register all nodes in a directory
nodecraft nodes register ./custom_nodes/ --recursive

# Register a scenario
nodecraft scenarios register ./my_scenario.yaml
```

## Configuration

Create a `.nodecraft.yaml` file in your project root:

```yaml
nodes:
  search_paths:
    - ".nodecraft/nodes"
    - "./custom_nodes"

scenarios:
  search_paths:
    - ".nodecraft/scenarios"
    - "./workflows"

llm:
  default_model: "claude-3-haiku-20240307"
  api_timeout: 60
```

Configuration priority: CLI arguments > Project config > Global config > Defaults

Global config location: `~/.nodecraft/config.yaml`

## Built-in Scenarios

OutcomeForge includes several built-in scenarios for common tasks:

- **snapshot**: Create snapshots of your codebase with AI analysis
- **adapt**: Analyze open-source repositories and generate adaptation plans
- **regression**: AI-powered quality gate based on test metrics
- **arch-drift**: Detect architecture violations and structural drift
- **rag**: Lightweight RAG for codebase Q&A
- **code-review**: Security, quality, and performance code review
- **wiki**: Generate structured wiki documentation from codebases

Example usage:

```bash
# Create a snapshot
nodecraft snapshot --patterns "**/*.py"

# Ask questions about your codebase
nodecraft rag --patterns "**/*.py" --query "How does this work?"

# Review code changes
nodecraft code-review --git-diff

# Generate wiki documentation
nodecraft wiki --local-dir ./my-project
```

## CLI Usage

### Node Management

```bash
# List nodes
nodecraft nodes list [--namespace <namespace>]

# Show node details
nodecraft nodes show <node_id>

# Create new node from template
nodecraft nodes create --name <name> [--type function|class]

# Register custom node
nodecraft nodes register <path> [--recursive]
```

### Scenario Management

```bash
# List scenarios
nodecraft scenarios list

# Show scenario details
nodecraft scenarios show <scenario_id>

# Create new scenario from template
nodecraft scenarios create --name <name> --template <template>

# Register custom scenario
nodecraft scenarios register <path> [--recursive]

# Run a scenario
nodecraft <scenario_id> [OPTIONS]
```

Available scenario templates:
- `rag-query`: RAG-based codebase Q&A
- `file-process`: File collection and processing
- `analyze-report`: Code analysis with report generation
- `gate-check`: Quality gate enforcement
- `snapshot-restore`: Version control and rollback
- `custom`: Blank template for custom workflows

### Tutorial System

```bash
# Get started tutorial
nodecraft tutorial

# Node creation tutorial
nodecraft tutorial nodes

# Scenario tutorial
nodecraft tutorial scenarios
```

## Architecture

### Node System

Nodes are the smallest units of work. Each node has three phases:

1. **prep**: Validate inputs and prepare parameters
2. **exec**: Execute the main operation
3. **post**: Process results and update context

Nodes are discovered automatically from:
- Framework built-in nodes (`nodes/common/`)
- Global user nodes (`~/.nodecraft/nodes/`)
- Project nodes (`.nodecraft/nodes/`)
- Configured search paths

### Scenario System

Scenarios are workflows composed of nodes. They can be defined in:

1. **Python** (programmatic):
```python
from engine import flow
from nodes.common import get_files_node, call_llm_node

def my_scenario(config):
    f = flow()
    f.add(get_files_node(), name="get_files")
    f.add(call_llm_node(), name="analyze")
    return f
```

2. **YAML** (declarative):
```yaml
scenario:
  id: my_scenario
  name: My Scenario
  description: Custom workflow

parameters:
  patterns:
    type: list
    default: ["**/*.py"]

steps:
  - node: "@common/get_files"
    name: get_files
    params:
      patterns: "{{params.patterns}}"

  - node: "@common/call_llm"
    name: analyze
```

### Context Flow

Data flows through the scenario via a shared context dictionary. Each node:
- Reads data from context using `input_keys`
- Writes results to context using `output_keys`
- Can access parameters via `{{params.name}}` syntax in YAML

## Development

### Project Structure

```
nodecraft/
├── core/                    # Core framework
│   ├── registry.py         # Node discovery and registration
│   ├── scenario_registry.py # Scenario management
│   ├── template_generator.py # Template generation
│   └── config.py           # Configuration management
├── nodes/
│   └── common/             # Built-in nodes
├── scenarios/              # Built-in scenarios
├── templates/              # Node and scenario templates
│   ├── nodes/
│   └── scenarios/
└── cli.py                  # CLI entry point
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_template_creation.py -v
```

## Requirements

- Python 3.7+
- anthropic (Claude API)
- openai (OpenAI API)
- click (CLI framework)
- pyyaml (YAML parsing)
- gitpython (Git operations)
- jinja2 (Template rendering)

## License

MIT
