"""Tests for features/output_completeness.feature."""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from discipline import (
    enforce_review_discipline,
    enforce_incomplete_review_warning,
    has_verdict,
)

scenarios("output_completeness.feature")


@pytest.fixture
def state():
    return {
        "review": "",
        "diff_lines": 0,
        "diff_lines_limit": 0,
        "max_tokens": 0,
        "output": "",
    }


@given("the review-discipline post-processing hook is available")
def hook_available():
    assert callable(enforce_review_discipline)


@given("a review body ending with the verdict line")
def review_with_verdict(state):
    state["review"] = "Section A\n- ✓ fine\n\n📝 **AI Recommendation: APPROVE WITH NOTES**"


@given("a review body containing a verdict-shaped string in the middle but no trailing verdict")
def review_verdict_midbody(state):
    state["review"] = (
        "Section A\n"
        "- The reviewer template ends with lines like **AI Recommendation: APPROVE** — "
        "  we quote it here as an example, not as our verdict.\n"
        "Section B\n"
        "- more text, no trailing verdict, mid-sentence like"
    )


@given("a review body with no verdict line")
def review_no_verdict(state):
    state["review"] = "Partial review that was chopped mid-sentence and never emitted a"


@given("a review body with a mis-marked section header and no verdict line")
def review_mismarked_no_verdict(state):
    state["review"] = "⚠️ Correctness\n- ✓ all fine here\n"


@given("the measured diff filled the diff_lines limit")
def diff_at_limit(state):
    state["diff_lines"] = 1500
    state["diff_lines_limit"] = 1500
    state["max_tokens"] = 4096


@given("the review body is close to the max_tokens ceiling in characters")
def output_at_max_tokens(state):
    state["review"] = "x" * 15000
    state["max_tokens"] = 4096


@given("the measured diff is well under the diff_lines limit")
def diff_well_under(state):
    state["diff_lines"] = 100
    state["diff_lines_limit"] = 1500


@given("the review body is well under the max_tokens ceiling")
def output_well_under(state):
    state["max_tokens"] = 4096


@when(parsers.parse("the discipline hook runs with any measured values"))
def when_hook_runs_any(state):
    state["output"] = enforce_incomplete_review_warning(
        state["review"], diff_lines=100, diff_lines_limit=1500, max_tokens=4096
    )


@when("the discipline hook runs")
def when_hook_runs(state):
    state["output"] = enforce_review_discipline(
        state["review"],
        diff_lines=state["diff_lines"],
        diff_lines_limit=state["diff_lines_limit"],
        max_tokens=state["max_tokens"],
    )


@then("no incomplete-review warning is appended")
def then_no_warning(state):
    assert "Review incomplete" not in state["output"], state["output"]


@then("an incomplete-review warning is appended")
def then_warning(state):
    assert "Review incomplete" in state["output"], state["output"]


@then(parsers.parse('the warning states "{phrase}"'))
def then_warning_phrase(state, phrase):
    assert phrase in state["output"], f"expected {phrase!r} in warning; output was:\n{state['output']}"


@then("the warning includes the measured DIFF_LINES over DIFF_LIMIT")
def then_diff_measured(state):
    assert (
        f"DIFF_LINES={state['diff_lines']}/{state['diff_lines_limit']}"
        in state["output"]
    ), state["output"]


@then("the warning instructs the reader to raise max_tokens")
def then_raise_max_tokens(state):
    assert "raise max_tokens" in state["output"], state["output"]


@then("the warning names the measured DIFF_LINES and output_chars for the reader")
def then_names_measured(state):
    assert f"DIFF_LINES={state['diff_lines']}/{state['diff_lines_limit']}" in state["output"]
    assert "output=" in state["output"]


@then("the section header is corrected by colour-semantics enforcement")
def then_colour_corrected(state):
    assert "✅ Correctness" in state["output"], state["output"]


@then("an incomplete-review warning is also appended")
def then_also_warning(state):
    assert "Review incomplete" in state["output"], state["output"]
