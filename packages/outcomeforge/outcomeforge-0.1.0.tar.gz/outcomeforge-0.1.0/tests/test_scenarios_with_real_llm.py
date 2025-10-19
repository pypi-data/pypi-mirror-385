"""
Comprehensive test suite for all scenarios with REAL LLM interaction

Tests:
1. Scenario 1: Snapshot creation, listing, and restoration
2. Scenario 2: Repository adaptation planning
3. Scenario 3: Regression detection
4. Scenario 4: Architecture drift detection
5. Scenario 5: RAG queries
6. Scenario 6: Code review

Each test requires ANTHROPIC_API_KEY or OPENAI_API_KEY to be set.
Tests verify actual LLM interaction and proper error handling.
"""

import pytest
import os
import json
import hashlib
from pathlib import Path
import shutil
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scenarios import (
    scenario_1_local_snapshot,
    scenario_2_repo_adapt,
    scenario_3_regression,
    scenario_4_arch_drift,
    scenario_5_local_rag,
    scenario_6_code_review
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def check_api_key():
    """Check if at least one API key is set"""
    has_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
    has_openai = bool(os.getenv('OPENAI_API_KEY'))

    if not (has_anthropic or has_openai):
        pytest.skip(
            "No API keys found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY to run these tests.\n"
            "Example: export ANTHROPIC_API_KEY='your-key-here'"
        )

    return {
        "has_anthropic": has_anthropic,
        "has_openai": has_openai,
        "preferred_model": "claude-3-haiku-20240307" if has_anthropic else "gpt-3.5-turbo"
    }


@pytest.fixture
def cleanup_snapshots():
    """Clean up test snapshots before and after tests"""
    snapshots_dir = Path(".ai-snapshots")

    # Clean up before test
    if snapshots_dir.exists():
        for f in snapshots_dir.glob("test-snapshot-*.json"):
            f.unlink()
        for f in snapshots_dir.glob("test-snapshot-*.md"):
            f.unlink()

    yield

    # Clean up after test
    if snapshots_dir.exists():
        for f in snapshots_dir.glob("test-snapshot-*.json"):
            f.unlink()
        for f in snapshots_dir.glob("test-snapshot-*.md"):
            f.unlink()


@pytest.fixture
def temp_test_file():
    """Create a temporary test file"""
    test_file = Path("test_temp_file.py")
    test_content = '''"""
Test module for snapshot testing
"""

def hello():
    """Say hello"""
    return "Hello, World!"

class Calculator:
    """Simple calculator"""

    def add(self, a, b):
        """Add two numbers"""
        return a + b

    def subtract(self, a, b):
        """Subtract two numbers"""
        return a - b
'''
    test_file.write_text(test_content)

    yield test_file

    # Clean up
    if test_file.exists():
        test_file.unlink()


# ============================================================================
# Scenario 1: Local Snapshot & Rollback Tests
# ============================================================================

class TestScenario1Snapshot:
    """Test snapshot creation, listing, and restoration"""

    def test_create_snapshot(self, check_api_key, cleanup_snapshots):
        """Test creating a snapshot with real LLM"""
        config = {
            "file_patterns": ["tests/**/*.py"],
            "model": check_api_key["preferred_model"]
        }

        result = scenario_1_local_snapshot.run(config)

        # Verify snapshot was created
        assert "snapshot_id" in result, "Snapshot ID should be in result"
        assert "llm_response" in result, "LLM response should be in result"

        snapshot_id = result["snapshot_id"]
        assert snapshot_id, "Snapshot ID should not be empty"

        # Verify files exist
        snapshot_file = Path(f".ai-snapshots/snapshot-{snapshot_id}.json")
        md_file = Path(f".ai-snapshots/snapshot-{snapshot_id}.md")

        assert snapshot_file.exists(), f"Snapshot JSON should exist: {snapshot_file}"
        assert md_file.exists(), f"Snapshot MD should exist: {md_file}"

        # Verify JSON structure
        with open(snapshot_file) as f:
            snapshot_data = json.load(f)

        assert "files" in snapshot_data, "Snapshot should contain files"
        assert "llm_analysis" in snapshot_data, "Snapshot should contain LLM analysis"
        assert len(snapshot_data["llm_analysis"]) > 0, "LLM analysis should not be empty"

        # Verify MD file has content
        md_content = md_file.read_text()
        assert len(md_content) > 100, "MD file should have substantial content"
        assert "snapshot_meta" in md_content.lower() or "meta" in md_content.lower(), \
            "MD should contain metadata section"

    def test_snapshot_with_file_hash_verification(self, check_api_key, temp_test_file):
        """Test that snapshot correctly stores file hashes"""
        config = {
            "file_patterns": [str(temp_test_file)],
            "model": check_api_key["preferred_model"]
        }

        result = scenario_1_local_snapshot.run(config)
        snapshot_id = result["snapshot_id"]

        # Load snapshot and verify hash
        snapshot_file = Path(f".ai-snapshots/snapshot-{snapshot_id}.json")
        with open(snapshot_file) as f:
            snapshot_data = json.load(f)

        # Calculate expected hash
        content = temp_test_file.read_text()
        expected_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

        # Find our test file in snapshot
        test_file_key = str(temp_test_file.resolve())
        assert test_file_key in snapshot_data["files"], f"Test file should be in snapshot"

        actual_hash = snapshot_data["files"][test_file_key]["hash"]
        assert actual_hash == expected_hash, "File hash should match"


# ============================================================================
# Scenario 2: Repository Adaptation Tests
# ============================================================================

class TestScenario2RepoAdapt:
    """Test repository adaptation planning"""

    def test_repo_adapt_with_small_repo(self, check_api_key):
        """Test adaptation plan generation for a small public repo"""
        config = {
            "repo_url": "https://github.com/pallets/click",
            "model": check_api_key["preferred_model"]
        }

        result = scenario_2_repo_adapt.run(config)

        # Verify plan was generated
        assert "llm_response" in result, "LLM response should be in result"
        assert "output_file_path" in result, "Output file path should be in result"

        # Verify plan file exists and has content
        plan_file = Path(result["output_file_path"])
        assert plan_file.exists(), f"Plan file should exist: {plan_file}"

        plan_content = plan_file.read_text()
        assert len(plan_content) > 100, "Plan should have substantial content"

        # Verify plan contains required sections (Chinese keywords)
        assert "仓库理解" in plan_content, "Plan should contain repository understanding"
        assert "plan:" in plan_content or "步骤" in plan_content, \
            "Plan should contain executable steps"

    def test_repo_adapt_missing_url(self, check_api_key):
        """Test that missing repo URL is handled properly"""
        config = {}

        result = scenario_2_repo_adapt.run(config)

        # Should return error
        assert "error" in result, "Should return error for missing repo URL"
        assert "repo_url" in result["error"].lower(), "Error should mention repo_url"


# ============================================================================
# Scenario 3: Regression Detection Tests
# ============================================================================

class TestScenario3Regression:
    """Test regression detection and quality gates"""

    def test_regression_detection(self, check_api_key):
        """Test regression detection with real LLM"""
        config = {
            "baseline": "main~1",
            "build": "HEAD",
            "model": check_api_key["preferred_model"],
            "pass_rate_min": 95,
            "coverage_drop_max": 5
        }

        result = scenario_3_regression.run(config)

        # Verify gate result
        assert "llm_response" in result, "LLM response should be in result"
        assert "output_file_path" in result, "Output file path should be in result"

        # Verify output file
        gate_file = Path(result["output_file_path"])
        assert gate_file.exists(), f"Gate file should exist: {gate_file}"

        gate_content = gate_file.read_text()
        assert len(gate_content) > 50, "Gate report should have content"


# ============================================================================
# Scenario 4: Architecture Drift Tests
# ============================================================================

class TestScenario4ArchDrift:
    """Test architecture drift detection"""

    def test_arch_drift_detection(self, check_api_key):
        """Test architecture drift detection with real LLM"""
        config = {
            "model": check_api_key["preferred_model"]
        }

        result = scenario_4_arch_drift.run(config)

        # Verify analysis
        assert "llm_response" in result, "LLM response should be in result"
        assert "output_file_path" in result, "Output file path should be in result"

        # Verify output file
        arch_file = Path(result["output_file_path"])
        assert arch_file.exists(), f"Arch file should exist: {arch_file}"

        arch_content = arch_file.read_text()
        assert len(arch_content) > 50, "Arch report should have content"


# ============================================================================
# Scenario 5: RAG Query Tests
# ============================================================================

class TestScenario5LocalRAG:
    """Test local RAG queries"""

    def test_rag_simple_query(self, check_api_key):
        """Test RAG with a simple query"""
        result = scenario_5_local_rag.run_rag_query(
            project_root=".",
            patterns=["tests/**/*.py"],
            query="What are the main test files in this project?",
            model=check_api_key["preferred_model"],
            format="xml"
        )

        # Verify response
        assert "llm_response" in result, "LLM response should be in result"
        assert "files_to_prompt_stats" in result, "Should have file stats"

        llm_response = result["llm_response"]
        assert len(llm_response) > 20, "LLM response should have content"

        # Verify stats
        stats = result["files_to_prompt_stats"]
        assert stats["files_processed"] > 0, "Should process some files"
        assert stats["total_lines"] > 0, "Should have some lines"

    def test_rag_with_line_numbers(self, check_api_key):
        """Test RAG with line numbers enabled"""
        result = scenario_5_local_rag.run_rag_query(
            project_root=".",
            patterns=["engine.py"],
            query="Explain the Flow class implementation",
            model=check_api_key["preferred_model"],
            format="xml",
            include_line_numbers=True
        )

        assert "llm_response" in result, "LLM response should be in result"
        assert len(result["llm_response"]) > 50, "Should have detailed response"


# ============================================================================
# Scenario 6: Code Review Tests
# ============================================================================

class TestScenario6CodeReview:
    """Test code review pipeline"""

    def test_code_review_no_changes(self, check_api_key):
        """Test code review when there are no changes"""
        config = {
            "git_ref": "HEAD",
            "output_format": "yaml",
            "model": check_api_key["preferred_model"]
        }

        # This might fail if there are no changes, which is expected
        try:
            result = scenario_6_code_review.run(config)

            # If successful, verify structure
            assert "overall_summary" in result, "Should have overall summary"
            assert "security_gate_status" in result, "Should have security gate status"

        except Exception as e:
            # Expected if no changes
            assert "no changes" in str(e).lower() or "diff" in str(e).lower(), \
                f"Expected 'no changes' error, got: {e}"


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling across scenarios"""

    def test_llm_call_failure_stops_flow(self, monkeypatch):
        """Test that LLM failure stops the flow (Bug #1 fix verification)"""
        # Temporarily unset API keys to force LLM failure
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        config = {
            "file_patterns": ["tests/**/*.py"],
            "model": "claude-3-haiku-20240307"
        }

        # Should raise ValueError about missing API key
        with pytest.raises(ValueError, match="API_KEY"):
            scenario_1_local_snapshot.run(config)

    def test_write_file_missing_data_key(self):
        """Test that write_file_node raises error for missing data key (Bug #2 fix verification)"""
        from nodes.common.write_file_node import write_file_node

        node = write_file_node()

        # Context without the required key
        ctx = {"some_other_key": "value"}
        params = {"data_key": "missing_key", "output_path": "/tmp/test.json"}

        # Should raise ValueError about missing key
        with pytest.raises(ValueError, match="Required data key"):
            node["prep"](ctx, params)


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple scenarios"""

    def test_snapshot_create_and_restore_cycle(self, check_api_key, temp_test_file):
        """Test complete snapshot -> modify -> restore cycle"""
        # 1. Create initial snapshot
        config = {
            "file_patterns": [str(temp_test_file)],
            "model": check_api_key["preferred_model"]
        }

        result1 = scenario_1_local_snapshot.run(config)
        snapshot_id_1 = result1["snapshot_id"]

        # 2. Modify the file
        original_content = temp_test_file.read_text()
        modified_content = original_content + "\n\n# Test modification\n"
        temp_test_file.write_text(modified_content)

        # 3. Create second snapshot
        result2 = scenario_1_local_snapshot.run(config)
        snapshot_id_2 = result2["snapshot_id"]

        # Verify different snapshots
        assert snapshot_id_1 != snapshot_id_2, "Snapshots should have different IDs"

        # 4. Restore from first snapshot
        snapshot_file_1 = Path(f".ai-snapshots/snapshot-{snapshot_id_1}.json")
        with open(snapshot_file_1) as f:
            snapshot_data = json.load(f)

        # Get original content from snapshot
        test_file_key = str(temp_test_file.resolve())
        original_from_snapshot = snapshot_data["files"][test_file_key]["content"]

        # Restore the file
        temp_test_file.write_text(original_from_snapshot)

        # 5. Verify restoration
        restored_content = temp_test_file.read_text()
        assert restored_content == original_content, "Content should be restored to original"
        assert "# Test modification" not in restored_content, "Modification should be removed"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
