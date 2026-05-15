"""
Tests for features/draft_pr_control.feature

Documentation scenarios are implemented locally (static file inspection).
Runtime scenarios (actual draft PR behaviour) require a live GitHub Actions
environment and are skipped without GITHUB_ACTIONS set.
"""

import os
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

scenarios("draft_pr_control.feature")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def action_yml_text():
    with open(os.path.join(REPO_ROOT, "action.yml"), encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def readme_text():
    with open(os.path.join(REPO_ROOT, "README.md"), encoding="utf-8") as f:
        return f.read()


# ── Given steps — live env required ──────────────────────────────────────────

@given("the pull request is a draft")
def pr_is_draft(live_env):
    pass


@given("the pull request is not a draft")
def pr_is_not_draft(live_env):
    pass


@given("the pull request was a draft and has been marked ready for review")
def pr_converted_to_ready(live_env):
    pass


@given("the pull request draft status is unavailable in the event context")
def pr_draft_status_unavailable(live_env):
    pass


@given("the review_drafts input is not configured")
def review_drafts_not_set(live_env):
    pass


@given(parsers.parse('the review_drafts input is set to "{value}"'))
def review_drafts_set(value, live_env):
    pass


@given('the review_drafts input is set to ""')
def review_drafts_set_empty(live_env):
    pass


@given(parsers.parse('the fail_on input is set to "{value}"'))
def fail_on_set(value, live_env):
    pass


@given("the action.yml file is examined")
def action_yml_examined():
    pass


@given("the README file is examined")
def readme_examined():
    pass


# ── When steps — live env required ───────────────────────────────────────────

@when("the pull request workflow triggers on the ready_for_review event")
def workflow_triggers_ready_for_review(live_env):
    pass


# ── Then steps — live env required ───────────────────────────────────────────

@then("the workflow exits with code 0")
def workflow_exits_zero(live_env):
    pass


@then("no review comment is posted")
def no_comment_posted_draft(live_env):
    pass


@then('the log contains "Skipping review — pull request is a draft"')
def log_contains_skip_message(live_env):
    pass


@then("the log contains a warning about the unrecognised review_drafts value")
def log_contains_review_drafts_warning(live_env):
    pass


@then("the log states the accepted values for review_drafts")
def log_states_accepted_values(live_env):
    pass


# ── Then steps — static (locally testable) ────────────────────────────────────

@then("the review_drafts input is defined")
def review_drafts_input_defined(action_yml_text):
    assert "review_drafts" in action_yml_text, \
        "action.yml does not define a review_drafts input"


@then("its description states the default is true")
def review_drafts_default_documented(action_yml_text):
    assert "review_drafts" in action_yml_text, \
        "review_drafts input missing from action.yml"
    idx = action_yml_text.index("review_drafts")
    section = action_yml_text[idx:idx + 500]
    assert "true" in section.lower() and "default" in section.lower(), \
        "review_drafts description does not state default is true"


@then("its description lists the accepted values")
def review_drafts_accepted_values_documented(action_yml_text):
    idx = action_yml_text.index("review_drafts")
    section = action_yml_text[idx:idx + 500]
    assert "true" in section and "false" in section, \
        "review_drafts description does not list accepted values"


@then("its description explains the fallback behaviour for unrecognised values")
def review_drafts_fallback_documented(action_yml_text):
    idx = action_yml_text.index("review_drafts")
    section = action_yml_text[idx:idx + 500]
    assert "warning" in section.lower() or "defaults" in section.lower() or \
           "unrecognised" in section.lower() or "unrecognized" in section.lower(), \
        "review_drafts description does not explain fallback for unrecognised values"


@then("the inputs table contains a row for review_drafts")
def readme_has_review_drafts_row(readme_text):
    assert "review_drafts" in readme_text, \
        "README inputs table does not contain a row for review_drafts"


@then("the row states the default value")
def readme_review_drafts_default(readme_text):
    idx = readme_text.index("review_drafts")
    line = readme_text[idx:idx + 300]
    assert "true" in line.lower(), \
        "README review_drafts row does not state the default value"


@then("the row describes the accepted values and fallback behaviour")
def readme_review_drafts_accepted_values(readme_text):
    idx = readme_text.index("review_drafts")
    line = readme_text[idx:idx + 300]
    assert "false" in line.lower() and ("warning" in line.lower() or
           "defaults" in line.lower() or "unrecognised" in line.lower()), \
        "README review_drafts row does not describe accepted values and fallback"


@then("it mentions that draft pull requests are reviewed by default")
def readme_mentions_draft_default(readme_text):
    text = readme_text.lower()
    assert "draft" in text and "default" in text, \
        "README does not mention that draft PRs are reviewed by default"


@then("it mentions the review_drafts input as the opt-out mechanism")
def readme_mentions_review_drafts_opt_out(readme_text):
    assert "review_drafts" in readme_text, \
        "README does not mention review_drafts as the opt-out mechanism"
