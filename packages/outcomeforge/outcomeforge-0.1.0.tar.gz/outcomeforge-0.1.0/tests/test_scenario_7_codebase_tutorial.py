"""
测试场景⑦：代码库教程生成

真实测试用例 - 使用PocketFlow-Rust仓库
"""

import pytest
import os
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scenarios import scenario_7_codebase_tutorial


@pytest.fixture(scope="session")
def check_api_key():
    """Check if API key is set"""
    has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
    has_openai = bool(os.getenv('OPENAI_API_KEY'))

    if not (has_anthropic or has_openai):
        pytest.skip(
            "No API keys found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY to run these tests."
        )

    return {
        "has_anthropic": has_anthropic,
        "has_openai": has_openai,
        "preferred_model": "claude-3-haiku-20240307" if has_anthropic else "gpt-4"
    }


class TestScenario7CodebaseTutorial:
    """Test codebase tutorial generation with real LLM"""

    def test_github_repo_tutorial_generation(self, check_api_key):
        """Test generating tutorial from GitHub repository (PocketFlow-Rust)"""
        config = {
            "repo_url": "https://github.com/The-Pocket/PocketFlow-Rust",
            "model": check_api_key["preferred_model"],
            "language": "english",
            "output_dir": "/tmp/tutorial_output",
            "max_abstraction_num": 5,  # Limit to 5 for faster testing
            "include_patterns": {"*.rs", "*.md", "Cargo.toml"},
            "exclude_patterns": {"**/target/*", "**/tests/*", "**/.git/*"},
            "max_file_size": 50000,  # 50KB limit for testing
            "use_cache": True
        }

        result = scenario_7_codebase_tutorial.run(config)

        # Verify tutorial was generated
        assert "error" not in result, f"Tutorial generation failed: {result.get('error')}"
        assert "final_output_dir" in result, "Output directory not in result"
        assert "project_name" in result, "Project name not in result"

        output_dir = Path(result["final_output_dir"])
        assert output_dir.exists(), f"Output directory should exist: {output_dir}"

        # Verify tutorial file exists
        tutorial_file = output_dir / "TUTORIAL.md"
        assert tutorial_file.exists(), f"Tutorial file should exist: {tutorial_file}"

        # Verify tutorial content
        tutorial_content = tutorial_file.read_text()
        assert len(tutorial_content) > 1000, "Tutorial should have substantial content"
        assert "PocketFlow" in tutorial_content or "Rust" in tutorial_content, \
            "Tutorial should mention the project"

        print(f"\n✓ Tutorial generated successfully!")
        print(f"  - Output dir: {output_dir}")
        print(f"  - Tutorial length: {len(tutorial_content)} chars")
        print(f"  - Abstractions: {len(result.get('abstractions', []))}")

    def test_local_directory_tutorial(self, check_api_key, tmp_path):
        """Test generating tutorial from local directory"""
        # Create a small test directory
        test_dir = tmp_path / "test_project"
        test_dir.mkdir()

        # Create some Python files
        (test_dir / "main.py").write_text("""
class Calculator:
    '''Simple calculator class'''
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
""")

        (test_dir / "utils.py").write_text("""
def validate_number(n):
    '''Validate that input is a number'''
    if not isinstance(n, (int, float)):
        raise ValueError("Input must be a number")
    return True
""")

        (test_dir / "README.md").write_text("""
# Test Project
A simple calculator project for testing.
""")

        config = {
            "local_dir": str(test_dir),
            "project_name": "TestCalculator",
            "model": check_api_key["preferred_model"],
            "language": "english",
            "output_dir": str(tmp_path / "output"),
            "max_abstraction_num": 3,
            "include_patterns": {"*.py", "*.md"},
            "max_file_size": 10000,
            "use_cache": False  # Disable cache for test
        }

        result = scenario_7_codebase_tutorial.run(config)

        # Verify results
        assert "error" not in result
        assert "final_output_dir" in result

        output_dir = Path(result["final_output_dir"])
        tutorial_file = output_dir / "TUTORIAL.md"

        assert tutorial_file.exists()
        tutorial_content = tutorial_file.read_text()
        assert "Calculator" in tutorial_content or "calculator" in tutorial_content

    def test_error_handling_no_source(self):
        """Test error handling when neither repo_url nor local_dir is provided"""
        config = {}

        result = scenario_7_codebase_tutorial.run(config)

        assert "error" in result
        assert "repo_url" in result["error"] or "local_dir" in result["error"]

    def test_multilanguage_support(self, check_api_key, tmp_path):
        """Test Chinese language tutorial generation"""
        # Create a simple test directory
        test_dir = tmp_path / "中文测试"
        test_dir.mkdir()

        (test_dir / "hello.py").write_text("""
def greet(name):
    '''Greet someone'''
    return f"Hello, {name}!"
""")

        config = {
            "local_dir": str(test_dir),
            "model": check_api_key["preferred_model"],
            "language": "chinese",  # Test Chinese output
            "output_dir": str(tmp_path / "中文输出"),
            "max_abstraction_num": 2,
            "include_patterns": {"*.py"},
            "use_cache": False
        }

        result = scenario_7_codebase_tutorial.run(config)

        assert "error" not in result
        output_dir = Path(result["final_output_dir"])
        tutorial_file = output_dir / "TUTORIAL.md"

        assert tutorial_file.exists()
        # Chinese content check would need proper encoding handling


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
