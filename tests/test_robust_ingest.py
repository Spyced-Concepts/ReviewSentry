"""
Tests for features/robust_ingest.feature

Unit-tests the pure-Python diff_utils additions from sub-feature A of the
review-reliability epic (RS-E-188-F-189): ``filter_by_exclude_paths``,
``split_file_diff_by_hunk``, ``pack_hunks_under_threshold``,
``chunk_single_file_diff``, and ``DEFAULT_EXCLUDE_PATHS``.

End-to-end behaviour (empty-diff race retry in action.yml, decode-error
banner in the posted review, all-excluded short-circuit) is exercised by
the workflow itself on real PRs — the reproducers for #174 and #178 are
the acceptance path.
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from diff_utils import (
    filter_by_exclude_paths,
    split_file_diff_by_hunk,
    chunk_single_file_diff,
    split_diff_by_file,
    file_path,
    DEFAULT_EXCLUDE_PATHS,
)

scenarios("robust_ingest.feature")


# ── State container (per-scenario) ────────────────────────────────────────────


@pytest.fixture
def state():
    return {}


# ── Fixture builders ──────────────────────────────────────────────────────────


def _make_file_diff(path: str, hunk_count: int = 1, lines_per_hunk: int = 3) -> str:
    """Fabricate a plausible unified-diff block for ``path`` with N hunks."""
    header = (
        f"diff --git a/{path} b/{path}\n"
        f"index abc..def 100644\n"
        f"--- a/{path}\n"
        f"+++ b/{path}\n"
    )
    hunks = []
    for i in range(hunk_count):
        start = 1 + i * 10
        body_lines = [f"+line {j}" for j in range(lines_per_hunk)]
        hunks.append(f"@@ -{start},0 +{start},{lines_per_hunk} @@\n" + "\n".join(body_lines) + "\n")
    return header + "".join(hunks)


# ── Given steps ───────────────────────────────────────────────────────────────


@given("the diff_utils module is available")
def diff_utils_available():
    pass  # import already succeeded at module load


@given(parsers.parse('a diff containing two files "{path_a}" and "{path_b}"'))
def diff_two_files(state, path_a, path_b):
    state["diff"] = _make_file_diff(path_a) + _make_file_diff(path_b)


@given(parsers.parse('a diff containing "{path_a}" and "{path_b}"'))
def diff_two_generic(state, path_a, path_b):
    state["diff"] = _make_file_diff(path_a) + _make_file_diff(path_b)


@given(parsers.parse('a small single-file diff with {n:d} lines'))
def small_single_file(state, n):
    body = max(1, n - 5)
    state["file_diff"] = _make_file_diff("src/small.py", hunk_count=1, lines_per_hunk=body)


@given("a single-file diff with three separate hunks totalling 30 lines")
def three_hunk_diff(state):
    state["file_diff"] = _make_file_diff("src/big.py", hunk_count=3, lines_per_hunk=8)


@given("a single-file diff with headers only and no hunks")
def rename_only_diff(state):
    state["file_diff"] = (
        "diff --git a/old.py b/new.py\n"
        "similarity index 100%\n"
        "rename from old.py\n"
        "rename to new.py\n"
    )


@given("a single-file diff with one hunk")
def one_hunk_diff(state):
    state["file_diff"] = _make_file_diff("src/one.py", hunk_count=1, lines_per_hunk=3)


# ── When steps ────────────────────────────────────────────────────────────────


@when("exclude_paths is set to the default lockfile suite")
def when_default_excludes(state):
    files = split_diff_by_file(state["diff"])
    state["kept"], state["excluded"] = filter_by_exclude_paths(files, list(DEFAULT_EXCLUDE_PATHS))


@when("exclude_paths is set to the empty list")
def when_empty_excludes(state):
    files = split_diff_by_file(state["diff"])
    state["kept"], state["excluded"] = filter_by_exclude_paths(files, [])


@when(parsers.parse('exclude_paths is set to "{pattern}"'))
def when_specific_pattern(state, pattern):
    files = split_diff_by_file(state["diff"])
    state["kept"], state["excluded"] = filter_by_exclude_paths(files, [pattern])


@when(parsers.parse("the file is chunked with a threshold of {threshold:d} lines"))
def when_chunk(state, threshold):
    state["chunks"] = chunk_single_file_diff(state["file_diff"], threshold)


@when("the file diff is split into header and hunks")
def when_split_header_hunks(state):
    state["header"], state["hunks"] = split_file_diff_by_hunk(state["file_diff"])


# ── Then steps ────────────────────────────────────────────────────────────────


@then(parsers.parse('"{path}" is kept for review'))
def then_kept(state, path):
    kept_paths = [file_path(fd) for fd in state["kept"]]
    assert path in kept_paths, f"expected {path} in kept, got {kept_paths}"


@then(parsers.parse('"{path}" is reported as excluded'))
def then_excluded(state, path):
    excluded_paths = [p for p, _ in state["excluded"]]
    assert path in excluded_paths, f"expected {path} in excluded, got {excluded_paths}"


@then("the excluded entry records its line count")
def then_line_count_present(state):
    for path, line_count in state["excluded"]:
        assert isinstance(line_count, int) and line_count > 0, (
            f"expected positive line count for {path}, got {line_count!r}"
        )


@then("both files are kept for review")
def then_both_kept(state):
    assert len(state["kept"]) == 2, f"expected 2 kept, got {len(state['kept'])}"


@then("no files are reported as excluded")
def then_no_excluded(state):
    assert state["excluded"] == [], f"expected no exclusions, got {state['excluded']}"


@then("a single sub-diff is returned")
def then_single_chunk(state):
    assert len(state["chunks"]) == 1, f"expected 1 chunk, got {len(state['chunks'])}"


@then("the sub-diff is identical to the original")
def then_identical(state):
    assert state["chunks"][0] == state["file_diff"]


@then("multiple sub-diffs are returned")
def then_multiple_chunks(state):
    assert len(state["chunks"]) > 1, f"expected >1 chunks, got {len(state['chunks'])}"


@then(parsers.parse('every sub-diff carries the file\'s "{marker}" header'))
def then_every_chunk_has_header(state, marker):
    for chunk in state["chunks"]:
        assert marker in chunk, f"chunk missing {marker!r}: {chunk[:80]!r}"


@then(parsers.parse('every sub-diff begins its own hunks with a "{marker}" line'))
def then_every_chunk_has_hunks(state, marker):
    for chunk in state["chunks"]:
        assert marker in chunk, f"chunk missing {marker!r}: {chunk[:120]!r}"


@then(parsers.parse('the header contains "{a}" and does not contain "{b}"'))
def then_header_contains_and_not(state, a, b):
    assert a in state["header"], f"header missing {a!r}"
    assert b not in state["header"], f"header should not contain {b!r}"


@then(parsers.parse('the first hunk starts with "{marker}"'))
def then_first_hunk_starts_with(state, marker):
    assert state["hunks"], "no hunks parsed"
    assert state["hunks"][0].startswith(marker), (
        f"first hunk should start with {marker!r}, got {state['hunks'][0][:40]!r}"
    )
