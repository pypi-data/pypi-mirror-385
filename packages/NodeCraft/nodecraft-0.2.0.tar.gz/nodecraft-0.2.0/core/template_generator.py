"""
Template Generator for Nodes and Scenarios

Generates code templates to help users create custom nodes and scenarios quickly.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from jinja2 import Environment, FileSystemLoader, Template
except ImportError:
    raise ImportError(
        "jinja2 is required for template generation. "
        "Install with: pip install jinja2"
    )


class NodeTemplateGenerator:
    """Generate Node code templates from predefined patterns"""

    TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "nodes"

    TEMPLATES = {
        "function": "function.template.py",
        "class": "class.template.py"
    }

    def __init__(self):
        if not self.TEMPLATE_DIR.exists():
            raise RuntimeError(
                f"Template directory not found: {self.TEMPLATE_DIR}"
            )

        self.env = Environment(
            loader=FileSystemLoader(str(self.TEMPLATE_DIR)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate(
        self,
        name: str,
        namespace: str = "custom",
        node_type: str = "function",
        description: str = "Custom node",
        output_dir: Optional[str] = None
    ) -> str:
        """Generate node file from template

        Args:
            name: Node name (snake_case, e.g., my_analyzer)
            namespace: Namespace (custom, org, etc.)
            node_type: Template type (function or class)
            description: Node description
            output_dir: Output directory path

        Returns:
            str: Path to created file

        Raises:
            ValueError: If node_type is invalid
            FileExistsError: If output file already exists
        """
        # Validate inputs
        if node_type not in self.TEMPLATES:
            raise ValueError(
                f"Unknown node type: {node_type}. "
                f"Valid types: {', '.join(self.TEMPLATES.keys())}"
            )

        # Prepare template variables
        class_name = self._to_class_name(name)
        template_vars = {
            "name": name,
            "namespace": namespace,
            "description": description,
            "ClassName": class_name
        }

        # Render template
        template = self.env.get_template(self.TEMPLATES[node_type])
        content = template.render(**template_vars)

        # Determine output path
        if output_dir is None:
            output_dir = Path.home() / ".outcomeforge" / "nodes"
        else:
            output_dir = Path(output_dir).expanduser()

        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{name}.py"

        # Check if file exists
        if output_file.exists():
            raise FileExistsError(
                f"File already exists: {output_file}\n"
                f"Use a different name or remove the existing file."
            )

        # Write file
        output_file.write_text(content, encoding="utf-8")

        return str(output_file)

    def _to_class_name(self, name: str) -> str:
        """Convert snake_case to CamelCase

        Examples:
            my_analyzer -> MyAnalyzer
            security_checker -> SecurityChecker
        """
        parts = name.replace("-", "_").split("_")
        return "".join(p.capitalize() for p in parts)

    def list_templates(self) -> Dict[str, str]:
        """List available node templates

        Returns:
            Dict mapping template name to description
        """
        return {
            "function": "Function-based node (simple, recommended for most cases)",
            "class": "Class-based node (advanced, with retry logic and state)"
        }


class ScenarioTemplateGenerator:
    """Generate Scenario YAML templates from patterns"""

    TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "scenarios"

    TEMPLATES = {
        "rag-query": "rag-query.template.yaml",
        "file-process": "file-process.template.yaml",
        "analyze-report": "analyze-report.template.yaml",
        "gate-check": "gate-check.template.yaml",
        "snapshot-restore": "snapshot-restore.template.yaml",
        "custom": "custom.template.yaml"
    }

    def __init__(self):
        if not self.TEMPLATE_DIR.exists():
            raise RuntimeError(
                f"Template directory not found: {self.TEMPLATE_DIR}"
            )

        self.env = Environment(
            loader=FileSystemLoader(str(self.TEMPLATE_DIR)),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def generate(
        self,
        name: str,
        template: str = "custom",
        description: str = "Custom scenario",
        author: str = "User",
        output_dir: Optional[str] = None
    ) -> str:
        """Generate scenario YAML from template

        Args:
            name: Scenario ID (e.g., my_workflow)
            template: Template type
            description: Scenario description
            author: Author name
            output_dir: Output directory path

        Returns:
            str: Path to created file

        Raises:
            ValueError: If template is invalid
            FileExistsError: If output file already exists
        """
        # Validate inputs
        if template not in self.TEMPLATES:
            raise ValueError(
                f"Unknown template: {template}. "
                f"Valid templates: {', '.join(self.TEMPLATES.keys())}"
            )

        # Prepare template variables
        display_name = self._to_display_name(name)
        template_vars = {
            "name": name,
            "Name": display_name,
            "description": description,
            "author": author
        }

        # Render template
        template_obj = self.env.get_template(self.TEMPLATES[template])
        content = template_obj.render(**template_vars)

        # Determine output path
        if output_dir is None:
            output_dir = Path.home() / ".outcomeforge" / "scenarios"
        else:
            output_dir = Path(output_dir).expanduser()

        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{name}.yaml"

        # Check if file exists
        if output_file.exists():
            raise FileExistsError(
                f"File already exists: {output_file}\n"
                f"Use a different name or remove the existing file."
            )

        # Write file
        output_file.write_text(content, encoding="utf-8")

        return str(output_file)

    def _to_display_name(self, name: str) -> str:
        """Convert ID to display name

        Examples:
            my_workflow -> My Workflow
            security_scan -> Security Scan
        """
        parts = name.replace("_", " ").replace("-", " ").split()
        return " ".join(p.capitalize() for p in parts)

    def list_templates(self) -> Dict[str, str]:
        """List available scenario templates

        Returns:
            Dict mapping template name to description
        """
        return {
            "rag-query": "RAG Query - Ask questions about codebase with LLM",
            "file-process": "File Processing - Collect and process files",
            "analyze-report": "Analysis & Report - Analyze code and generate reports",
            "gate-check": "Quality Gate - Enforce quality thresholds",
            "snapshot-restore": "Snapshot & Restore - Version control pattern",
            "custom": "Custom - Start from blank template"
        }
