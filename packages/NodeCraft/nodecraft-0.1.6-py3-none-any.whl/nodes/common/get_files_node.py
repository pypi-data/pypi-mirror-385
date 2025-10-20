from engine import node
from pathlib import Path
import fnmatch

def get_files_node():
    """Get files from project matching specified patterns

    This node scans the project directory and returns a list of files
    that match the given patterns, respecting exclude rules.
    """

    # Metadata declaration
    metadata = {
        "id": "get_files",
        "namespace": "common",
        "description": "Scan project and collect files matching patterns",
        "params_schema": {
            "patterns": {
                "type": "list",
                "default": ["**/*"],
                "description": "Glob patterns to match files (e.g., **/*.py, src/**/*.js)"
            },
            "exclude": {
                "type": "list",
                "default": ["node_modules/**", ".git/**", "__pycache__/**"],
                "description": "Patterns to exclude"
            },
            "extensions": {
                "type": "list",
                "default": [],
                "description": "File extensions to include (e.g., ['.py', '.js'])"
            }
        },
        "input_keys": ["project_root"],
        "output_keys": ["files", "file_count"]
    }

    def prep(ctx, params):
        project_root = Path(ctx.get("project_root", ".")).resolve()
        patterns = params.get("patterns", ["**/*"])
        exclude = params.get("exclude", ["node_modules/**", ".git/**", "__pycache__/**"])
        extensions = params.get("extensions", [])
        return {
            "project_root": project_root,
            "patterns": patterns,
            "exclude": exclude,
            "extensions": extensions
        }

    def exec(prep_result, params):
        root = prep_result["project_root"]
        patterns = prep_result["patterns"]
        exclude = prep_result["exclude"]
        exts = prep_result["extensions"]

        all_files = set()

        # Use glob for each pattern
        for pattern in patterns:
            for path in root.glob(pattern):
                if not path.is_file():
                    continue
                rel = path.relative_to(root).as_posix()

                # exclude
                excluded = False
                for ex in exclude:
                    if fnmatch.fnmatch(rel, ex) or fnmatch.fnmatch(rel, ex.rstrip('/**')):
                        excluded = True
                        break
                if excluded:
                    continue

                # extension
                if exts and path.suffix not in exts:
                    continue

                all_files.add(str(path.resolve()))

        return sorted(list(all_files))

    def post(ctx, prep_result, exec_result, params):
        ctx["files"] = exec_result
        ctx["file_count"] = len(exec_result)
        return "files_retrieved"

    node_func = node(prep=prep, exec=exec, post=post)
    node_func["metadata"] = metadata
    return node_func
