"""
outcomeForge CLI - A modular framework to forge and verify intelligent outcomes.

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

@click.group(cls=NaturalOrderGroup)
def cli():
    """outcomeForge - A modular framework to forge and verify intelligent outcomes.

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
    pass


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


if __name__ == '__main__':
    cli()
