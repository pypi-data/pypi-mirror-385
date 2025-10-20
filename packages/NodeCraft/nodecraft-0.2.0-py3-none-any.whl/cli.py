"""
NodeCraft CLI - A modular framework to forge and verify intelligent outcomes.

Supported scenarios:
  1. snapshot: Local snapshot and rollback (no GitHub dependency)
  2. adapt: Open-source repository understanding and adaptation
  3. regression: Regression detection with diff analysis
  4. arch-drift: Architecture drift and impact scanning
  5. rag: Local lightweight RAG (Files-to-Prompt)
  6. code-review: Code review pipeline (security, quality, performance)
  7. wiki: Codebase wiki generation
"""

import click
import json
import hashlib
from pathlib import Path
from scenarios import scenario_1_local_snapshot
from scenarios import scenario_2_repo_adapt
from scenarios import scenario_3_regression
from scenarios import scenario_4_arch_drift
from scenarios import scenario_5_local_rag
from scenarios import scenario_6_code_review
from scenarios import scenario_7_codebase_tutorial


class NaturalOrderGroup(click.Group):
    """Custom Click Group that maintains command order"""
    def list_commands(self, ctx):
        return list(self.commands)

@click.group(cls=NaturalOrderGroup, invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """NodeCraft - A modular framework to forge and verify intelligent outcomes.

    \b
    Quick Start:
      nodecraft tutorial                # Getting started guide
      nodecraft tutorial node           # Create custom nodes
      nodecraft nodes list              # Discover available nodes
      nodecraft scenarios list          # See all scenarios

    \b
    Supported scenarios:
      1. snapshot - Local snapshot and rollback (no GitHub dependency)
      2. adapt - Open-source repository understanding and adaptation
      3. regression - Regression detection with diff analysis
      4. arch-drift - Architecture drift and impact scanning
      5. rag - Local lightweight RAG (Files-to-Prompt)
      6. code-review - Code review pipeline (security, quality, performance)
      7. wiki - Codebase wiki generation
    """
    # If no command specified, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command(name='tutorial')
@click.argument('topic', default='main', required=False)
def tutorial_cmd(topic):
    """Show interactive tutorials

    \b
    Available topics:
      main              - Getting Started Guide (default)
      node              - Create Your First Custom Node
      node-class        - Create Class-Based Nodes
      scenario          - Create Your First YAML Scenario
      scenario-advanced - Advanced Scenario Patterns
      registry          - Understanding the Registry System
      list              - List all tutorials

    \b
    Examples:
      nodecraft tutorial                # Show getting started
      nodecraft tutorial node           # Node creation tutorial
      nodecraft tutorial scenario       # Scenario tutorial
      nodecraft tutorial list           # List all tutorials
    """
    from core.tutorials import get_tutorial, list_tutorials

    if topic == "list":
        click.echo(list_tutorials())
    else:
        click.echo(get_tutorial(topic))


@cli.command()
@click.option('--patterns', multiple=True, default=['**/*.py'], help='File matching patterns')
@click.option('--model', default='gpt-4', help='LLM model')
def snapshot(patterns, model):
    """Scenario 1: Local snapshot and rollback (no GitHub dependency)

    Scan project files, parse code structure, use AI to analyze and create snapshot
    """
    click.echo("Scenario 1: Local snapshot and rollback")
    config = {
        'file_patterns': list(patterns),
        'model': model
    }
    result = scenario_1_local_snapshot.run(config)
    snapshot_id = result.get('snapshot_id')
    if snapshot_id:
        click.echo(f"Snapshot created: {snapshot_id}")
        response = result.get('llm_response', '')
        if response:
            preview = response[:300] + "..." if len(response) > 300 else response
            click.echo(f"\nSnapshot preview:\n{preview}\n")
    else:
        click.echo("Snapshot created (mock LLM content), see .ai-snapshots/ directory")


@cli.command(name='snapshot-list')
def snapshot_list():
    """List all snapshots"""
    snapshots_dir = Path(".ai-snapshots")
    if not snapshots_dir.exists():
        click.echo("No snapshots found")
        return

    snapshot_files = sorted(snapshots_dir.glob("snapshot-*.json"), reverse=True)

    if not snapshot_files:
        click.echo("No snapshots found")
        return

    click.echo("Available Snapshots:\n")
    for snap_file in snapshot_files:
        try:
            with open(snap_file, 'r') as f:
                data = json.load(f)
            timestamp = data.get('timestamp', 'unknown')
            file_count = len(data.get('files', {}))
            snapshot_id = snap_file.stem.replace('snapshot-', '')
            click.echo(f"  [{snapshot_id}] {timestamp} - {file_count} files")
        except Exception as e:
            click.echo(f"  [Error] {snap_file.name}: {e}")


@cli.command(name='snapshot-restore')
@click.argument('snapshot_id')
def snapshot_restore(snapshot_id):
    """Restore files from snapshot

    Example: python cli.py snapshot-restore 20250101_120000
    """
    snapshot_file = Path(f".ai-snapshots/snapshot-{snapshot_id}.json")

    if not snapshot_file.exists():
        click.echo(f"Snapshot not found: {snapshot_id}")
        click.echo("Run 'python cli.py snapshot-list' to see available snapshots")
        return

    try:
        with open(snapshot_file, 'r') as f:
            snapshot_data = json.load(f)

        files = snapshot_data.get('files', {})
        restored_count = 0
        hash_matches = 0

        click.echo(f"Restoring from snapshot {snapshot_id}...\n")

        for file_path, file_data in files.items():
            content = file_data.get('content', '')
            expected_hash = file_data.get('hash', '')

            # Write file
            full_path = Path(file_path)
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Verify hash
            actual_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            if actual_hash == expected_hash:
                hash_matches += 1

            restored_count += 1

        click.echo(f"Restored {restored_count} files")
        click.echo(f"Hash verification: {hash_matches}/{restored_count} files matched")

        if hash_matches == restored_count:
            click.echo("All files restored successfully with matching hashes")
        else:
            click.echo("Some files have hash mismatches")

    except Exception as e:
        click.echo(f"Error restoring snapshot: {e}")


@cli.command()
@click.argument('repo', required=False)
@click.option('--model', default='gpt-4', help='LLM model')
def adapt(repo, model):
    """Scenario 2: Open-source repository understanding and adaptation

    Analyze open-source repository and generate adaptation plan

    Example:
      python cli.py adapt https://github.com/pallets/flask
    """
    if not repo:
        click.echo("Repository URL required")
        click.echo("Example: python cli.py adapt https://github.com/pallets/flask")
        return

    click.echo(f"Scenario 2: Repository understanding and adaptation")
    click.echo(f"Repository: {repo}")

    config = {'repo_url': repo, 'model': model}
    result = scenario_2_repo_adapt.run(config)

    if result.get('error'):
        click.echo(f"Error: {result['error']}")
        return

    out = result.get('output_file_path')
    if out:
        click.echo(f"Adaptation plan saved: {out}")
        if 'llm_response' in result:
            response = result['llm_response']
            if 'plan:' in response:
                plan_start = response.find('plan:')
                plan_section = response[plan_start:plan_start+500]
                click.echo(f"\nPlan summary:\n{plan_section}...\n")


@cli.command()
@click.option('--baseline', default='main~1', help='Baseline version (default: main~1)')
@click.option('--build', default='HEAD', help='Build version (default: HEAD)')
@click.option('--model', default='gpt-4', help='LLM model')
@click.option('--pass-rate-min', default=95, help='Minimum test pass rate')
@click.option('--coverage-drop-max', default=5, help='Maximum coverage drop')
def regression(baseline, build, model, pass_rate_min, coverage_drop_max):
    """Scenario 3: Regression detection with diff analysis

    Collect test, coverage, and lint metrics; AI evaluates quality gate
    """
    click.echo("Scenario 3: Regression detection")
    click.echo(f"Baseline: {baseline}, Build: {build}")

    config = {
        'baseline': baseline,
        'build': build,
        'model': model,
        'pass_rate_min': pass_rate_min,
        'coverage_drop_max': coverage_drop_max
    }
    result = scenario_3_regression.run(config)

    out = result.get('output_file_path')
    if out:
        click.echo(f"Quality gate result saved: {out}")
        if 'llm_response' in result:
            response = result['llm_response']
            if 'gate:' in response or 'PASS' in response or 'FAIL' in response:
                lines = response.split('\n')[:10]
                click.echo(f"\nGate decision:\n" + '\n'.join(lines) + "\n")


@cli.command(name='arch-drift')
@click.option('--model', default='gpt-4', help='LLM model')
def arch_drift(model):
    """Scenario 4: Architecture drift and impact scanning

    Analyze dependency graph, layer violations, complexity, API breakage; AI audits architecture health
    """
    click.echo("Scenario 4: Architecture drift scanning")

    config = {'model': model}
    result = scenario_4_arch_drift.run(config)

    out = result.get('output_file_path')
    if out:
        click.echo(f"Architecture gate result saved: {out}")
        if 'llm_response' in result:
            response = result['llm_response']
            if 'arch_gate:' in response or 'score:' in response:
                lines = response.split('\n')[:15]
                click.echo(f"\nArchitecture assessment:\n" + '\n'.join(lines) + "\n")


@cli.command()
@click.option('--patterns', multiple=True, default=['**/*.py'], help='File matching patterns (can specify multiple)')
@click.option('--query', required=True, help='Query to ask LLM')
@click.option('--format', type=click.Choice(['xml', 'markdown']), default='xml', help='Output format')
@click.option('--cxml', is_flag=True, help='Use compact XML format (for long context)')
@click.option('--line-numbers', is_flag=True, help='Include line numbers')
@click.option('--model', default='claude-3-haiku-20240307', help='LLM model')
def rag(patterns, query, format, cxml, line_numbers, model):
    """Scenario 5: Local lightweight RAG (Files-to-Prompt)

    Quick LLM understanding of codebase and question answering

    Use cases:
      1. Project overview: --query "How does this project work?"
      2. Generate docs: --patterns "tests/**/*.py" --query "Generate API docs"
      3. Locate feature: --query "Where is JWT validation implemented?" --line-numbers
      4. Code review: --query "Review code quality"

    Examples:
      python cli.py rag --patterns "**/*.py" --query "What is the project architecture?"
      python cli.py rag --patterns "tests/**" --query "Generate test documentation" --format markdown
    """
    click.echo("Scenario 5: Local lightweight RAG")
    click.echo(f"File patterns: {', '.join(patterns)}")
    click.echo(f"Query: {query}\n")

    result = scenario_5_local_rag.run_rag_query(
        project_root=".",
        patterns=list(patterns),
        query=query,
        model=model,
        format=format,
        cxml=cxml,
        include_line_numbers=line_numbers
    )

    # Display statistics
    stats = result.get('files_to_prompt_stats', {})
    if stats:
        click.echo(f"Statistics:")
        click.echo(f"   - Files processed: {stats.get('files_processed', 0)}")
        click.echo(f"   - Total lines: {stats.get('total_lines', 0):,}")
        click.echo(f"   - Total characters: {stats.get('total_chars', 0):,}")
        click.echo(f"   - Average lines per file: {stats.get('avg_lines_per_file', 0)}\n")

    # Display LLM response
    response = result.get('llm_response', '')
    if response:
        click.echo("LLM response:")
        click.echo("-" * 80)
        click.echo(response)
        click.echo("-" * 80)
    else:
        error = result.get('files_to_prompt_error') or result.get('llm_error')
        if error:
            click.echo(f"Error: {error}")
        else:
            click.echo("No response received")


@cli.command(name='code-review')
@click.option('--git-diff', is_flag=True, help='Review current git changes')
@click.option('--git-ref', default=None, help='Git reference to diff against (e.g., HEAD~1, main)')
@click.option('--diff', 'diff_file', default=None, help='Path to diff/patch file')
@click.option('--output', default=None, help='Output file path')
@click.option('--format', 'output_format', type=click.Choice(['yaml', 'json', 'markdown']), default='yaml', help='Output format')
@click.option('--security-only', is_flag=True, help='Only run security checks')
def code_review(git_diff, git_ref, diff_file, output, output_format, security_only):
    """Scenario 6: Code review pipeline (security, quality, performance)

    Reviews code changes for security, quality, and performance issues.

    Examples:
      python cli.py code-review --git-diff
      python cli.py code-review --git-ref HEAD~1 --output review.yaml
      python cli.py code-review --diff changes.patch --format markdown
      python cli.py code-review --git-diff --security-only
    """
    click.echo("Scenario 6: Code review pipeline")
    click.echo("=" * 80)

    # Determine what to review
    if git_diff or (not git_ref and not diff_file):
        git_ref_to_use = None
        source = "working directory changes"
    elif git_ref:
        git_ref_to_use = git_ref
        source = f"changes vs {git_ref}"
    elif diff_file:
        git_ref_to_use = None
        source = f"diff file: {diff_file}"
    else:
        click.echo("Error: Specify --git-diff, --git-ref, or --diff")
        return

    click.echo(f"Reviewing: {source}")
    click.echo()

    # Build config
    config = {
        "git_ref": git_ref_to_use,
        "diff_file": diff_file,
        "output_format": output_format,
        "output_file": output
    }

    # Security-only mode
    if security_only:
        config["quality_checks"] = []
        config["performance_checks"] = []
        click.echo("Mode: Security checks only")
    else:
        click.echo("Mode: Full review (security + quality + performance)")

    click.echo()

    # Run review
    try:
        result = scenario_6_code_review.run(config)

        # Display summary
        overall_summary = result.get("overall_summary", {})
        security_gate = result.get("security_gate_status", "N/A")
        security_reason = result.get("security_gate_reason", "")

        click.echo("Results:")
        click.echo("-" * 80)
        click.echo(f"Security Gate: {security_gate}")
        if security_reason:
            click.echo(f"Reason: {security_reason}")
        click.echo()

        click.echo(f"Total Issues: {overall_summary.get('total_issues', 0)}")
        click.echo(f"New Issues: {overall_summary.get('new_issues', 0)}")
        click.echo()

        # Category breakdown
        by_category = overall_summary.get("by_category", {})
        if any(by_category.values()):
            click.echo("By Category:")
            for category, count in by_category.items():
                if count > 0:
                    click.echo(f"  - {category.capitalize()}: {count}")
            click.echo()

        # Severity breakdown
        by_severity = overall_summary.get("by_severity", {})
        if any(by_severity.values()):
            click.echo("By Severity:")
            for severity in ["critical", "high", "medium", "low"]:
                count = by_severity.get(severity, 0)
                if count > 0:
                    click.echo(f"  - {severity.capitalize()}: {count}")
            click.echo()

        # Top findings
        all_findings = result.get("all_findings", [])
        if all_findings:
            click.echo("Top Issues:")
            for finding in all_findings[:5]:
                severity = finding["severity"].upper()
                file_path = finding["file"]
                line = finding["line"]
                message = finding["message"]
                click.echo(f"  [{severity}] {file_path}:{line}")
                click.echo(f"    {message}")
            if len(all_findings) > 5:
                click.echo(f"  ... and {len(all_findings) - 5} more issues")
            click.echo()

        # Output file
        if "output_file_path" in result:
            click.echo(f"Full report saved to: {result['output_file_path']}")
        elif not output:
            click.echo("-" * 80)
            click.echo(result.get("formatted_report", "No report generated"))

    except Exception as e:
        click.echo(f"Error during code review: {e}")
        import traceback
        traceback.print_exc()

    click.echo("=" * 80)


@cli.command()
@click.option('--repo', default=None, help='GitHub repository URL')
@click.option('--local-dir', default=None, help='Local directory path')
@click.option('--output', default='output', help='Output directory')
@click.option('--model', default='claude-3-haiku-20240307', help='LLM model')
@click.option('--language', type=click.Choice(['english', 'chinese']), default='english', help='Output language')
@click.option('--max-abstractions', default=10, help='Maximum number of abstractions to identify')
@click.option('--multi-file', is_flag=True, help='Generate multiple files (index.md + chapters) instead of single TUTORIAL.md')
@click.option('--include-pattern', multiple=True, help='File patterns to include (can specify multiple)')
@click.option('--exclude-pattern', multiple=True, help='File patterns to exclude (can specify multiple)')
def wiki(repo, local_dir, output, model, language, max_abstractions, multi_file, include_pattern, exclude_pattern):
    """Scenario 7: Codebase wiki generation

    Generate structured wiki documentation from codebase (GitHub repo or local directory)

    Examples:
      python cli.py wiki --repo https://github.com/The-Pocket/PocketFlow-Rust
      python cli.py wiki --local-dir ./my-project --language chinese
      python cli.py wiki --repo https://github.com/pallets/flask --max-abstractions 15
      python cli.py wiki --local-dir . --multi-file --output ./docs
    """
    click.echo("Scenario 7: Codebase wiki generation")
    click.echo("=" * 80)

    # Validate input
    if not repo and not local_dir:
        click.echo("Error: Either --repo or --local-dir must be specified")
        click.echo("\nExamples:")
        click.echo("  python cli.py wiki --repo https://github.com/The-Pocket/PocketFlow-Rust")
        click.echo("  python cli.py wiki --local-dir ./my-project")
        return

    if repo:
        click.echo(f"Source: GitHub repository - {repo}")
    else:
        click.echo(f"Source: Local directory - {local_dir}")

    click.echo(f"Language: {language.capitalize()}")
    click.echo(f"Max abstractions: {max_abstractions}")
    click.echo(f"Output mode: {'Multi-file' if multi_file else 'Single-file'}")
    click.echo()

    # Build config
    config = {
        'output_dir': output,
        'model': model,
        'language': language,
        'max_abstraction_num': max_abstractions,
        'single_file_output': not multi_file,
        'use_cache': True
    }

    if repo:
        config['repo_url'] = repo
    else:
        config['local_dir'] = local_dir

    # Add file patterns if specified
    if include_pattern:
        config['include_patterns'] = set(include_pattern)
    if exclude_pattern:
        config['exclude_patterns'] = set(exclude_pattern)

    # Run wiki generation
    try:
        click.echo("Starting wiki generation...")
        result = scenario_7_codebase_tutorial.run(config)

        if 'error' in result:
            click.echo(f"Error: {result['error']}")
            return

        # Display results
        click.echo("\nResults:")
        click.echo("-" * 80)
        click.echo(f"Project: {result.get('project_name', 'Unknown')}")
        click.echo(f"Files processed: {len(result.get('files', []))}")
        click.echo(f"Abstractions identified: {len(result.get('abstractions', []))}")
        click.echo(f"Chapters generated: {len(result.get('chapters', []))}")
        click.echo()

        # List abstractions
        abstractions = result.get('abstractions', [])
        if abstractions:
            click.echo("Identified abstractions:")
            for i, abstr in enumerate(abstractions, 1):
                click.echo(f"  {i}. {abstr.get('name', 'Unknown')}")
            click.echo()

        # Output location
        output_dir = result.get('final_output_dir')
        if output_dir:
            click.echo(f"Wiki generated successfully!")
            click.echo(f"Location: {output_dir}")

            if multi_file:
                click.echo(f"  - index.md (main index)")
                click.echo(f"  - Chapter files: {len(result.get('chapters', []))} files")
            else:
                click.echo(f"  - TUTORIAL.md (single file)")

    except Exception as e:
        click.echo(f"Error during wiki generation: {e}")
        import traceback
        traceback.print_exc()

    click.echo("=" * 80)


# Nodes command group
@cli.group(name='nodes')
def nodes():
    """Manage and discover nodes

    \b
    Examples:
      nodecraft nodes list                        # List all nodes
      nodecraft nodes list --namespace custom     # List custom nodes only
      nodecraft nodes show @common/get_files      # Show node details
      nodecraft nodes create --name my_analyzer   # Create new node
    """
    pass


@nodes.command(name='list')
@click.option('--namespace', default=None, help='Filter by namespace (common, custom, community)')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
def nodes_list(namespace, output_format):
    """List all available nodes"""
    from core.registry import node_registry

    # Auto-discover nodes
    try:
        node_registry.auto_discover()
    except Exception as e:
        click.echo(f"Error discovering nodes: {e}")
        return

    nodes_list_data = node_registry.list_nodes(namespace=namespace)

    if output_format == 'table':
        click.echo("\nAvailable Nodes:\n")
        click.echo(f"{'ID':<45} {'Namespace':<12} {'Description':<50}")
        click.echo("=" * 107)

        # Group by namespace
        by_namespace = {}
        for node in nodes_list_data:
            ns = node.get('namespace', 'unknown')
            if ns not in by_namespace:
                by_namespace[ns] = []
            by_namespace[ns].append(node)

        # Display by namespace
        for ns in sorted(by_namespace.keys()):
            click.echo(f"\n[{ns.upper()}]")
            for node in by_namespace[ns]:
                node_id_str = node.get('full_id', node.get('id', 'unknown'))
                desc = node.get('description', 'No description')
                # Truncate description if too long
                if len(desc) > 50:
                    desc = desc[:47] + "..."
                click.echo(f"  {node_id_str:<43} {ns:<12} {desc:<50}")

        click.echo(f"\n\nTotal: {len(nodes_list_data)} nodes")
        click.echo("\nRun 'nodecraft nodes show <node_id>' for details\n")

    elif output_format == 'json':
        import json
        click.echo(json.dumps(nodes_list_data, indent=2))

    elif output_format == 'yaml':
        try:
            import yaml
            click.echo(yaml.dump(nodes_list_data, default_flow_style=False, allow_unicode=True))
        except ImportError:
            click.echo("PyYAML not installed. Install with: pip install pyyaml")


@nodes.command(name='show')
@click.argument('node_id', required=True)
def nodes_show(node_id):
    """Show detailed information about a specific node"""
    from core.registry import node_registry

    # Auto-discover nodes
    try:
        node_registry.auto_discover()
    except Exception as e:
        click.echo(f"Error discovering nodes: {e}")
        return

    nodes_list_data = node_registry.list_nodes()
    node = next((n for n in nodes_list_data if n['full_id'] == node_id or n['id'] == node_id), None)

    if not node:
        click.echo(f"Node not found: {node_id}")
        click.echo(f"\nAvailable nodes: {', '.join([n['full_id'] for n in nodes_list_data[:5]])}...")
        click.echo("\nRun 'nodecraft nodes list' to see all nodes")
        return

    # Display detailed node information
    click.echo("\n" + "=" * 80)
    click.echo(f"Node: {node['full_id']}")
    click.echo("=" * 80)
    click.echo(f"\nID: {node.get('id', 'N/A')}")
    click.echo(f"Namespace: {node.get('namespace', 'N/A')}")
    click.echo(f"Type: {node.get('source_type', 'N/A')}")
    click.echo(f"Description: {node.get('description', 'N/A')}\n")

    # Source file
    source_file = node.get('source_file')
    if source_file:
        click.echo(f"Source: {source_file}\n")

    # Parameters
    params = node.get('params_schema', {})
    if params:
        click.echo("Parameters:")
        for param_name, param_info in params.items():
            param_type = param_info.get('type', 'any')
            default = param_info.get('default', 'N/A')
            desc = param_info.get('description', '')
            choices = param_info.get('choices')

            param_str = f"  --{param_name} ({param_type})"
            if choices:
                param_str += f" [choices: {', '.join(map(str, choices))}]"
            param_str += f" [default: {default}]"

            click.echo(param_str)
            if desc:
                click.echo(f"    {desc}")
        click.echo()

    # Input/Output keys
    input_keys = node.get('input_keys', [])
    output_keys = node.get('output_keys', [])

    if input_keys:
        click.echo(f"Input Keys (from context): {', '.join(input_keys)}")
    if output_keys:
        click.echo(f"Output Keys (to context): {', '.join(output_keys)}")

    click.echo("\n" + "=" * 80 + "\n")


@nodes.command(name='create')
@click.option('--name', required=True, help='Node name (e.g., my_analyzer)')
@click.option('--namespace', default='custom', help='Namespace [default: custom]')
@click.option('--type', 'node_type', default='function',
              type=click.Choice(['function', 'class']),
              help='Node type')
@click.option('--description', help='Node description [interactive if not provided]')
@click.option('--output-dir', help='Output directory [default: ~/.nodecraft/nodes/]')
@click.option('--dry-run', is_flag=True, help='Preview without creating files')
def nodes_create(name, namespace, node_type, description, output_dir, dry_run):
    """Create a new node from template

    \b
    Examples:
      nodecraft nodes create --name my_analyzer
      nodecraft nodes create --name api_caller --type class
    """
    from core.template_generator import NodeTemplateGenerator

    generator = NodeTemplateGenerator()

    # Show available templates
    click.echo("\nAvailable templates:")
    for tmpl_name, tmpl_desc in generator.list_templates().items():
        marker = " *" if tmpl_name == node_type else "  "
        click.echo(f"{marker} {tmpl_name}: {tmpl_desc}")
    click.echo()

    # Interactive prompt for description if not provided
    if not description:
        description = click.prompt('Node description', default='Custom node')

    # Dry run mode
    if dry_run:
        click.echo("Preview (--dry-run mode):")
        click.echo(f"  Would create node: {name}")
        click.echo(f"  Namespace: {namespace}")
        click.echo(f"  Type: {node_type}")
        click.echo(f"  Description: {description}")
        if output_dir:
            click.echo(f"  Output: {output_dir}/{name}.py")
        else:
            click.echo(f"  Output: ~/.nodecraft/nodes/{name}.py")
        return

    # Generate node file
    try:
        output_file = generator.generate(
            name=name,
            namespace=namespace,
            node_type=node_type,
            description=description,
            output_dir=output_dir
        )

        click.echo(f"Created: {output_file}")
        click.echo()
        click.echo("Next steps:")
        click.echo("  1. Edit the file to implement prep/exec/post logic")
        click.echo(f"  2. Test: nodecraft nodes show @{namespace}/{name}")
        click.echo(f"  3. Use in scenarios: @{namespace}/{name}")

    except FileExistsError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error creating node: {e}", err=True)
        raise click.Abort()


@nodes.command(name='register')
@click.argument('path', type=click.Path(exists=True))
@click.option('--namespace', default='custom', help='Default namespace [default: custom]')
@click.option('--recursive', is_flag=True, help='Recursively scan directory for nodes')
def nodes_register(path, namespace, recursive):
    """Register node(s) from file or directory

    \b
    Examples:
      nodecraft nodes register ./my_node.py
      nodecraft nodes register ./custom_nodes/ --recursive
    """
    from core import node_registry

    path_obj = Path(path)

    try:
        if path_obj.is_file():
            # Register single file
            registered = node_registry.register_from_file(str(path), namespace)
            click.echo(f"Registered {len(registered)} node(s) from {path}:")
            for node_id in registered:
                click.echo(f"  - {node_id}")
        elif path_obj.is_dir():
            # Register directory
            registered = node_registry.register_from_directory(str(path), namespace, recursive)
            if registered:
                click.echo(f"Registered {len(registered)} node(s) from {path}:")
                for node_id in registered:
                    click.echo(f"  - {node_id}")
            else:
                click.echo(f"No nodes found in {path}")
        else:
            click.echo(f"Error: Invalid path: {path}", err=True)
            raise click.Abort()

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error registering nodes: {e}", err=True)
        raise click.Abort()


@cli.command(name='scenarios')
@click.argument('action', type=click.Choice(['list', 'show', 'run', 'create', 'register']), default='list')
@click.argument('scenario_id', required=False)
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'yaml']), default='table', help='Output format')
@click.option('--params', type=str, help='Parameters as JSON string (for run action)')
@click.option('--with-context', is_flag=True, help='Inject RAG context before execution')
@click.option('--context-patterns', multiple=True, help='File patterns for context (e.g., **/*.py)')
@click.option('--context-query', type=str, help='Query to ask about the context')
@click.option('--name', help='Scenario name (for create action)')
@click.option('--template', type=click.Choice(['rag-query', 'file-process', 'analyze-report', 'gate-check', 'snapshot-restore', 'custom']), default='custom', help='Template type (for create action)')
@click.option('--description', help='Scenario description (for create action)')
@click.option('--output-dir', help='Output directory (for create action)')
@click.option('--dry-run', is_flag=True, help='Preview without creating files (for create action)')
@click.option('--recursive', is_flag=True, help='Recursively scan directory (for register action)')
def scenarios_cmd(action, scenario_id, output_format, params, with_context, context_patterns, context_query, name, template, description, output_dir, dry_run, recursive):
    """Manage and discover scenarios

    \b
    Examples:
      nodecraft scenarios list                    # List all scenarios
      nodecraft scenarios show simple_rag         # Show scenario details
      nodecraft scenarios run simple_rag --params '{"query": "What does this code do?"}'
    """
    from core import scenario_registry, node_registry

    # Auto-discover nodes and scenarios
    try:
        node_registry.auto_discover()

        # Add templates directory to scan
        try:
            import nodecraft
            templates_dir = Path(nodecraft.__file__).parent / "scenarios" / "templates"
        except (ImportError, AttributeError):
            # Package not installed, use relative path
            templates_dir = Path(__file__).parent / "scenarios" / "templates"

        scan_dirs = [str(templates_dir)] if templates_dir.exists() else []
        scenario_registry.auto_discover(additional_dirs=scan_dirs)
    except Exception as e:
        click.echo(f"Error discovering scenarios: {e}")
        import traceback
        traceback.print_exc()
        return

    if action == 'list':
        scenarios = scenario_registry.list_scenarios()

        if output_format == 'table':
            click.echo("\nAvailable Scenarios:\n")
            click.echo(f"{'ID':<20} {'Name':<30} {'Version':<10} {'Description':<40}")
            click.echo("=" * 100)

            for scenario in scenarios:
                sid = scenario.get('id', 'unknown')
                name = scenario.get('name', 'N/A')
                version = scenario.get('version', 'N/A')
                desc = scenario.get('description', 'No description')

                # Truncate if too long
                if len(name) > 30:
                    name = name[:27] + "..."
                if len(desc) > 40:
                    desc = desc[:37] + "..."

                click.echo(f"{sid:<20} {name:<30} {version:<10} {desc:<40}")

            click.echo(f"\n\nTotal: {len(scenarios)} scenarios")
            click.echo("\nRun 'nodecraft scenarios show <scenario_id>' for details")
            click.echo("Run 'nodecraft scenarios run <scenario_id> --params <json>' to execute\n")

        elif output_format == 'json':
            import json
            click.echo(json.dumps(scenarios, indent=2))

        elif output_format == 'yaml':
            try:
                import yaml
                click.echo(yaml.dump(scenarios, default_flow_style=False, allow_unicode=True))
            except ImportError:
                click.echo("PyYAML not installed. Install with: pip install pyyaml")

    elif action == 'show':
        if not scenario_id:
            click.echo("Error: scenario_id required for 'show' action")
            click.echo("\nExample: nodecraft scenarios show simple_rag")
            return

        scenarios = scenario_registry.list_scenarios()
        scenario = next((s for s in scenarios if s['id'] == scenario_id), None)

        if not scenario:
            click.echo(f"Scenario not found: {scenario_id}")
            click.echo(f"\nAvailable scenarios: {', '.join([s['id'] for s in scenarios])}")
            click.echo("\nRun 'nodecraft scenarios list' to see all scenarios")
            return

        # Display detailed scenario information
        click.echo("\n" + "=" * 80)
        click.echo(f"Scenario: {scenario['name']}")
        click.echo("=" * 80)
        click.echo(f"\nID: {scenario.get('id', 'N/A')}")
        click.echo(f"Version: {scenario.get('version', 'N/A')}")
        click.echo(f"Author: {scenario.get('author', 'N/A')}")
        click.echo(f"Description: {scenario.get('description', 'N/A')}\n")

        # Source
        source = scenario.get('source')
        if source:
            click.echo(f"Source: {source}\n")

        # Parameters
        parameters = scenario.get('parameters', {})
        if parameters:
            click.echo("Parameters:")
            for param_name, param_def in parameters.items():
                param_type = param_def.get('type', 'str')
                default = param_def.get('default', 'N/A')
                desc = param_def.get('description', '')
                required = param_def.get('required', False)

                req_str = "[REQUIRED]" if required else f"[default: {default}]"
                click.echo(f"  --{param_name} ({param_type}) {req_str}")
                if desc:
                    click.echo(f"    {desc}")
            click.echo()

        # Steps
        try:
            scenario_def = scenario_registry.get_scenario(scenario_id)
            steps = scenario_def.get('steps', [])
            if steps:
                click.echo(f"Steps ({len(steps)} total):")
                for i, step in enumerate(steps, 1):
                    step_name = step.get('name', 'unnamed')
                    node_id = step.get('node', 'unknown')
                    condition = step.get('condition')

                    step_str = f"  {i}. {step_name} ({node_id})"
                    if condition:
                        step_str += f" [conditional: {condition}]"
                    click.echo(step_str)
                click.echo()
        except Exception as e:
            click.echo(f"Error loading scenario steps: {e}\n")

        click.echo("=" * 80)
        click.echo(f"\nUsage: nodecraft scenarios run {scenario_id} --params '<json>'\n")

    elif action == 'run':
        if not scenario_id:
            click.echo("Error: scenario_id required for 'run' action")
            click.echo("\nExample: nodecraft scenarios run simple_rag --params '{\"query\": \"test\"}'")
            return

        # Parse parameters
        user_params = {}
        if params:
            try:
                import json
                user_params = json.loads(params)
            except json.JSONDecodeError as e:
                click.echo(f"Error parsing parameters JSON: {e}")
                return

        # Run scenario
        try:
            click.echo(f"Running scenario: {scenario_id}")
            click.echo(f"Parameters: {user_params}")

            # Check for context injection
            if with_context:
                click.echo("Context injection: ENABLED")
                if context_patterns:
                    click.echo(f"Context patterns: {', '.join(context_patterns)}")
                if context_query:
                    click.echo(f"Context query: {context_query}")
                click.echo()

                # Use context injection
                from core.context_integration import inject_context_to_scenario_run

                context_config = {
                    "enabled": True,
                    "patterns": list(context_patterns) if context_patterns else None,
                    "query": context_query
                }

                result = inject_context_to_scenario_run(
                    scenario_registry,
                    scenario_id,
                    user_params,
                    context_config=context_config
                )
            else:
                click.echo()
                result = scenario_registry.run_scenario(scenario_id, user_params)

            click.echo("\nScenario completed successfully!")
            click.echo("\nResults:")
            click.echo("-" * 80)

            # Display key results
            for key, value in result.items():
                if key.startswith("_"):
                    continue
                if isinstance(value, (str, int, float, bool)):
                    click.echo(f"{key}: {value}")
                elif isinstance(value, list):
                    click.echo(f"{key}: {len(value)} items")

            # Display LLM response if present
            if "llm_response" in result:
                click.echo("\nLLM Response:")
                click.echo("-" * 80)
                click.echo(result["llm_response"])

        except Exception as e:
            click.echo(f"Error running scenario: {e}")
            import traceback
            traceback.print_exc()

    elif action == 'create':
        from core.template_generator import ScenarioTemplateGenerator

        # Name is required for create
        if not name:
            click.echo("Error: --name is required for create action")
            click.echo("\nExample: nodecraft scenarios create --name my_workflow --template rag-query")
            return

        generator = ScenarioTemplateGenerator()

        # Show available templates
        click.echo("\nAvailable templates:")
        for tmpl_name, tmpl_desc in generator.list_templates().items():
            marker = " *" if tmpl_name == template else "  "
            click.echo(f"{marker} {tmpl_name}: {tmpl_desc}")
        click.echo()

        # Interactive prompt for description if not provided
        if not description:
            description = click.prompt('Scenario description', default='Custom workflow')

        # Dry run mode
        if dry_run:
            click.echo("Preview (--dry-run mode):")
            click.echo(f"  Would create scenario: {name}")
            click.echo(f"  Template: {template}")
            click.echo(f"  Description: {description}")
            if output_dir:
                click.echo(f"  Output: {output_dir}/{name}.yaml")
            else:
                click.echo(f"  Output: ~/.nodecraft/scenarios/{name}.yaml")
            return

        # Generate scenario file
        try:
            output_file = generator.generate(
                name=name,
                template=template,
                description=description,
                output_dir=output_dir
            )

            click.echo(f"Created: {output_file}")
            click.echo()
            click.echo("Next steps:")
            click.echo("  1. Edit the YAML to customize workflow steps")
            click.echo(f"  2. Test: nodecraft scenarios show {name}")
            click.echo(f"  3. Run: nodecraft {name} [OPTIONS]")

        except FileExistsError as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()
        except Exception as e:
            click.echo(f"Error creating scenario: {e}", err=True)
            raise click.Abort()

    elif action == 'register':
        from core import scenario_registry

        # Path is passed via scenario_id argument for register action
        if not scenario_id:
            click.echo("Error: Path is required for register action")
            click.echo("\nExamples:")
            click.echo("  nodecraft scenarios register ./my_scenario.yaml")
            click.echo("  nodecraft scenarios register ./custom_scenarios/ --recursive")
            return

        path = scenario_id
        path_obj = Path(path)

        if not path_obj.exists():
            click.echo(f"Error: Path not found: {path}", err=True)
            raise click.Abort()

        try:
            if path_obj.is_file():
                # Register single file
                scenario_registry.register_scenario_from_yaml(path_obj)

                # Get scenario ID from the file to show confirmation
                import yaml
                with open(path_obj) as f:
                    scenario_def = yaml.safe_load(f)
                    scenario_id_from_file = scenario_def.get('scenario', {}).get('id', path_obj.stem)

                click.echo(f"Registered scenario from {path}:")
                click.echo(f"  - {scenario_id_from_file}")
            elif path_obj.is_dir():
                # Register directory with optional recursive flag
                registered = scenario_registry.register_from_directory(str(path), recursive)
                if registered:
                    click.echo(f"Registered {len(registered)} scenario(s) from {path}:")
                    for sid in registered:
                        click.echo(f"  - {sid}")
                else:
                    click.echo(f"No scenarios found in {path}")
            else:
                click.echo(f"Error: Invalid path: {path}", err=True)
                raise click.Abort()

        except FileNotFoundError as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()
        except Exception as e:
            click.echo(f"Error registering scenarios: {e}", err=True)
            raise click.Abort()


# Register dynamic commands from scenarios
def _register_dynamic_scenario_commands():
    """Register dynamic CLI commands from YAML scenarios"""
    try:
        from core.dynamic_cli import register_dynamic_commands
        from core import node_registry, scenario_registry

        register_dynamic_commands(cli, scenario_registry, node_registry)
    except Exception as e:
        import warnings
        warnings.warn(f"Failed to register dynamic scenario commands: {e}")


# Call registration before running CLI
_register_dynamic_scenario_commands()


if __name__ == '__main__':
    cli()
