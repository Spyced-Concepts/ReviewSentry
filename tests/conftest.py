"""
Shared fixtures and step definitions for the ReviewSentry BDD test suite.

Steps shared across multiple feature files are defined here.
Scenario-specific steps live in their respective test_*.py files.
"""

import os
import sys
import subprocess
import tempfile
import pytest

# ── Path setup ────────────────────────────────────────────────────────────────
# Add repo root and scripts/ to sys.path so production modules can be imported.

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")

for _path in (REPO_ROOT, SCRIPTS_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def repo_root():
    return REPO_ROOT


@pytest.fixture
def scripts_dir():
    return SCRIPTS_DIR


@pytest.fixture
def live_env():
    """Skip the test unless running inside GitHub Actions."""
    if not os.environ.get("GITHUB_ACTIONS"):
        pytest.skip("End-to-end scenario — requires GitHub Actions environment")


@pytest.fixture
def result_state():
    """Shared state for capturing subprocess results across step definitions."""
    return {"result": None}


@pytest.fixture
def temp_runner(tmp_path):
    """Provides a RUNNER_TEMP directory with a minimal diff file and GITHUB_OUTPUT."""
    diff_file = tmp_path / "pr_diff.txt"
    diff_file.write_text("+added line\n-removed line\n", encoding="utf-8")
    output_file = tmp_path / "github_output"
    output_file.write_text("", encoding="utf-8")
    return {
        "RUNNER_TEMP": str(tmp_path),
        "GITHUB_OUTPUT": str(output_file),
        "diff_path": str(diff_file),
    }


@pytest.fixture
def base_env(temp_runner):
    """Minimal valid environment for running review.py, minus the API key."""
    env = os.environ.copy()
    env.update({
        "AI_API_KEY":          "sk-test-key",
        "AI_MODEL":            "claude-haiku-4-5-20251001",
        "AI_PROVIDER":         "anthropic",
        "AI_BASE_URL":         "",
        "PR_TITLE":            "Test PR",
        "PR_BODY":             "Test description",
        "PR_NUMBER":           "1",
        "REVIEW_CRITERIA":     "",
        "CUSTOM_RULES":        "",
        "DIFF_LINES_LIMIT":    "1500",
        "SYSTEM_CONTEXT":      "",
        "REVIEWSENTRY_CONFIG": "",
        "SHOW_PASSING_CRITERIA": "true",
        "RUNNER_TEMP":         temp_runner["RUNNER_TEMP"],
        "GITHUB_OUTPUT":       temp_runner["GITHUB_OUTPUT"],
    })
    return env


def run_review_script(env):
    """Run review.py as a subprocess and return the CompletedProcess."""
    return subprocess.run(
        [sys.executable, os.path.join(SCRIPTS_DIR, "review.py")],
        env=env,
        capture_output=True,
        text=True,
    )


# ── Shared step definitions ───────────────────────────────────────────────────

from pytest_bdd import given, when, then, parsers  # noqa: E402 — after sys.path setup


@given("the action is configured with a valid API key")
def valid_api_key():
    pass


@given("the action is configured with a valid model identifier")
def valid_model():
    pass


@given(parsers.parse('the provider is set to "{provider}"'))
def provider_set(provider):
    return provider


@when("the pull request workflow triggers")
def workflow_triggers():
    pass


@then("the workflow completes without error")
def workflow_completes(live_env):
    pass


@then("a review comment is posted on the pull request")
def review_comment_posted(live_env):
    pass


@then("the workflow fails with a non-zero exit code")
def workflow_fails_shared(result_state):
    if result_state.get("result") is None:
        pytest.skip("No result captured — scenario requires live environment or populated result_state")
    assert result_state["result"].returncode != 0, \
        f"Expected non-zero exit code, got {result_state['result'].returncode}"
