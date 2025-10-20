"""
Node Registry - Auto-discovery and registration mechanism for nodes

This module provides:
- Automatic discovery of nodes from specified directories
- Support for both function-based and class-based nodes
- Namespace management (@common, @custom, @community)
- Metadata schema for node documentation
"""

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
import warnings


class NodeRegistry:
    """Node registration and discovery system

    The registry automatically discovers nodes from:
    1. Framework built-in nodes (outcomeforge/nodes/common/)
    2. Global user nodes (~/.outcomeforge/nodes/)
    3. Project-level nodes (.outcomeforge/nodes/)

    Example:
        >>> registry = NodeRegistry()
        >>> registry.auto_discover()
        >>> nodes = registry.list_nodes()
        >>> node = registry.get_node("@common/get_files")
    """

    def __init__(self, config_manager=None):
        """Initialize NodeRegistry

        Args:
            config_manager: Optional ConfigManager instance for configuration
        """
        self.nodes: Dict[str, dict] = {}
        self._scan_dirs: List[Path] = []
        self.config_manager = config_manager
        self._setup_scan_dirs()

    def _setup_scan_dirs(self):
        """Setup directories to scan for nodes"""
        # Framework built-in nodes
        try:
            # Get the outcomeforge package root
            import outcomeforge
            package_root = Path(outcomeforge.__file__).parent
            builtin_nodes = package_root / "nodes" / "common"
            if builtin_nodes.exists():
                self._scan_dirs.append(builtin_nodes)
        except (ImportError, AttributeError):
            # If outcomeforge is not installed as package, use relative path
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent
            builtin_nodes = project_root / "nodes" / "common"
            if builtin_nodes.exists():
                self._scan_dirs.append(builtin_nodes)

        # Add configured search paths
        if self.config_manager:
            config_paths = self.config_manager.get_node_search_paths()
            for path in config_paths:
                if path.exists():
                    self._scan_dirs.append(path)

        # Global user nodes (default location)
        global_nodes = Path.home() / ".outcomeforge" / "nodes"
        if global_nodes.exists() and global_nodes not in self._scan_dirs:
            self._scan_dirs.append(global_nodes)

        # Project-level nodes (default location)
        project_nodes = Path.cwd() / ".outcomeforge" / "nodes"
        if project_nodes.exists() and project_nodes not in self._scan_dirs:
            self._scan_dirs.append(project_nodes)

    def auto_discover(self, additional_dirs: Optional[List[str]] = None):
        """Automatically discover all nodes from configured directories

        Args:
            additional_dirs: Optional list of additional directories to scan

        Example:
            >>> registry.auto_discover()
            >>> registry.auto_discover(additional_dirs=["./custom_nodes"])
        """
        scan_dirs = self._scan_dirs.copy()

        if additional_dirs:
            scan_dirs.extend([Path(d) for d in additional_dirs])

        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            self._scan_directory(scan_dir)

    def _scan_directory(self, directory: Path):
        """Scan a directory for node definitions

        Args:
            directory: Directory to scan
        """
        # Determine namespace from directory
        if "common" in directory.parts:
            default_namespace = "common"
        elif ".outcomeforge" in directory.parts:
            default_namespace = "custom"
        else:
            default_namespace = "custom"

        for py_file in directory.rglob("*.py"):
            # Skip __init__.py and private files
            if py_file.name.startswith("_"):
                continue

            self._load_node_from_file(py_file, default_namespace)

    def _load_node_from_file(self, file_path: Path, default_namespace: str):
        """Load node from a Python file

        Args:
            file_path: Path to Python file
            default_namespace: Default namespace if not specified in metadata
        """
        try:
            # Create a unique module name
            module_name = f"_node_module_{file_path.stem}_{id(file_path)}"

            # Load module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find node functions or classes
            for name, obj in inspect.getmembers(module):
                if name.startswith("_"):
                    continue

                if self._is_node_function(obj, name):
                    self._register_function_node(obj, name, default_namespace, file_path)
                elif self._is_node_class(obj):
                    self._register_class_node(obj, default_namespace, file_path)

        except Exception as e:
            warnings.warn(f"Failed to load node from {file_path}: {e}")

    def _is_node_function(self, obj: Any, name: str) -> bool:
        """Check if object is a node factory function

        Args:
            obj: Object to check
            name: Name of the object

        Returns:
            True if this is a node function
        """
        return (
            callable(obj) and
            name.endswith("_node") and
            not inspect.isclass(obj) and
            not name.startswith("_")
        )

    def _is_node_class(self, obj: Any) -> bool:
        """Check if object is a Node class

        Args:
            obj: Object to check

        Returns:
            True if this is a Node class
        """
        try:
            from engine import BaseNode, Node
            return (
                inspect.isclass(obj) and
                issubclass(obj, (BaseNode, Node)) and
                obj not in (BaseNode, Node)
            )
        except ImportError:
            return False

    def _register_function_node(
        self,
        func: Callable,
        name: str,
        default_namespace: str,
        file_path: Path
    ):
        """Register a function-based node

        Args:
            func: Node factory function
            name: Function name
            default_namespace: Default namespace
            file_path: Source file path
        """
        # Try to get an instance to extract metadata
        try:
            node_instance = func()
            metadata = node_instance.get("metadata", {}) if isinstance(node_instance, dict) else {}
        except Exception:
            metadata = {}

        # Extract metadata
        node_id = metadata.get("id", name.replace("_node", ""))
        namespace = metadata.get("namespace", default_namespace)
        full_id = f"@{namespace}/{node_id}"

        # Build complete metadata
        complete_metadata = {
            "id": node_id,
            "namespace": namespace,
            "full_id": full_id,
            "description": metadata.get("description", func.__doc__ or "No description"),
            "params_schema": metadata.get("params_schema", {}),
            "input_keys": metadata.get("input_keys", []),
            "output_keys": metadata.get("output_keys", []),
            "source_file": str(file_path),
            "source_type": "function"
        }

        self.nodes[full_id] = {
            "type": "function",
            "factory": func,
            "metadata": complete_metadata
        }

    def _register_class_node(
        self,
        cls: type,
        default_namespace: str,
        file_path: Path
    ):
        """Register a class-based node

        Args:
            cls: Node class
            default_namespace: Default namespace
            file_path: Source file path
        """
        node_id = getattr(cls, "id", cls.__name__.replace("Node", "").lower())
        namespace = getattr(cls, "namespace", default_namespace)
        full_id = f"@{namespace}/{node_id}"

        complete_metadata = {
            "id": node_id,
            "namespace": namespace,
            "full_id": full_id,
            "description": getattr(cls, "description", cls.__doc__ or "No description"),
            "params_schema": getattr(cls, "params_schema", {}),
            "input_keys": getattr(cls, "input_keys", []),
            "output_keys": getattr(cls, "output_keys", []),
            "source_file": str(file_path),
            "source_type": "class"
        }

        self.nodes[full_id] = {
            "type": "class",
            "class": cls,
            "metadata": complete_metadata
        }

    def get_node(self, node_id: str) -> Any:
        """Get a node instance by ID

        Args:
            node_id: Node ID (e.g., "@common/get_files")

        Returns:
            Node instance (dict for function nodes, object for class nodes)

        Raises:
            ValueError: If node not found

        Example:
            >>> node = registry.get_node("@common/get_files")
        """
        node_info = self.nodes.get(node_id)
        if not node_info:
            raise ValueError(
                f"Node not found: {node_id}\n"
                f"Available nodes: {', '.join(self.nodes.keys())}"
            )

        if node_info["type"] == "function":
            return node_info["factory"]()
        else:
            return node_info["class"]()

    def list_nodes(self, namespace: Optional[str] = None) -> List[dict]:
        """List all registered nodes

        Args:
            namespace: Optional namespace filter (e.g., "common", "custom")

        Returns:
            List of node metadata dictionaries

        Example:
            >>> all_nodes = registry.list_nodes()
            >>> custom_nodes = registry.list_nodes(namespace="custom")
        """
        result = []
        for node_id, node_info in sorted(self.nodes.items()):
            metadata = node_info["metadata"]
            if namespace and metadata.get("namespace") != namespace:
                continue
            result.append(metadata)
        return result

    def register_function_node_manually(
        self,
        func: Callable,
        node_id: str,
        namespace: str = "custom",
        metadata: Optional[dict] = None
    ):
        """Manually register a function-based node

        Args:
            func: Node factory function
            node_id: Unique node ID
            namespace: Namespace (default: "custom")
            metadata: Optional metadata dictionary

        Example:
            >>> registry.register_function_node_manually(
            ...     my_node_func,
            ...     "my_custom_node",
            ...     namespace="custom",
            ...     metadata={"description": "My custom node"}
            ... )
        """
        full_id = f"@{namespace}/{node_id}"

        complete_metadata = {
            "id": node_id,
            "namespace": namespace,
            "full_id": full_id,
            "description": metadata.get("description", func.__doc__ or "No description") if metadata else (func.__doc__ or "No description"),
            "params_schema": metadata.get("params_schema", {}) if metadata else {},
            "input_keys": metadata.get("input_keys", []) if metadata else [],
            "output_keys": metadata.get("output_keys", []) if metadata else [],
            "source_type": "manual"
        }

        self.nodes[full_id] = {
            "type": "function",
            "factory": func,
            "metadata": complete_metadata
        }

    def register_from_file(self, file_path: str, namespace: str = "custom") -> List[str]:
        """Register node(s) from a Python file

        Args:
            file_path: Path to Python file containing node(s)
            namespace: Default namespace if not specified in metadata

        Returns:
            List of registered node IDs

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file contains no valid nodes

        Example:
            >>> registry.register_from_file("./my_node.py")
            ['@custom/my_node']
        """
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        initial_count = len(self.nodes)
        initial_ids = set(self.nodes.keys())

        self._load_node_from_file(path, namespace)

        new_ids = [nid for nid in self.nodes.keys() if nid not in initial_ids]

        if len(self.nodes) == initial_count:
            raise ValueError(
                f"No valid nodes found in {file_path}\n"
                f"Ensure the file contains functions ending with '_node' or classes inheriting from Node"
            )

        return new_ids

    def register_from_directory(
        self,
        directory: str,
        namespace: str = "custom",
        recursive: bool = False
    ) -> List[str]:
        """Register all nodes from a directory

        Args:
            directory: Directory path
            namespace: Default namespace
            recursive: If True, scan subdirectories recursively

        Returns:
            List of registered node IDs

        Raises:
            FileNotFoundError: If directory doesn't exist
            ValueError: If directory is not a directory

        Example:
            >>> registry.register_from_directory("./custom_nodes", recursive=True)
            ['@custom/node1', '@custom/node2']
        """
        path = Path(directory).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not path.is_dir():
            raise ValueError(f"Not a directory: {directory}")

        initial_ids = set(self.nodes.keys())

        if recursive:
            pattern = "**/*.py"
        else:
            pattern = "*.py"

        for py_file in path.glob(pattern):
            if py_file.name.startswith("_"):
                continue
            try:
                self._load_node_from_file(py_file, namespace)
            except Exception as e:
                warnings.warn(f"Failed to load {py_file}: {e}")

        new_ids = [nid for nid in self.nodes.keys() if nid not in initial_ids]
        return new_ids


# Global registry instance
node_registry = NodeRegistry()
