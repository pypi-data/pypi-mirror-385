# outcomeForge

A modular framework to forge and verify intelligent outcomes.

## Features
- Clear separation between Common and Custom Nodes
- Truly pluggable Scenario system
- 7 core scenarios: Snapshot, Adaptation, Regression, Architecture Drift, Local RAG, Code Review, Wiki Generation
- LLM-powered analysis (Anthropic Claude, OpenAI)
- Support for parallel/async execution
- Structured output with YAML metadata
- Complete Pass to Fail to Pass verification cycles
- Lightweight RAG with files-to-prompt integration
- Code review with security, quality, and performance checks
- Codebase wiki generation with smart abstraction identification

## Quick Start

### Installation

#### Option 1: pip install (Recommended)

```bash
# Install from source
git clone https://github.com/yourusername/outcomeforge.git
cd outcomeforge
pip install -e .

# Or install directly (once published to PyPI)
pip install outcomeforge

# Set up your API key (REQUIRED - no mock mode)
export ANTHROPIC_API_KEY="your-api-key-here"
```

After installation, you can use the `outcomeforge` command globally:
```bash
outcomeforge --help
outcomeforge snapshot --patterns "**/*.py"
outcomeforge wiki --local-dir ./my-project
```

#### Option 2: Manual installation (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/outcomeforge.git
cd outcomeforge

# Install dependencies
pip install -r requirements.txt

# Set up your API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Use cli.py directly
python cli.py --help
```

**IMPORTANT**: This system requires a real API key to function. Mock mode has been removed to ensure all AI interactions are genuine. You must configure at least one API key before using any scenario.

### Verify API Configuration

Before running scenarios, verify your API setup:

```bash
# Check API configuration and test connectivity
python check_api_config.py
```

This tool will:
- Check if API keys are set
- Verify required packages are installed
- Test actual API connectivity
- Provide clear error messages if something is wrong

### One-Click Verification

Run all four scenarios with complete Pass ↔ Fail ↔ Pass cycles:

```bash
bash examples/run_all_scenarios.sh
```

This will:
-  Verify all four scenarios end-to-end
-  Generate structured outputs (JSON + YAML + MD)

### Try Local RAG

Quick start with the lightweight RAG feature:

```bash
# Ask questions about the codebase
python cli.py rag --patterns "**/*.py" --query "How does this project work?" --cxml

# Generate documentation from tests
python cli.py rag --patterns "tests/**/*.py" --query "Generate API documentation" --format markdown

# Locate features
python cli.py rag --query "Where is the snapshot functionality implemented?" --line-numbers
```

### Try Code Review (New!)

Quick start with the new code review feature:

```bash
# Review current changes
python cli.py code-review --git-diff

# Review against specific commit
python cli.py code-review --git-ref HEAD~1 --output review.yaml

# Security-only scan
python cli.py code-review --git-diff --security-only
```

## Seven Core Scenarios

### Scenario 1 - Local Snapshot and Rollback (no GitHub dependency)

**Purpose**: Create AI-powered code snapshots and restore files byte-for-byte

#### Features
- File content + hash snapshot (SHA-256)
- LLM-powered code health analysis
- Byte-for-byte restoration with hash verification
- **Complete cycle**: Create → Modify → Snapshot → Rollback → Verify

#### Commands
```bash
# Create snapshot
python cli.py snapshot --patterns "**/*.py" --model "claude-3-haiku-20240307"

# List snapshots
python cli.py snapshot-list

# Restore from snapshot
python cli.py snapshot-restore 20250118_120000
```

#### Demo Script
```bash
bash examples/demo_scenario1_snapshot_rollback.sh
```

**Verification Points**:
-  Creates snapshot with file contents and hashes
-  LLM generates code health report
-  Modifies files and creates second snapshot
-  Restores from first snapshot
-  Hash verification passes (byte-for-byte match)

**Output Files**:
- `.ai-snapshots/snapshot-{timestamp}.json` - Full snapshot with file contents
- `.ai-snapshots/snapshot-{timestamp}.md` - LLM analysis report

---

### Scenario 2 - Open-source Repository Understanding and Adaptation

**Purpose**: Analyze open-source projects and generate organization-compliant adaptation plans

#### Features
- Clone and analyze real GitHub repositories
- Detect organization standard violations
- Generate executable YAML plans
- 10-point repository understanding

#### Commands
```bash
python cli.py adapt "https://github.com/pallets/click" --model "claude-3-haiku-20240307"
```

**Verification Points**:
-  Clones real repository (Click project)
-  Generates 10 understanding points
-  Detects rule violations
-  Creates executable `plan` YAML with steps

**Output Files**:
- `.ai-snapshots/repo_adapt_plan-{timestamp}.md`

---

### Scenario 3 - Regression Detection with Diff Analysis

**Purpose**: AI-powered quality gate decisions based on test metrics

#### Features
- Collects test pass rate, coverage, lint metrics
- LLM evaluates PASS/FAIL with reasoning
- **Complete cycle**: Baseline PASS → Inject Failure → FAIL → Fix → PASS

#### Commands
```bash
python cli.py regression --baseline "HEAD~1" --build "HEAD" --model "claude-3-haiku-20240307"
```

#### Demo Script
```bash
bash examples/demo_scenario3_regression_cycle.sh
```

**Verification Points**:
-  Baseline test returns PASS
-  Simulates failure injection
-  After fix returns PASS
-  Generates `gate` YAML with reasons and actions

**Output Files**:
- `.ai-snapshots/regression_gate-{timestamp}.md`

---

### Scenario 4 - Architecture Drift and Impact Scanning

**Purpose**: Detect architecture violations and structural drift

#### Features
- Dependency graph analysis
- Layer violation detection
- Complexity metrics tracking
- **Complete cycle**: Baseline PASS → Inject Drift → FAIL → Fix → PASS

#### Commands
```bash
python cli.py arch-drift --model "claude-3-haiku-20240307"
```

#### Demo Script
```bash
bash examples/demo_scenario4_arch_drift_cycle.sh
```

**Verification Points**:
-  Baseline returns PASS with score (e.g., 90/100)
-  Simulates architecture drift
-  After fix returns PASS
-  Generates `arch_gate` YAML with score and pass/fail

**Output Files**:
- `.ai-snapshots/arch_gate-{timestamp}.md`

---

### Scenario 5 - Local Lightweight RAG (Files-to-Prompt)

**Purpose**: Lightweight RAG for quick codebase understanding and Q&A

Inspired by [Simon Willison's files-to-prompt](https://github.com/simonw/files-to-prompt), this scenario formats code files into LLM-friendly prompts for rapid codebase analysis.

#### Features
- Quick project onboarding (seconds to understand architecture)
- Auto-generate documentation from tests/source
- Code navigation ("Where is JWT validation?")
- Optimized for long-context models (Claude XML format)

#### Commands
```bash
# Quick overview
python cli.py rag --patterns "**/*.py" --query "How does this project work?" --cxml

# Generate docs from tests
python cli.py rag --patterns "tests/**/*.py" --query "Generate API documentation" --format markdown

# Locate features with line numbers
python cli.py rag --query "Where is snapshot implemented?" --line-numbers

# Code review
python cli.py rag --patterns "nodes/**/*.py" --query "Review code quality"
```

#### Demo Script
```bash
bash examples/demo_scenario5_local_rag.sh
```

#### Use Cases
1. **Project Onboarding**: "What's the architecture? What are the core modules?"
2. **Documentation Generation**: Extract API docs from test cases
3. **Feature Location**: "Where is JWT validation implemented?"
4. **Code Review**: Quality analysis with specific focus areas

#### Format Options
- `--format xml`: Standard XML output
- `--format xml --cxml`: Compact XML (recommended for long context)
- `--format markdown`: Markdown code blocks
- `--line-numbers`: Include line numbers for precise location

**Output**: Direct LLM response to terminal (no files saved)

**Documentation**: See `docs/scenario_5_rag_usage.md` for detailed usage

---

### Scenario 6 - Code Review Pipeline (Security, Quality, Performance)

**Purpose**: Comprehensive code review for security, quality, and performance

Integrates CodeReviewAgent capabilities with modular review nodes for detecting issues across multiple categories.

#### Features
- **Security Review**: SQL injection, hardcoded secrets, command injection, path traversal, unsafe deserialization, weak cryptography
- **Quality Review**: Magic numbers, deep nesting, long functions, print statements, broad exceptions, missing docstrings
- **Performance Review**: Nested loops (O(n²)), string concatenation in loops, N+1 queries, loading all data
- **Flexible Execution**: Run all checks or individual categories (security-only mode)
- **Multiple Output Formats**: YAML, JSON, Markdown
- **Security Gate**: Auto-fail on critical issues

#### Commands
```bash
# Full review of working directory changes
python cli.py code-review --git-diff

# Review specific commit
python cli.py code-review --git-ref HEAD~1 --output review.yaml

# Review a diff file
python cli.py code-review --diff changes.patch --format markdown

# Security-only scan
python cli.py code-review --git-diff --security-only
```

#### Demo Script
```bash
bash examples/demo_scenario6_code_review.sh
```

---

### Scenario 7 - Codebase Wiki Generation

**Purpose**: Generate structured wiki documentation from any codebase (GitHub or local)

Automatically analyze your codebase, identify core abstractions, understand their relationships, and generate beginner-friendly wiki documentation with intelligent chapter ordering.

#### Features
- **Smart Abstraction Identification**: Uses LLM to identify 5-15 core concepts in your codebase
- **Relationship Analysis**: Understands how abstractions relate to each other
- **Intelligent Chapter Ordering**: Orders tutorial chapters based on dependencies for optimal learning
- **Batch Processing**: Automatically handles large repositories with token limit management
- **Multi-language Support**: Generate wikis in English or Chinese
- **LLM Caching**: Resume from checkpoints when processing large repos
- **Dual Output Modes**: Single TUTORIAL.md file or multi-file format (index + chapters)
- **Source Flexibility**: Works with GitHub repos or local directories

#### Commands
```bash
# Generate wiki from GitHub repository
python cli.py wiki --repo https://github.com/The-Pocket/PocketFlow-Rust

# Generate wiki from local directory
python cli.py wiki --local-dir ./my-project

# Chinese language output
python cli.py wiki --local-dir . --language chinese

# Custom abstraction limit
python cli.py wiki --repo https://github.com/pallets/flask --max-abstractions 15

# Multi-file output (index.md + chapter files)
python cli.py wiki --local-dir . --multi-file --output ./docs

# With custom file patterns
python cli.py wiki --repo https://github.com/example/repo \
  --include-pattern "*.rs" --include-pattern "*.md" \
  --exclude-pattern "**/tests/*"
```

#### Workflow
1. **Fetch Files**: Crawl GitHub repo or local directory
2. **Identify Abstractions**: LLM analyzes code structure and extracts core concepts
3. **Analyze Relationships**: Understand dependencies between abstractions
4. **Order Chapters**: Smart ordering based on learning progression
5. **Write Chapters**: Generate detailed chapter for each abstraction
6. **Combine Wiki**: Merge into final TUTORIAL.md with table of contents and Mermaid diagrams

#### Output Structure

**Single-file mode** (default):
```
output/ProjectName/
└── TUTORIAL.md    # Complete wiki with all chapters
```

**Multi-file mode** (`--multi-file`):
```
output/ProjectName/
├── index.md                 # Main index with Mermaid diagram
├── 01_concept_name.md      # Chapter 1
├── 02_another_concept.md   # Chapter 2
└── ...                     # More chapters
```

#### Example Output

The generated wiki includes:
- **Project Overview**: Summary of what the project does
- **Mermaid Diagram**: Visual representation of abstraction relationships
- **Chapter List**: Intelligently ordered learning path
- **Detailed Chapters**: Beginner-friendly explanations with code examples
- **Cross-references**: Links between related concepts

#### Advanced Options
- `--model`: Choose LLM model (default: claude-3-haiku-20240307)
- `--max-abstractions`: Limit number of concepts (default: 10)
- `--output`: Custom output directory (default: ./output)
- `--include-pattern`: File patterns to include (can specify multiple)
- `--exclude-pattern`: File patterns to exclude (can specify multiple)

#### Demo Script
```bash
bash examples/demo_scenario7_wiki_generation.sh
```

**Verification Points**:
- Fetches and analyzes repository files
- Identifies core abstractions (concepts, classes, modules)
- Generates relationship graph
- Creates ordered learning path
- Produces comprehensive TUTORIAL.md

**Example Repositories Tested**:
- [PocketFlow-Rust](https://github.com/The-Pocket/PocketFlow-Rust) - Rust flow framework (32 files, 5 abstractions)
- Custom Python projects
- Multi-language repositories

**Documentation**: See `SCENARIO_7_INTEGRATION.md` and `SCENARIO_7_SUCCESS_SUMMARY.md` for implementation details

---

## CLI Commands

### Snapshot Commands
```bash
# Create snapshot
python cli.py snapshot --patterns "**/*.py" --model "claude-3-haiku-20240307"

# List all snapshots
python cli.py snapshot-list

# Restore from snapshot (with hash verification)
python cli.py snapshot-restore <snapshot-id>
```

### Analysis Commands
```bash
# Repository adaptation
python cli.py adapt "https://github.com/pallets/click" --model "claude-3-haiku-20240307"

# Regression detection
python cli.py regression --baseline "HEAD~1" --build "HEAD" --model "claude-3-haiku-20240307"

# Architecture drift
python cli.py arch-drift --model "claude-3-haiku-20240307"
```

### RAG Commands
```bash
# Quick project overview
python cli.py rag --patterns "**/*.py" --query "How does this project work?" --cxml

# Generate documentation from tests
python cli.py rag --patterns "tests/**/*.py" --query "Generate API documentation" --format markdown

# Locate feature implementation
python cli.py rag --query "Where is snapshot functionality implemented?" --line-numbers

# Multiple patterns
python cli.py rag --patterns "**/*.py" --patterns "**/*.md" --query "Summarize the project"

# Code review
python cli.py rag --patterns "nodes/**/*.py" --query "Review error handling and code reuse"
```

### Code Review Commands (New!)
```bash
# Review current working directory changes
python cli.py code-review --git-diff

# Review against specific commit
python cli.py code-review --git-ref HEAD~1 --output review.yaml

# Review a diff/patch file
python cli.py code-review --diff changes.patch --format markdown

# Security-only scan (fast)
python cli.py code-review --git-diff --security-only

# Full review with JSON output
python cli.py code-review --git-ref main --format json --output report.json
```

### Wiki Generation Commands (New!)
```bash
# Generate wiki from GitHub repository
python cli.py wiki --repo https://github.com/The-Pocket/PocketFlow-Rust

# Generate wiki from local directory
python cli.py wiki --local-dir ./my-project

# Chinese language wiki
python cli.py wiki --local-dir . --language chinese --output ./docs_cn

# Multi-file output mode
python cli.py wiki --local-dir . --multi-file --output ./wiki

# Custom abstraction limit and patterns
python cli.py wiki --repo https://github.com/example/project \
  --max-abstractions 15 \
  --include-pattern "*.py" --include-pattern "*.md" \
  --exclude-pattern "**/tests/*"
```

## How It Works

### Flow/Node Architecture
Each scenario is a **Flow** composed of **Nodes**:
```python
def create_local_snapshot_scenario(config):
    f = flow()
    f.add(get_files_node(), name="get_files")
    f.add(parse_code_node(), name="parse_code")
    f.add(snapshot_files_node(), name="snapshot_files")  # Saves file contents + hashes
    f.add(call_llm_node(), name="llm_snapshot", params={
        "prompt_file": "prompts/snapshot.prompt.md",
        "model": config.get("model", "gpt-4"),
    })
    f.add(save_snapshot_node(), name="save_snapshot")  # Saves JSON + MD
    return f
```

### Three-Phase Node Execution
Each node has three phases:
1. **prep**: Prepare parameters from context
2. **exec**: Execute the operation
3. **post**: Update context and determine next state

### Example: Local RAG Flow
```python
from engine import flow
from nodes.common import get_files_node, files_to_prompt_node, call_llm_node

def create_rag_scenario(config):
    f = flow()

    # Step 1: Get files matching patterns
    f.add(get_files_node(), name="get_files", params={
        "patterns": config.get("patterns", ["**/*.py"])
    })

    # Step 2: Format files for LLM (files-to-prompt style)
    f.add(files_to_prompt_node(), name="format", params={
        "format": "xml",
        "cxml": True,  # Compact XML for long context
        "include_line_numbers": False
    })

    # Step 3: Query LLM
    f.add(call_llm_node(), name="query", params={
        "prompt_file": "prompts/rag_query.prompt.md",
        "model": "claude-3-haiku-20240307"
    })

    return f

# Run the flow
result = create_rag_scenario(config).run({
    "project_root": ".",
    "query": "How does this work?"
})
print(result.get("llm_response"))
```

## Requirements

- Python 3.7+
- anthropic (for Claude API)
- openai (for OpenAI API)
- click (for CLI)
- pyyaml (for config parsing)
- gitpython (for git operations)


## Contributing

Contributions welcome! Areas for improvement:
- Additional language support beyond Python
- LLM-powered semantic review for Scenario 6
- CI/CD pipeline integration (GitHub Actions, GitLab CI)
- Custom reporting formats and templates
- More review patterns and rules
- Integration with issue trackers

## License

MIT

