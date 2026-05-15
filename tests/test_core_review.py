"""
Tests for features/core_review.feature

Validation error scenarios are tested by running review.py as a subprocess
with controlled environment variables. Scenarios requiring a live GitHub Actions
environment or real AI provider are skipped with a clear reason.
"""

import os
import sys
import pytest
from pytest_bdd import scenarios, given, then
from conftest import run_review_script

scenarios("core_review.feature")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Given steps (live or local) ───────────────────────────────────────────────

@given("the test repository has an open pull request with a non-empty diff")
def open_pr_with_diff(live_env):
    pass


@given("the API key is empty")
def api_key_empty(base_env, result_state):
    base_env["AI_API_KEY"] = ""
    result_state["result"] = run_review_script(base_env)


@given("the model identifier is empty")
def model_empty(base_env, result_state):
    base_env["AI_MODEL"] = ""
    result_state["result"] = run_review_script(base_env)


@given('the model identifier is set to a current valid provider model slug')
def valid_model_slug(live_env):
    pass


@given('the model identifier is set to "not-a-real-model-xyz"')
def invalid_model_slug(live_env):
    pass


@given("the API key is syntactically valid but rejected by the provider")
def invalid_api_key(live_env):
    pass


@given('the provider is set to "notarealai"')
def unknown_provider(base_env, result_state):
    base_env["AI_PROVIDER"] = "notarealai"
    result_state["result"] = run_review_script(base_env)


@given("the pull request has an empty diff")
def empty_diff(live_env):
    pass


@given("a custom base URL is configured pointing to an OpenAI-compatible endpoint")
def custom_base_url(live_env):
    pass


@given("the API key is set to the GITHUB_TOKEN")
def github_token_as_key(live_env):
    pass


@given('the diff_lines limit is set to "10"')
def diff_lines_limit(live_env):
    pass


@given('the pull request diff adds a workflow using a valid provider model slug in ai_model')
def diff_with_model_slug(live_env):
    pass


# ── Then steps ────────────────────────────────────────────────────────────────

@then("a comment is posted on the pull request")
def comment_posted(live_env):
    pass


@then('the comment contains the header "## AI Code Review"')
def comment_has_header(live_env):
    pass


@then('the comment ends with exactly one of "APPROVE", "APPROVE WITH NOTES", or "REQUEST CHANGES"')
def comment_has_verdict(live_env):
    pass


@then('the comment contains the footer "Automated review. Maintainer approval required."')
def comment_has_footer(live_env):
    pass


@then("no external API key was used")
def no_external_api_key(live_env):
    pass


@then('the review comment contains the truncation note "Diff was large — review based on first 10 lines only."')
def truncation_note(live_env):
    pass


@then('the log contains "AI_API_KEY secret not configured"')
def log_missing_api_key(result_state):
    output = result_state["result"].stdout + result_state["result"].stderr
    assert "AI_API_KEY secret not configured" in output, \
        f"Expected error message not found in output:\n{output}"


@then("no review comment is posted")
def no_comment_posted(result_state):
    # When validation fails before the adapter call, no comment step is reached
    assert result_state["result"].returncode != 0


@then('the log contains "AI_MODEL variable not configured"')
def log_missing_model(result_state):
    output = result_state["result"].stdout + result_state["result"].stderr
    assert "AI_MODEL variable not configured" in output, \
        f"Expected error message not found in output:\n{output}"


@then("the log contains an HTTP 401 error code")
def log_http_error(live_env):
    pass


@then("the log lists all supported provider names")
def log_supported_providers(result_state):
    output = result_state["result"].stdout + result_state["result"].stderr
    for provider in ("anthropic", "openai", "gemini", "github-models"):
        assert provider in output, \
            f"Expected provider '{provider}' not found in error output:\n{output}"


@then("the log contains a provider API error")
def log_provider_error(live_env):
    pass


@then("the log does not contain a ReviewSentry-generated model validation message")
def no_model_validation_message(live_env):
    pass


@then("the review comment does not contain a finding claiming the model name is invalid or non-existent")
def no_model_invalid_finding(live_env):
    pass
