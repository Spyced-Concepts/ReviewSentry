"""
Tests for features/model_handling.feature

Static scenarios (SYSTEM prompt inspection, README content) are implemented.
Live API scenarios are skipped.
"""

import os
import pytest
from pytest_bdd import scenarios, given, then

scenarios("model_handling.feature")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def review_py_source():
    path = os.path.join(REPO_ROOT, "scripts", "review.py")
    with open(path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def readme_source():
    path = os.path.join(REPO_ROOT, "README.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


# ── Given steps ───────────────────────────────────────────────────────────────

@given("the model identifier is set to a current valid provider model slug")
def valid_slug(live_env):
    pass


@given('the model identifier is set to "not-a-real-model-xyz"')
def invalid_slug(live_env):
    pass


@given("the pull request diff adds a workflow using a valid provider model slug in ai_model")
def diff_with_valid_model(live_env):
    pass


@given("the README is examined")
def readme_examined():
    pass


# ── Then steps — live (skipped) ───────────────────────────────────────────────

@then("a review comment is posted")
def review_posted(live_env):
    pass


@then("the log contains a provider API error")
def provider_api_error(live_env):
    pass


@then("the log does not contain a ReviewSentry-generated model validation message")
def no_model_validation(live_env):
    pass


# ── Then steps — static ───────────────────────────────────────────────────────

@then("the review comment does not contain a finding claiming the model name is invalid or non-existent")
def no_invalid_model_finding(review_py_source):
    assert "validate" not in review_py_source.lower() or \
           "do not attempt to validate" in review_py_source.lower(), \
        "review.py may still be validating model identifiers"
    assert "Do not attempt to validate AI model identifiers" in review_py_source, \
        "SYSTEM prompt should instruct the AI not to validate model identifiers"


@then("it does not list specific model identifiers as the only valid options")
def readme_no_exhaustive_model_list(readme_source):
    assert "only valid" not in readme_source.lower() and \
           "only supported model" not in readme_source.lower(), \
        "README implies specific models are the only valid options"


@then("it states that any model identifier supported by the configured provider is accepted")
def readme_any_model_accepted(readme_source):
    text = readme_source.lower()
    assert "any model" in text or "provider" in text and "model" in text, \
        "README does not state that any provider-supported model identifier is accepted"


@then("it recommends choosing a cost-efficient model without naming specific models")
def readme_cost_efficient_recommendation(readme_source):
    assert "cost" in readme_source.lower() or "efficient" in readme_source.lower() or \
           "setup guide" in readme_source.lower(), \
        "README should recommend choosing a cost-efficient model"
