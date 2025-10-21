"""
Generic file fetching node - Supports GitHub repositories and local directories

Can be reused by multiple scenarios:
- Scenario 2: Repository Adaptation
- Scenario 5: Local RAG
- Scenario 7: Tutorial Generation
"""

from engine import node
from utils import crawl_github_files, crawl_local_files, save_state
import os


def fetch_files_node():
    """
    Generic file fetching node

    Input parameters (params):
    - repo_url: GitHub repository URL (optional)
    - local_dir: Local directory path (optional, choose one)
    - github_token: GitHub token (optional, for private repos)
    - include_patterns: File patterns to include (set)
    - exclude_patterns: File patterns to exclude (set)
    - max_file_size: Maximum file size (bytes)
    - project_name: Project name (optional, auto-derived)
    - use_relative_paths: Use relative paths (default True)
    - save_state_enabled: Save state (default False, used by tutorial scenario)

    Output to context:
    - files: [(path, content), ...] file list
    - project_name: Project name
    - fetch_stats: Fetch statistics
    """

    def prep(ctx, params):
        repo_url = params.get("repo_url")
        local_dir = params.get("local_dir")
        project_name = params.get("project_name")

        # Derive project name if not provided
        if not project_name:
            if repo_url:
                project_name = repo_url.split("/")[-1].replace(".git", "")
            elif local_dir:
                project_name = os.path.basename(os.path.abspath(local_dir))
            else:
                project_name = "unknown_project"

            # Store in context for other nodes
            ctx["project_name"] = project_name

        return {
            "repo_url": repo_url,
            "local_dir": local_dir,
            "project_name": project_name,
            "github_token": params.get("github_token"),
            "include_patterns": params.get("include_patterns"),
            "exclude_patterns": params.get("exclude_patterns"),
            "max_file_size": params.get("max_file_size", 100000),
            "use_relative_paths": params.get("use_relative_paths", True),
            "save_state_enabled": params.get("save_state_enabled", False)
        }

    def exec(prep_res):
        if prep_res["repo_url"]:
            print(f"Crawling repository: {prep_res['repo_url']}...")
            result = crawl_github_files(
                repo_url=prep_res["repo_url"],
                token=prep_res["github_token"],
                include_patterns=prep_res["include_patterns"],
                exclude_patterns=prep_res["exclude_patterns"],
                max_file_size=prep_res["max_file_size"],
                use_relative_paths=prep_res["use_relative_paths"],
            )
        elif prep_res["local_dir"]:
            print(f"Crawling directory: {prep_res['local_dir']}...")
            result = crawl_local_files(
                directory=prep_res["local_dir"],
                include_patterns=prep_res["include_patterns"],
                exclude_patterns=prep_res["exclude_patterns"],
                max_file_size=prep_res["max_file_size"],
                use_relative_paths=prep_res["use_relative_paths"]
            )
        else:
            raise ValueError("Either repo_url or local_dir must be provided")

        # Convert dict to list of tuples: [(path, content), ...]
        files_list = list(result.get("files", {}).items())

        if len(files_list) == 0:
            raise ValueError("Failed to fetch files or no files matched patterns")

        print(f"Fetched {len(files_list)} files.")

        return {
            "files": files_list,
            "stats": result.get("stats", {}),
            "project_name": prep_res["project_name"],
            "save_state_enabled": prep_res["save_state_enabled"]
        }

    def post(ctx, prep_res, exec_res):
        ctx["files"] = exec_res["files"]
        ctx["fetch_stats"] = exec_res["stats"]
        ctx["project_name"] = exec_res["project_name"]

        # Save state if enabled (for tutorial scenario)
        if exec_res["save_state_enabled"]:
            save_state(exec_res["project_name"], "fetch", {"files": exec_res["files"]})

        return "files_fetched"

    return node(prep=prep, exec=exec, post=post)
