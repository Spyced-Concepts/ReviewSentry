"""Review-output post-processing passes."""

from __future__ import annotations

import re


_ACTIONABLE_MARKERS = ("🔴", "🟠", "🟡")
_SECTION_HEADER_RE = re.compile(r"^(⚠️|⚠|✅)\s+(.+?)\s*$")
_FINDING_LINE_RE = re.compile(r"^(?:\s*[-*]\s+)?(🔴|🟠|🟡|🔵|✓)")


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


def enforce_review_discipline(review_text: str) -> str:
    """Return `review_text` after all discipline passes."""
    return enforce_colour_semantics(review_text)
