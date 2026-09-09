"""
ReviewSentry — review-discipline post-processing hook.

Established by sub-feature C of epic #188 (RS-E-188-F-191, honest colour
semantics). Provides the shared post-processing hook that later sub-features
chain into:

  - Output composition + multi-comment split (sub-feature B, epic #188, F-190)
  - Evidence anchor + pass-section discipline (#184, epic #183)
  - A11y disclaimer append (#187, epic #183)

Kept in its own module (no side effects at import time) so unit tests can
exercise the discipline passes without running the full ``review.py`` script.
"""

from __future__ import annotations

import re


# ── Colour-marker vocabulary ─────────────────────────────────────────────────

_ACTIONABLE_MARKERS = ("🔴", "🟠", "🟡")
_NON_ACTIONABLE_MARKERS = ("🔵", "✓")

# Section headers may or may not carry the U+FE0F variation selector on ⚠.
# Match both forms; ✅ is a single codepoint. Group 1 is normalised on emit.
_SECTION_HEADER_RE = re.compile(r"^(⚠️|⚠|✅)\s+(.+?)\s*$")

# Findings may be plain-line ("🔴 Something...") or list-item ("- 🔴 ..." / "* 🔴 ...").
_FINDING_LINE_RE = re.compile(r"^(?:\s*[-*]\s+)?(🔴|🟠|🟡|🔵|✓)")


def _normalise_header_marker(marker: str) -> str:
    """Return the canonical two-char ⚠️ form; leave ✅ untouched."""
    return "⚠️" if marker in ("⚠", "⚠️") else "✅"


# ── Sub-feature C — colour-semantics enforcement ─────────────────────────────


def enforce_colour_semantics(review_text: str) -> str:
    """Reconcile section-header markers with actual findings.

    A ⚠️ header requires at least one actionable finding (🔴/🟠/🟡) in its body;
    a ✅ header requires none. Where the emitted marker disagrees with its body,
    the header is rewritten and a machine note is appended recording the fix.
    """
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
        declared = _normalise_header_marker(declared_raw)

        # Collect section body up to the next section header (or end of review).
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
    """Return True if any finding-line in the body carries an actionable marker."""
    for line in body_lines:
        m = _FINDING_LINE_RE.match(line)
        if m and m.group(1) in _ACTIONABLE_MARKERS:
            return True
    return False


# ── Shared hook — chain point for later sub-features ─────────────────────────


def enforce_review_discipline(review_text: str, metadata: dict | None = None) -> str:
    """Shared post-processing hook.

    Currently applies colour-semantics enforcement only. Chain point for:

      - Output composition + multi-comment split (sub-feature B of #188)
      - Evidence anchor + pass-section discipline (#184 of #183)
      - A11y disclaimer append (#187 of #183)

    The ``metadata`` argument is unused here — reserved for later passes that
    need to derive accurate incomplete-review warnings from measured values
    (``DIFF_LINES``, ``output_chars``, ``max_tokens_estimate``, ...).
    """
    return enforce_colour_semantics(review_text)
