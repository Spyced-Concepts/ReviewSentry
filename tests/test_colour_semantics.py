"""
Tests for features/colour_semantics.feature

Unit-tests the ``discipline.enforce_colour_semantics`` post-processing pass
established by RS-E-188-F-191 (sub-feature C of the review-reliability epic).

These are pure-Python unit tests — no subprocess, no live provider. The
discipline module has no import-time side effects, which is why it lives in
its own file (``scripts/discipline.py``) rather than inline in ``review.py``.
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from discipline import enforce_colour_semantics

scenarios("colour_semantics.feature")


# ── State container (per-scenario) ────────────────────────────────────────────


@pytest.fixture
def state():
    return {"input": "", "output": ""}


# ── Given steps ───────────────────────────────────────────────────────────────


@given("the review-discipline post-processing hook is available")
def hook_available():
    # Import-check: discipline module loads cleanly.
    from discipline import enforce_review_discipline  # noqa: F401


@given(parsers.parse('a review with section header "{header}"'))
def given_section_header(state, header):
    state["input"] = f"{header}\n"


@given(parsers.parse('the section body contains only "{marker} {label}" findings'))
def body_only_marker(state, marker, label):
    # Two homogeneous findings so the body isn't a one-liner.
    state["input"] += (
        f"- {marker} first {label.lower()} observation\n"
        f"- {marker} second {label.lower()} observation\n"
    )


@given(parsers.parse('the section body contains a "{marker} {label}" finding'))
def body_contains_marker(state, marker, label):
    state["input"] += f"- {marker} example {label.lower()} finding\n"


@given(parsers.parse('the section body contains a list-item finding "{line}"'))
def body_list_item(state, line):
    state["input"] += f"{line}\n"


@given("a review with two sections")
def two_sections_marker(state):
    # No-op: subsequent "the first section is ..." / "the second section is ..."
    # steps build the input incrementally.
    state["input"] = ""


@given(parsers.parse('the first section is "{header}" with only "{marker} {label}" findings'))
def first_section(state, header, marker, label):
    state["input"] += f"{header}\n- {marker} first fine bit\n- {marker} second fine bit\n\n"


@given(parsers.parse('the second section is "{header}" with a "{marker} {label}" finding'))
def second_section(state, header, marker, label):
    state["input"] += f"{header}\n- {marker} genuine {label.lower()} finding\n"


# ── When ──────────────────────────────────────────────────────────────────────


@when("the discipline hook runs")
def run_hook(state):
    state["output"] = enforce_colour_semantics(state["input"])


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('the section header remains "{header}"'))
def header_remains(state, header):
    # Header line should appear unchanged (allowing trailing whitespace variance).
    lines = state["output"].splitlines()
    header_lines = [ln for ln in lines if ln.strip().startswith(header.split(" ", 1)[0])]
    assert header_lines, f'No line starting with header marker; output was:\n{state["output"]}'
    # The literal header text must appear verbatim (no machine-note appended).
    assert any(ln.strip() == header for ln in lines), (
        f'Expected verbatim header "{header}" — output was:\n{state["output"]}'
    )


@then("no machine note is appended to the header")
def no_note(state):
    assert "post-processed" not in state["output"], (
        f'Expected no machine note; output was:\n{state["output"]}'
    )


@then(parsers.parse('the section header is rewritten to "{header}"'))
def header_rewritten(state, header):
    assert header in state["output"], (
        f'Expected header "{header}" in output; output was:\n{state["output"]}'
    )


@then(parsers.parse('the section header is emitted as "{header}"'))
def header_emitted_as(state, header):
    assert header in state["output"], (
        f'Expected header "{header}" in output; output was:\n{state["output"]}'
    )


@then(parsers.parse('a machine note is appended recording "{phrase}"'))
def note_appended(state, phrase):
    assert "post-processed" in state["output"], (
        f'Expected machine note; output was:\n{state["output"]}'
    )
    assert phrase in state["output"], (
        f'Expected phrase "{phrase}" in machine note; output was:\n{state["output"]}'
    )


@then("both section headers are preserved")
def both_preserved(state):
    lines = state["output"].splitlines()
    assert any(ln.strip() == "✅ Correctness" for ln in lines), state["output"]
    assert any(ln.strip() == "⚠️ Security" for ln in lines), state["output"]


@then("no machine notes are appended")
def no_notes(state):
    assert "post-processed" not in state["output"], state["output"]
