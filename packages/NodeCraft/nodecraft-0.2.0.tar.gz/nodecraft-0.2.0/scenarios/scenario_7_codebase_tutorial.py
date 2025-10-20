"""
场景⑦：代码库教程生成 (Codebase Tutorial Generation)

从GitHub仓库或本地目录生成结构化教程文档

工作流：
1. FetchRepo: 爬取GitHub仓库或本地目录的代码文件
2. IdentifyAbstractions: 使用LLM识别代码库中的核心抽象概念
3. AnalyzeRelationships: 分析抽象概念之间的关系
4. OrderChapters: 智能排序教程章节
5. WriteChapters: 为每个概念生成教程章节
6. CombineTutorial: 合并成最终的完整教程

特点：
- 支持GitHub仓库和本地目录
- 多语言支持（英文、中文等）
- 智能文件过滤（include/exclude patterns）
- LLM响应缓存优化
- 状态保存与恢复
"""

from engine import Flow
from nodes.common import FetchFiles
from nodes.tutorial import (
    IdentifyAbstractions,
    AnalyzeRelationships,
    OrderChapters,
    WriteChapters,
    CombineTutorial
)


# Default file patterns
DEFAULT_INCLUDE_PATTERNS = {
    "*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.go", "*.java", "*.pyi", "*.pyx",
    "*.c", "*.cc", "*.cpp", "*.h", "*.md", "*.rst", "*Dockerfile",
    "*Makefile", "*.yaml", "*.yml", "*.rs", "Cargo.toml",
}

DEFAULT_EXCLUDE_PATTERNS = {
    "assets/*", "data/*", "images/*", "public/*", "static/*", "temp/*",
    "*docs/*", "*venv/*", "*.venv/*", "*test*", "*tests/*", "*examples/*",
    "v1/*", "*dist/*", "*build/*", "*experimental/*", "*deprecated/*",
    "*misc/*", "*legacy/*", ".git/*", ".github/*", ".next/*", ".vscode/*",
    "*obj/*", "*bin/*", "*node_modules/*", "*.log", "**/target/*"
}


def create_tutorial_flow():
    """Creates and returns the codebase tutorial generation flow."""

    # Instantiate nodes - using common FetchFiles instead of tutorial-specific FetchRepo
    fetch_files = FetchFiles()
    identify_abstractions = IdentifyAbstractions(max_retries=5, wait=20)
    analyze_relationships = AnalyzeRelationships(max_retries=5, wait=20)
    order_chapters = OrderChapters(max_retries=5, wait=20)
    write_chapters = WriteChapters(max_retries=5, wait=20)  # This is a BatchNode
    combine_tutorial = CombineTutorial()

    # Connect nodes in sequence based on the design
    fetch_files >> identify_abstractions
    identify_abstractions >> analyze_relationships
    analyze_relationships >> order_chapters
    order_chapters >> write_chapters
    write_chapters >> combine_tutorial

    # Create the flow starting with FetchFiles
    tutorial_flow = Flow(start=fetch_files)

    return tutorial_flow


def run(config=None):
    """运行场景⑦：代码库教程生成"""
    config = config or {}

    # Validate inputs
    if not config.get("repo_url") and not config.get("local_dir"):
        return {"error": "Either repo_url or local_dir must be provided"}

    # Derive project name if not provided
    project_name = config.get("project_name")
    if not project_name:
        if config.get("repo_url"):
            project_name = config["repo_url"].split("/")[-1].replace(".git", "")
        else:
            import os
            project_name = os.path.basename(os.path.abspath(config["local_dir"]))

    # Initialize the shared dictionary with inputs
    shared = {
        "repo_url": config.get("repo_url"),
        "local_dir": config.get("local_dir"),
        "project_name": project_name,
        "github_token": config.get("github_token"),
        "output_dir": config.get("output_dir", "output"),

        # Add include/exclude patterns and max file size
        "include_patterns": config.get("include_patterns", DEFAULT_INCLUDE_PATTERNS),
        "exclude_patterns": config.get("exclude_patterns", DEFAULT_EXCLUDE_PATTERNS),
        "max_file_size": config.get("max_file_size", 100000),

        # Add language for multi-language support
        "language": config.get("language", "english"),

        # Add use_cache flag
        "use_cache": config.get("use_cache", True),

        # Add max_abstraction_num parameter
        "max_abstraction_num": config.get("max_abstraction_num", 10),

        # Enable state saving for tutorial scenario (for checkpoint/resume with large repos)
        "save_state_enabled": True,

        # Outputs will be populated by the nodes
        "files": [],
        "abstractions": [],
        "relationships": {},
        "chapter_order": [],
        "chapters": [],
        "final_output_dir": None
    }

    # Display starting message
    print(f"Starting tutorial generation for: {config.get('repo_url') or config.get('local_dir')}")
    print(f"Language: {shared['language'].capitalize()}")
    print(f"LLM caching: {'Enabled' if shared['use_cache'] else 'Disabled'}")

    # Create the flow instance
    tutorial_flow = create_tutorial_flow()

    # Run the flow
    tutorial_flow.run(shared)

    # Return results
    return shared
