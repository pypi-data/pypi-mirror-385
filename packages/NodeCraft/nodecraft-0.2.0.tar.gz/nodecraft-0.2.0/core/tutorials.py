"""
Tutorial System - Interactive guides for OutcomeForge

Provides step-by-step tutorials for:
- Creating custom nodes
- Defining YAML scenarios
- Using the registry system
"""


def show_getting_started():
    """Show comprehensive getting started guide"""
    return """
================================================================================
                     OutcomeForge - Getting Started Guide
================================================================================

OutcomeForge uses a "Building Blocks" architecture where you compose Nodes
into Scenarios to create intelligent workflows.

Quick Links:
  [1] Create Your First Custom Node (30 seconds)
  [2] Create Your First YAML Scenario (2 minutes)
  [3] Understanding the Registry System
  [4] Advanced Topics

Choose a number or press Ctrl+C to exit.

================================================================================
""".strip()


def show_node_tutorial():
    """Tutorial for creating custom nodes"""
    return """
================================================================================
                   Tutorial: Create Your First Custom Node
================================================================================

A Node is the smallest building block in OutcomeForge. Each node performs a
single, well-defined task.

STEP 1: Create the directory
----------------------------
mkdir -p ~/.outcomeforge/nodes

STEP 2: Create your node file
----------------------------
Create file: ~/.outcomeforge/nodes/hello_node.py

'''python
from engine import node

def hello_node():
    '''Say hello to someone'''

    # Metadata declaration
    metadata = {
        "id": "hello",
        "namespace": "custom",
        "description": "Print a hello message",
        "params_schema": {
            "name": {
                "type": "str",
                "default": "World",
                "description": "Name to greet"
            }
        },
        "input_keys": [],
        "output_keys": ["message"]
    }

    def prep(ctx, params):
        # Extract parameters
        return {"name": params.get("name", "World")}

    def exec(prep_result, params):
        # Main logic
        name = prep_result["name"]
        return f"Hello, {name}!"

    def post(ctx, prep_result, exec_result, params):
        # Update context and return next action
        ctx["message"] = exec_result
        print(exec_result)
        return "default"

    node_func = node(prep=prep, exec=exec, post=post)
    node_func["metadata"] = metadata
    return node_func
'''

STEP 3: Verify your node
----------------------------
outcomeforge nodes list --namespace custom

You should see:
  @custom/hello    custom    Print a hello message

STEP 4: View node details
----------------------------
outcomeforge nodes show @custom/hello

STEP 5: Use in a scenario
----------------------------
Create a YAML scenario that uses your custom node:

'''yaml
scenario:
  id: test_hello
  name: Test Hello Node

steps:
  - node: "@custom/hello"
    name: greet
    params:
      name: "Alice"
'''

================================================================================
                            Next Steps
================================================================================

- Create more complex nodes with multiple inputs/outputs
- Use class-based nodes (inherit from Node, AsyncNode, etc.)
- Add error handling in exec_fallback
- Explore batch processing with BatchNode

View class-based node tutorial:
  outcomeforge --tutorial node-class

================================================================================
""".strip()


def show_node_class_tutorial():
    """Tutorial for class-based nodes"""
    return """
================================================================================
                Tutorial: Create a Class-Based Custom Node
================================================================================

Class-based nodes offer more structure and features like retry logic.

EXAMPLE: Create a file analyzer node
----------------------------
Create file: ~/.outcomeforge/nodes/file_analyzer.py

'''python
from engine import Node
from pathlib import Path

class FileAnalyzer(Node):
    '''Analyze file statistics'''

    # Metadata as class attributes
    id = "file_analyzer"
    namespace = "custom"
    description = "Analyze file size, lines, and complexity"

    params_schema = {
        "file_path": {
            "type": "str",
            "required": True,
            "description": "Path to file to analyze"
        }
    }

    input_keys = []
    output_keys = ["file_stats"]

    def __init__(self):
        # Enable retry with 3 attempts, 1 second wait
        super().__init__(max_retries=3, wait=1)

    def prep(self, shared):
        # Get file path from parameters
        file_path = self.params.get("file_path")
        return {"file_path": Path(file_path)}

    def exec(self, prep_res):
        # Analyze file
        file_path = prep_res["file_path"]

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\\n')

        return {
            "size": file_path.stat().st_size,
            "lines": len(lines),
            "chars": len(content),
            "avg_line_length": len(content) / len(lines) if lines else 0
        }

    def exec_fallback(self, prep_res, exc):
        # Fallback when all retries fail
        return {
            "error": str(exc),
            "size": 0,
            "lines": 0,
            "chars": 0,
            "avg_line_length": 0
        }

    def post(self, shared, prep_res, exec_res):
        shared["file_stats"] = exec_res
        return "default"
'''

KEY BENEFITS OF CLASS-BASED NODES:
- Built-in retry mechanism
- Cleaner organization
- Easier to test
- Fallback handling
- Better IDE support

================================================================================
""".strip()


def show_scenario_tutorial():
    """Tutorial for creating YAML scenarios"""
    return """
================================================================================
                Tutorial: Create Your First YAML Scenario
================================================================================

Scenarios combine multiple nodes into a workflow. With YAML, you can define
scenarios without writing Python code.

STEP 1: Create the directory
----------------------------
mkdir -p ~/.outcomeforge/scenarios

STEP 2: Create your scenario file
----------------------------
Create file: ~/.outcomeforge/scenarios/my_first_scenario.yaml

'''yaml
scenario:
  id: my_first_scenario
  name: My First Scenario
  description: A simple scenario to get started
  author: Your Name
  version: 1.0.0

# Parameters that users can customize
parameters:
  patterns:
    type: list
    default: ["**/*.py"]
    description: File patterns to analyze

  model:
    type: str
    default: claude-3-haiku-20240307
    description: LLM model to use

# Workflow steps
steps:
  # Step 1: Collect files
  - node: "@common/get_files"
    name: get_files
    params:
      patterns: "{{params.patterns}}"
      exclude: ["node_modules/**", ".git/**"]

  # Step 2: Format for LLM
  - node: "@common/files_to_prompt"
    name: format_context
    params:
      format: xml
      cxml: true

  # Step 3: Call LLM
  - node: "@common/call_llm"
    name: analyze
    params:
      prompt_template: |
        Analyze the following codebase:

        {formatted_prompt}

        Provide:
        1. Overview of the project structure
        2. Key components
        3. Suggestions for improvement
      model: "{{params.model}}"
      temperature: 0.3
'''

STEP 3: Test your scenario
----------------------------
# List scenarios to verify it's registered
outcomeforge scenarios list

# View details
outcomeforge scenarios show my_first_scenario

# Run it
outcomeforge scenarios run my_first_scenario --params '{"patterns": ["*.py"]}'

================================================================================
                         Template Rendering
================================================================================

Use {{params.xxx}} to reference parameters:
  patterns: "{{params.patterns}}"

Use {xxx} to reference context values:
  prompt_template: "{formatted_prompt}"

================================================================================
                         Conditional Steps
================================================================================

Add conditions to steps:

'''yaml
steps:
  - node: "@common/write_file"
    name: save_report
    condition: params.output_file is not None
    params:
      file_path: "{{params.output_file}}"
'''

Condition expressions support:
- params.xxx - Parameter values
- context.xxx - Context values
- Comparisons: >, <, ==, !=, is None, is not None
- Boolean: and, or, not

================================================================================
                            Next Steps
================================================================================

- Add multiple steps to create complex workflows
- Use conditional execution
- Create scenario templates for common patterns
- Share scenarios with your team

View advanced scenario topics:
  outcomeforge --tutorial scenario-advanced

================================================================================
""".strip()


def show_registry_tutorial():
    """Tutorial for understanding the registry system"""
    return """
================================================================================
                   Tutorial: Understanding the Registry System
================================================================================

OutcomeForge uses registries to discover and manage nodes and scenarios.

DIRECTORY STRUCTURE
-------------------

Global (User-level):
  ~/.outcomeforge/
  ├── nodes/           # Your custom nodes
  │   └── my_node.py
  └── scenarios/       # Your custom scenarios
      └── my_scenario.yaml

Project-level:
  your-project/
  ├── .outcomeforge/
  │   ├── nodes/       # Project-specific nodes
  │   └── scenarios/   # Project-specific scenarios
  └── (your project files)

Framework built-in:
  outcomeforge/
  └── nodes/
      └── common/      # Built-in nodes

NAMESPACES
----------

Nodes use namespaces to avoid conflicts:

@common/*     - Framework built-in nodes
@custom/*     - User-defined nodes
@community/*  - Community-contributed nodes

Example:
  @common/get_files
  @custom/my_analyzer
  @community/python_linter

DISCOVERY PROCESS
-----------------

When you run 'outcomeforge nodes list':

1. Scans framework built-in nodes (nodes/common/)
2. Scans global user nodes (~/.outcomeforge/nodes/)
3. Scans project nodes (.outcomeforge/nodes/)
4. Registers all found nodes with metadata

When you run 'outcomeforge scenarios list':

1. Scans template scenarios (scenarios/templates/)
2. Scans global user scenarios (~/.outcomeforge/scenarios/)
3. Scans project scenarios (.outcomeforge/scenarios/)
4. Validates and registers all YAML files

METADATA
--------

Nodes declare metadata to enable discovery:

'''python
metadata = {
    "id": "my_node",              # Unique identifier
    "namespace": "custom",         # Namespace
    "description": "...",          # Human-readable description
    "params_schema": {...},        # Parameter definitions
    "input_keys": [...],           # Context keys read
    "output_keys": [...]           # Context keys written
}
'''

This metadata powers:
- 'nodes list' command
- 'nodes show' detailed view
- Parameter validation
- Auto-generated documentation

PRIORITY RULES
--------------

When multiple items have the same ID:
- Project-level overrides global
- Global overrides built-in

This allows you to customize built-in nodes/scenarios per project.

================================================================================
""".strip()


def show_advanced_scenario_tutorial():
    """Advanced scenario patterns"""
    return """
================================================================================
              Tutorial: Advanced Scenario Patterns
================================================================================

PATTERN 1: Multi-stage Pipeline
--------------------------------

'''yaml
scenario:
  id: advanced_pipeline
  name: Advanced Multi-Stage Pipeline

parameters:
  stages:
    type: list
    default: ["collect", "analyze", "report"]

steps:
  # Stage 1: Data Collection
  - node: "@common/get_files"
    name: collect_files

  - node: "@custom/extract_metadata"
    name: extract_metadata

  # Stage 2: Analysis
  - node: "@custom/static_analysis"
    name: analyze_code

  - node: "@common/call_llm"
    name: ai_analysis

  # Stage 3: Reporting
  - node: "@custom/generate_charts"
    name: create_visualizations
    condition: "generate_charts" in params.stages

  - node: "@common/write_file"
    name: save_report
'''

PATTERN 2: Error Handling
--------------------------

'''yaml
scenario:
  id: robust_scenario
  name: Scenario with Error Handling

steps:
  - node: "@custom/risky_operation"
    name: try_operation

  # Fallback if previous step fails
  - node: "@custom/fallback_operation"
    name: fallback
    condition: context.error is not None

  # Always run cleanup
  - node: "@custom/cleanup"
    name: cleanup
'''

PATTERN 3: Dynamic Parameters
------------------------------

'''yaml
scenario:
  id: dynamic_params
  name: Dynamic Parameter Scenario

parameters:
  env:
    type: str
    default: dev
    choices: [dev, staging, prod]

steps:
  - node: "@common/call_llm"
    name: analyze
    params:
      # Different models per environment
      model: |
        {% if params.env == "prod" %}
        gpt-4
        {% else %}
        gpt-3.5-turbo
        {% endif %}
'''

PATTERN 4: Batch Processing
----------------------------

'''yaml
scenario:
  id: batch_processor
  name: Process Multiple Items

parameters:
  items:
    type: list
    required: true

steps:
  # Process each item
  - node: "@custom/batch_processor"
    name: process_all
    params:
      items: "{{params.items}}"
'''

PATTERN 5: Snapshot-Restore
----------------------------

'''yaml
scenario:
  id: safe_transformation
  name: Safe Code Transformation

steps:
  # Create snapshot before changes
  - node: "@common/snapshot_files"
    name: create_snapshot

  # Perform risky transformation
  - node: "@custom/transform_code"
    name: transform

  # Validate results
  - node: "@custom/validate_changes"
    name: validate

  # Restore if validation fails
  - node: "@custom/restore_snapshot"
    name: restore
    condition: context.validation_failed
'''

================================================================================
                          Best Practices
================================================================================

1. Single Responsibility
   - Each node does one thing well
   - Compose simple nodes into complex workflows

2. Descriptive Naming
   - Use clear step names: "validate_input" not "step1"
   - Use meaningful parameter names

3. Error Handling
   - Add conditions for error cases
   - Provide fallback steps
   - Always include cleanup steps

4. Documentation
   - Add descriptions to all parameters
   - Document expected context keys
   - Provide usage examples

5. Testing
   - Test scenarios with different parameters
   - Validate conditional branches
   - Check error handling paths

================================================================================
""".strip()


TUTORIALS = {
    "main": show_getting_started,
    "node": show_node_tutorial,
    "node-class": show_node_class_tutorial,
    "scenario": show_scenario_tutorial,
    "registry": show_registry_tutorial,
    "scenario-advanced": show_advanced_scenario_tutorial,
}


def get_tutorial(name="main"):
    """Get tutorial by name

    Args:
        name: Tutorial name (main, node, scenario, registry, etc.)

    Returns:
        Tutorial text
    """
    tutorial_func = TUTORIALS.get(name, show_getting_started)
    return tutorial_func()


def list_tutorials():
    """List all available tutorials"""
    return """
Available Tutorials:

  main              - Getting Started Guide (default)
  node              - Create Your First Custom Node
  node-class        - Create Class-Based Nodes
  scenario          - Create Your First YAML Scenario
  scenario-advanced - Advanced Scenario Patterns
  registry          - Understanding the Registry System

Usage:
  outcomeforge --tutorial              # Show getting started
  outcomeforge --tutorial node         # Show node tutorial
  outcomeforge --tutorial scenario     # Show scenario tutorial
""".strip()
