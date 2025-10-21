"""
Generic file fetching node - Supports GitHub repositories and local directories

Can be reused by multiple scenarios:
- Scenario 2: Repository Adaptation
- Scenario 5: Local RAG
- Scenario 7: Tutorial Generation
"""

import os
from engine import Node
from utils.crawl_github_files import crawl_github_files
from utils.crawl_local_files import crawl_local_files
from utils.state_manager import save_state


class FetchFiles(Node):
    """
    Generic file fetching node (class version, used for pocketflow)

    Parameters from shared:
    - repo_url: GitHub repository URL (optional)
    - local_dir: Local directory path (optional, choose one)
    - github_token: GitHub token (optional, for private repos)
    - include_patterns: File patterns to include (set)
    - exclude_patterns: File patterns to exclude (set)
    - max_file_size: Maximum file size (bytes)
    - project_name: Project name (optional, auto-derived)
    - save_state_enabled: Save state (default False, used by tutorial scenario)

    Output to shared:
    - files: [(path, content), ...] file list
    - project_name: Project name
    - fetch_stats: Fetch statistics (optional)
    """

    def prep(self, shared):
        repo_url = shared.get("repo_url")
        local_dir = shared.get("local_dir")
        project_name = shared.get("project_name")

        # Derive project name if not provided
        if not project_name:
            if repo_url:
                project_name = repo_url.split("/")[-1].replace(".git", "")
            elif local_dir:
                project_name = os.path.basename(os.path.abspath(local_dir))
            else:
                project_name = "unknown_project"

            # Store in shared for other nodes
            shared["project_name"] = project_name

        return {
            "repo_url": repo_url,
            "local_dir": local_dir,
            "project_name": project_name,
            "token": shared.get("github_token"),
            "include_patterns": shared.get("include_patterns"),
            "exclude_patterns": shared.get("exclude_patterns"),
            "max_file_size": shared.get("max_file_size", 100000),
            "use_relative_paths": shared.get("use_relative_paths", True),
            "save_state_enabled": shared.get("save_state_enabled", False)
        }

    def exec(self, prep_res):
        if prep_res["repo_url"]:
            print(f"Crawling repository: {prep_res['repo_url']}...")
            result = crawl_github_files(
                repo_url=prep_res["repo_url"],
                token=prep_res["token"],
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

    def post(self, shared, prep_res, exec_res):
        shared["files"] = exec_res["files"]

        # Optionally save stats if the key exists in shared
        if "fetch_stats" in shared or exec_res["stats"]:
            shared["fetch_stats"] = exec_res["stats"]

        shared["project_name"] = exec_res["project_name"]

        # Save state if enabled (for tutorial scenario)
        if exec_res["save_state_enabled"]:
            save_state(exec_res["project_name"], "fetch", {"files": exec_res["files"]})
