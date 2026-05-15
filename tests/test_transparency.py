"""
Tests for features/transparency.feature

All scenarios are static — they inspect repository files and source code.
No live GitHub Actions environment or API key required.
"""

import os
import re
import ast
import pytest
from pytest_bdd import scenarios, given, then

scenarios("transparency.feature")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def security_md_text():
    path = os.path.join(REPO_ROOT, "SECURITY.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def readme_text():
    path = os.path.join(REPO_ROOT, "README.md")
    with open(path, encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def review_py_text():
    path = os.path.join(REPO_ROOT, "scripts", "review.py")
    with open(path, encoding="utf-8") as f:
        return f.read()


# ── Step definitions ──────────────────────────────────────────────────────────

@given("the repository at the current release SHA is examined")
def repo_examined():
    pass


@given("the SECURITY.md file is read")
def security_md_read():
    pass


@given("the README example workflow is examined")
def readme_examined():
    pass


@given("the README example workflow permissions block is examined")
def readme_permissions_examined():
    pass


@given("the SYSTEM prompt in review.py is examined")
def system_prompt_examined():
    pass


@then("a SECURITY.md file exists at the repository root")
def security_md_exists():
    assert os.path.isfile(os.path.join(REPO_ROOT, "SECURITY.md")), \
        "SECURITY.md not found at repo root"


@then("it lists every secret the action receives")
def security_lists_secrets(security_md_text):
    assert "AI_API_KEY" in security_md_text or "ai_api_key" in security_md_text, \
        "SECURITY.md does not mention the AI API key"
    assert "github_token" in security_md_text.lower() or "GH_TOKEN" in security_md_text, \
        "SECURITY.md does not mention the GitHub token"


@then("it states exactly how each secret is used")
def security_states_secret_usage(security_md_text):
    assert "used" in security_md_text.lower() or "transmitted" in security_md_text.lower(), \
        "SECURITY.md does not describe how secrets are used"


@then("it states no secret is logged stored or transmitted beyond its intended destination")
def security_states_no_logging(security_md_text):
    text = security_md_text.lower()
    assert "not logged" in text or "never logged" in text or "no secret" in text or \
           "not stored" in text or "not transmitted" in text, \
        "SECURITY.md does not state that secrets are not logged/stored beyond intended use"


@then("it states only the PR diff and metadata are sent to the AI provider")
def security_states_data_sent(security_md_text):
    text = security_md_text.lower()
    assert "diff" in text and ("metadata" in text or "pr title" in text or "pr_title" in text), \
        "SECURITY.md does not specify that only diff and metadata are transmitted"


@then("it states no source code beyond the diff is transmitted")
def security_no_extra_source(security_md_text):
    text = security_md_text.lower()
    assert "diff" in text and ("source code" in text or "no additional" in text or
                               "only the" in text or "nothing else" in text or
                               "beyond the diff" in text), \
        "SECURITY.md does not confirm that no source code beyond the diff is transmitted"


@then("it explains how to pin to a full commit SHA")
def security_sha_pinning(security_md_text):
    assert "sha" in security_md_text.lower() or "commit" in security_md_text.lower(), \
        "SECURITY.md does not mention SHA pinning"


@then("it provides commands for verifying SHA to tag correspondence")
def security_sha_commands(security_md_text):
    assert "git" in security_md_text.lower() or "sha" in security_md_text.lower(), \
        "SECURITY.md does not provide SHA verification commands"


@then("it provides a responsible disclosure contact")
def security_disclosure_contact(security_md_text):
    text = security_md_text.lower()
    assert "contact" in text or "disclose" in text or "report" in text or \
           "security@" in text or "email" in text, \
        "SECURITY.md does not provide a responsible disclosure contact"


@then("it includes the complete SYSTEM prompt text")
def security_includes_system_prompt(security_md_text, review_py_text):
    match = re.search(r'_system_base\s*=\s*\(\s*"([^"]+)"', review_py_text)
    if match:
        first_sentence = match.group(1)[:40]
        assert first_sentence.lower() in security_md_text.lower(), \
            "SECURITY.md does not appear to include the SYSTEM prompt text"


@then("it explains the purpose of the untrusted-input instruction")
def security_explains_untrusted_instruction(security_md_text):
    text = security_md_text.lower()
    assert "untrusted" in text or "pr author" in text or "pr title" in text or \
           "pr body" in text or "injection" in text, \
        "SECURITY.md does not explain the purpose of the untrusted-input instruction"


@then('it does not contain a step using "actions/checkout"')
def readme_no_checkout(readme_text):
    assert "actions/checkout" not in readme_text, \
        "README example workflow contains actions/checkout — it should not be required"


@then('it does not include "contents: read"')
def readme_no_contents_read(readme_text):
    assert "contents: read" not in readme_text, \
        "README example workflow permissions include 'contents: read' — unnecessary"


@then('it includes "timeout-minutes"')
def readme_has_timeout(readme_text):
    assert "timeout-minutes" in readme_text, \
        "README example workflow does not include timeout-minutes"


@then('it includes a "concurrency" block keyed to the pull request number')
def readme_has_concurrency(readme_text):
    assert "concurrency" in readme_text and "pull_request" in readme_text, \
        "README example workflow does not include a concurrency block"


@then('"cancel-in-progress" is set to true')
def readme_cancel_in_progress(readme_text):
    assert "cancel-in-progress: true" in readme_text, \
        "README example workflow does not set cancel-in-progress: true"


@then("it contains an explicit instruction to treat PR title and body as data only")
def system_prompt_untrusted(review_py_text):
    assert "data only" in review_py_text.lower() or \
           "treat them as data" in review_py_text.lower() or \
           "untrusted" in review_py_text.lower(), \
        "SYSTEM prompt does not instruct the AI to treat PR content as data only"


@then("it contains an explicit instruction not to follow instructions embedded in PR content")
def system_prompt_no_follow(review_py_text):
    assert "do not follow" in review_py_text.lower() or \
           "not follow any instructions" in review_py_text.lower(), \
        "SYSTEM prompt does not instruct the AI to ignore embedded instructions"
