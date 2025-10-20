"""
Context Integration - Automatic context injection for scenarios

Provides:
- Automatic RAG context collection before scenario execution
- Customizable context patterns and queries
- Context injection without modifying scenario definitions
"""

from pathlib import Path
from typing import Optional, List, Dict, Any


class ContextInjector:
    """Inject context collection nodes before scenario execution

    Example:
        >>> injector = ContextInjector(node_registry)
        >>> enhanced_flow = injector.inject_rag_context(
        ...     original_flow,
        ...     patterns=["**/*.py"],
        ...     context_query="Summarize project architecture"
        ... )
    """

    def __init__(self, node_registry):
        """Initialize with node registry

        Args:
            node_registry: NodeRegistry instance
        """
        self.node_registry = node_registry

    def inject_rag_context(
        self,
        original_flow,
        patterns: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        context_query: Optional[str] = None,
        context_key: str = "project_context",
        **kwargs
    ):
        """Inject RAG context collection before flow execution

        This prepends context collection nodes to the existing flow,
        making project context available to all subsequent nodes.

        Args:
            original_flow: Original Flow object
            patterns: File patterns to include in context
            exclude: Patterns to exclude
            context_query: Optional query to ask about the context
            context_key: Key to store context in shared store
            **kwargs: Additional parameters for context nodes

        Returns:
            Enhanced Flow with context collection prepended

        Example:
            >>> flow = scenario_loader.create_flow(scenario_def, {})
            >>> enhanced = injector.inject_rag_context(
            ...     flow,
            ...     patterns=["**/*.py", "**/*.md"],
            ...     context_query="What is the project about?"
            ... )
        """
        from engine import Flow

        # Create new flow
        enhanced_flow = Flow()

        # Default patterns
        if patterns is None:
            patterns = ["**/*.py", "**/*.md", "**/*.txt"]

        if exclude is None:
            exclude = [
                "node_modules/**",
                ".git/**",
                "__pycache__/**",
                "*.pyc",
                ".pytest_cache/**",
                "dist/**",
                "build/**",
                "*.egg-info/**"
            ]

        # Step 1: Get files for context
        get_files_node = self.node_registry.get_node("@common/get_files")
        enhanced_flow.add(
            get_files_node,
            name="_context_get_files",
            params={
                "patterns": patterns,
                "exclude": exclude
            }
        )

        # Step 2: Format files to prompt
        files_to_prompt_node = self.node_registry.get_node("@common/files_to_prompt")
        enhanced_flow.add(
            files_to_prompt_node,
            name="_context_format",
            params={
                "format": kwargs.get("format", "xml"),
                "cxml": kwargs.get("cxml", True),
                "include_line_numbers": kwargs.get("include_line_numbers", False),
                "output_key": context_key
            }
        )

        # Step 3 (optional): Ask LLM about context if query provided
        if context_query:
            call_llm_node = self.node_registry.get_node("@common/call_llm")
            enhanced_flow.add(
                call_llm_node,
                name="_context_summarize",
                params={
                    "prompt_template": f"""Here is the project context:

{{{context_key}}}

Question: {context_query}

Please analyze the codebase and answer concisely.""",
                    "model": kwargs.get("model", "claude-3-haiku-20240307"),
                    "temperature": 0.2,
                    "max_tokens": kwargs.get("max_tokens", 2000)
                }
            )

        # Add all nodes from original flow
        for node_info in original_flow.nodes:
            enhanced_flow.add(
                node_info["node"],
                name=node_info["name"],
                on=node_info.get("on"),
                params=node_info.get("params", {})
            )

        return enhanced_flow

    def create_context_scenario(
        self,
        patterns: Optional[List[str]] = None,
        query: str = "Summarize this codebase",
        **kwargs
    ) -> Dict[str, Any]:
        """Create a standalone context collection scenario

        This is useful for quick context exploration without a full scenario.

        Args:
            patterns: File patterns to include
            query: Question to ask about the codebase
            **kwargs: Additional parameters

        Returns:
            Scenario definition dictionary

        Example:
            >>> scenario_def = injector.create_context_scenario(
            ...     patterns=["**/*.py"],
            ...     query="What is the main purpose of this project?"
            ... )
        """
        if patterns is None:
            patterns = ["**/*.py"]

        return {
            "scenario": {
                "id": "_quick_context",
                "name": "Quick Context Query",
                "description": "Quickly query project context"
            },
            "parameters": {
                "patterns": {
                    "type": "list",
                    "default": patterns
                },
                "query": {
                    "type": "str",
                    "default": query
                }
            },
            "steps": [
                {
                    "node": "@common/get_files",
                    "name": "get_files",
                    "params": {
                        "patterns": "{{params.patterns}}"
                    }
                },
                {
                    "node": "@common/files_to_prompt",
                    "name": "format_context",
                    "params": {
                        "format": "xml",
                        "cxml": True
                    }
                },
                {
                    "node": "@common/call_llm",
                    "name": "query_context",
                    "params": {
                        "prompt_template": "{formatted_prompt}\n\nQuestion: {{params.query}}",
                        "model": kwargs.get("model", "claude-3-haiku-20240307")
                    }
                }
            ]
        }


def inject_context_to_scenario_run(
    scenario_registry,
    scenario_id: str,
    user_params: Dict[str, Any],
    context_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Helper function to run a scenario with automatic context injection

    Args:
        scenario_registry: ScenarioRegistry instance
        scenario_id: Scenario ID to run
        user_params: User parameters for the scenario
        context_config: Context injection configuration
            - patterns: List of file patterns
            - exclude: List of exclude patterns
            - query: Optional context query
            - enabled: Whether to inject context (default True)

    Returns:
        Execution result dictionary

    Example:
        >>> result = inject_context_to_scenario_run(
        ...     scenario_registry,
        ...     "my_scenario",
        ...     {"param1": "value1"},
        ...     context_config={"patterns": ["**/*.py"], "query": "Overview?"}
        ... )
    """
    if context_config is None:
        context_config = {}

    # Get scenario definition
    scenario_def = scenario_registry.get_scenario(scenario_id)

    # Build flow
    from core.scenario_loader import ScenarioLoader
    loader = ScenarioLoader(scenario_registry.node_registry)
    flow = loader.create_flow(scenario_def, user_params)

    # Inject context if enabled
    if context_config.get("enabled", True):
        injector = ContextInjector(scenario_registry.node_registry)
        flow = injector.inject_rag_context(
            flow,
            patterns=context_config.get("patterns"),
            exclude=context_config.get("exclude"),
            context_query=context_config.get("query")
        )

    # Run flow
    shared_store = user_params.copy() if user_params else {}
    if "project_root" not in shared_store:
        shared_store["project_root"] = str(Path.cwd())

    result = flow.run(shared_store)
    return result
