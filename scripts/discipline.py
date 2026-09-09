"""Review-output post-processing passes."""

from __future__ import annotations

import re


_ACTIONABLE_MARKERS = ("🔴", "🟠", "🟡")
_SECTION_HEADER_RE = re.compile(r"^(⚠️|⚠|✅)\s+(.+?)\s*$")
_FINDING_LINE_RE = re.compile(r"^(?:\s*[-*]\s+)?(🔴|🟠|🟡|🔵|✓)")
_VERDICT_LINE_RE = re.compile(
    r"\*\*AI Recommendation:\s*(APPROVE WITH NOTES|REQUEST CHANGES|APPROVE)\*{0,2}"
)
_CHARS_PER_TOKEN = 4
_INCOMPLETE_OUTPUT_RATIO = 0.9


def enforce_colour_semantics(review_text: str) -> str:
    """Return `review_text` with section headers rewritten to match their findings."""
    lines = review_text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        header_match = _SECTION_HEADER_RE.match(lines[i])
        if not header_match:
            out.append(lines[i])
            i += 1
            continue

        declared_raw, section_name = header_match.groups()
        declared = "⚠️" if declared_raw in ("⚠", "⚠️") else "✅"

        body_start = i + 1
        body_end = body_start
        while body_end < len(lines) and not _SECTION_HEADER_RE.match(lines[body_end]):
            body_end += 1
        body_lines = lines[body_start:body_end]

        has_actionable = _section_has_actionable(body_lines)
        correct = "⚠️" if has_actionable else "✅"

        if declared != correct:
            note = (
                f"  *(post-processed: header {declared} → {correct}; section "
                f"contained {'an actionable' if has_actionable else 'no actionable'} finding)*"
            )
            out.append(f"{correct} {section_name}{note}")
        else:
            out.append(f"{correct} {section_name}")

        out.extend(body_lines)
        i = body_end
    return "\n".join(out)


def _section_has_actionable(body_lines: list[str]) -> bool:
    """Return True if any line in `body_lines` starts with an actionable finding marker."""
    for line in body_lines:
        m = _FINDING_LINE_RE.match(line)
        if m and m.group(1) in _ACTIONABLE_MARKERS:
            return True
    return False


def has_verdict(review_text: str) -> bool:
    """Return True if the last non-empty line of `review_text` contains a valid AI Recommendation verdict."""
    for line in reversed(review_text.splitlines()):
        if line.strip():
            return _VERDICT_LINE_RE.search(line) is not None
    return False


def derive_incomplete_cause(
    output_chars: int,
    diff_lines: int,
    diff_lines_limit: int,
    max_tokens: int,
) -> str:
    """Return the most probable cause of an incomplete review, derived from measured values."""
    max_tokens_chars_estimate = max_tokens * _CHARS_PER_TOKEN
    if diff_lines_limit and diff_lines >= diff_lines_limit:
        return (
            f"diff too large — reached diff_lines ({diff_lines}/{diff_lines_limit}); "
            "reduce PR scope or raise diff_lines"
        )
    if max_tokens_chars_estimate and output_chars >= int(max_tokens_chars_estimate * _INCOMPLETE_OUTPUT_RATIO):
        return (
            f"output limit reached — review reached max_tokens (~{output_chars} of "
            f"~{max_tokens_chars_estimate} chars); raise max_tokens"
        )
    return (
        "cause undetermined — measured diff and output were within their limits; "
        "check provider status or increase max_tokens"
    )


def enforce_incomplete_review_warning(
    review_text: str,
    diff_lines: int,
    diff_lines_limit: int,
    max_tokens: int,
) -> str:
    """Return `review_text` with an incomplete-review warning appended if no verdict is present."""
    if has_verdict(review_text):
        return review_text
    cause = derive_incomplete_cause(
        output_chars=len(review_text),
        diff_lines=diff_lines,
        diff_lines_limit=diff_lines_limit,
        max_tokens=max_tokens,
    )
    warning = (
        f"\n\n⚠️ **Review incomplete: {cause}.**\n"
        f"Measured: DIFF_LINES={diff_lines}/{diff_lines_limit}, "
        f"output={len(review_text)} chars, max_tokens={max_tokens}."
    )
    return review_text.rstrip() + warning


def enforce_review_discipline(
    review_text: str,
    diff_lines: int,
    diff_lines_limit: int,
    max_tokens: int,
) -> str:
    """Return `review_text` after all discipline passes."""
    review_text = enforce_colour_semantics(review_text)
    review_text = enforce_incomplete_review_warning(
        review_text,
        diff_lines=diff_lines,
        diff_lines_limit=diff_lines_limit,
        max_tokens=max_tokens,
    )
    return review_text
