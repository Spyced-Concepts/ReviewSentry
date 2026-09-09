"""
ReviewSentry diff utilities.

Splitting, batching, and aggregation helpers used by review.py.
All functions are pure (no I/O, no env reads) so tests can import them directly.

Sub-feature A of epic #188 (RS-E-188-F-189) added:
    - filter_by_exclude_paths — drop generated / lockfile paths before review
    - split_file_diff_by_hunk / pack_hunks_under_threshold / chunk_single_file_diff
      — within-file hunk-boundary chunking so a single oversized file
      (package-lock.json etc.) no longer blows the model's context window
"""

import fnmatch
import os
import re

# ── Verdict constants ──────────────────────────────────────────────────────────

_VERDICT_RE = re.compile(
    r'\*\*AI Recommendation: (APPROVE WITH NOTES|REQUEST CHANGES|APPROVE)\*{0,2}'
)
_VERDICT_RANK = {"REQUEST CHANGES": 2, "APPROVE WITH NOTES": 1, "APPROVE": 0}
_VERDICT_EMOJI = {"APPROVE": "✅", "APPROVE WITH NOTES": "📝", "REQUEST CHANGES": "❌"}


# ── Diff splitting ─────────────────────────────────────────────────────────────

def split_diff_by_file(diff_text: str) -> list[str]:
    """Split a unified diff into per-file sections at diff --git boundaries."""
    files: list[str] = []
    current: list[str] = []
    for line in diff_text.splitlines(keepends=True):
        if line.startswith('diff --git ') and current:
            files.append(''.join(current))
            current = []
        current.append(line)
    if current:
        files.append(''.join(current))
    return files


def file_path(file_diff: str) -> str:
    """Extract the b-side path from a diff --git header line."""
    first = file_diff.split('\n', 1)[0]
    parts = first.split(' b/', 1)
    return parts[1].strip() if len(parts) == 2 else first.strip()


def batch_file_diffs(file_diffs: list[str], char_limit: int) -> list[list[str]]:
    """
    Group file diffs into batches each fitting within char_limit.

    A single file that exceeds char_limit on its own is placed in its own
    batch rather than dropped — the caller decides how to handle oversized
    individual files. If char_limit is very small, each file still gets its
    own batch (no infinite loop, no data loss).
    """
    batches: list[list[str]] = []
    current: list[str] = []
    size = 0
    for fd in file_diffs:
        if size + len(fd) > char_limit and current:
            batches.append(current)
            current = []
            size = 0
        current.append(fd)
        size += len(fd)
    if current:
        batches.append(current)
    return batches


# ── Sub-feature A of #188 — exclude_paths filtering ──────────────────────────


def _path_matches_any(path: str, patterns: list[str]) -> bool:
    """Return True if ``path`` matches any glob in ``patterns``.

    Patterns are matched against the full path AND the basename, so both
    ``package-lock.json`` (bare filename) and ``build/**/*.json`` (subtree)
    glob styles work as expected.
    """
    basename = os.path.basename(path)
    for pat in patterns:
        if fnmatch.fnmatchcase(path, pat) or fnmatch.fnmatchcase(basename, pat):
            return True
    return False


def filter_by_exclude_paths(
    file_diffs: list[str],
    exclude_patterns: list[str],
) -> tuple[list[str], list[tuple[str, int]]]:
    """Split ``file_diffs`` into (kept, excluded).

    ``excluded`` is a list of ``(path, line_count)`` tuples so callers can
    render an *"Excluded from review"* section listing what was skipped and
    by how much. An empty ``exclude_patterns`` list is a no-op — everything
    is kept.
    """
    if not exclude_patterns:
        return list(file_diffs), []
    kept: list[str] = []
    excluded: list[tuple[str, int]] = []
    for fd in file_diffs:
        path = file_path(fd)
        if _path_matches_any(path, exclude_patterns):
            excluded.append((path, fd.count('\n')))
        else:
            kept.append(fd)
    return kept, excluded


# ── Sub-feature A of #188 — within-file hunk-boundary chunking ───────────────

# Sensible default suite of lockfiles that are almost always machine-generated
# and rarely valuable to review line-by-line. Callers may extend or replace.
DEFAULT_EXCLUDE_PATHS = (
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.lock",
    "Gemfile.lock",
    "poetry.lock",
    "composer.lock",
    "go.sum",
    "pubspec.lock",
    "mix.lock",
    "uv.lock",
)


def split_file_diff_by_hunk(file_diff: str) -> tuple[str, list[str]]:
    """Split a single-file diff into (header, hunks).

    ``header`` carries the ``diff --git`` / ``index`` / ``---`` / ``+++`` lines
    that precede the first hunk. ``hunks`` is a list of ``@@`` blocks, each
    including its own ``@@`` header and content lines up to (but not including)
    the next ``@@`` — or end of the file diff.

    A file diff with no hunks (pure rename, mode change, etc.) returns the
    whole thing as the header with an empty ``hunks`` list.
    """
    lines = file_diff.splitlines(keepends=True)
    first_hunk = next((i for i, ln in enumerate(lines) if ln.startswith('@@')), None)
    if first_hunk is None:
        return ''.join(lines), []
    header = ''.join(lines[:first_hunk])
    hunks: list[str] = []
    current: list[str] = []
    for line in lines[first_hunk:]:
        if line.startswith('@@') and current:
            hunks.append(''.join(current))
            current = []
        current.append(line)
    if current:
        hunks.append(''.join(current))
    return header, hunks


def pack_hunks_under_threshold(
    header: str,
    hunks: list[str],
    threshold_lines: int,
) -> list[str]:
    """Pack ``hunks`` into sub-diffs each ≤ ``threshold_lines``, prefixing
    every batch with ``header`` so the reviewer always sees which file is
    being examined.

    A hunk that exceeds ``threshold_lines`` on its own is emitted in a batch
    of its own — never split further, and never dropped. This matches the
    behaviour of ``batch_file_diffs`` for oversized single files.
    """
    if not hunks:
        return [header] if header.strip() else []
    header_lines = header.count('\n')
    batches: list[str] = []
    current: list[str] = []
    current_lines = header_lines
    for hunk in hunks:
        hunk_lines = hunk.count('\n')
        if current and (current_lines + hunk_lines) > threshold_lines:
            batches.append(header + ''.join(current))
            current = []
            current_lines = header_lines
        current.append(hunk)
        current_lines += hunk_lines
    if current:
        batches.append(header + ''.join(current))
    return batches


def chunk_single_file_diff(file_diff: str, threshold_lines: int) -> list[str]:
    """Return ``[file_diff]`` if the diff is under threshold; otherwise
    split by hunk boundary and return multiple sub-diffs each ≤ threshold.

    Each returned sub-diff carries the file's header (``diff --git`` /
    ``---`` / ``+++``) so the reviewer knows which file it is looking at.
    """
    if file_diff.count('\n') <= threshold_lines:
        return [file_diff]
    header, hunks = split_file_diff_by_hunk(file_diff)
    if not hunks:
        return [file_diff]  # nothing to split — usually a rename with no body
    return pack_hunks_under_threshold(header, hunks, threshold_lines)


# ── Verdict extraction and aggregation ────────────────────────────────────────

def extract_verdict(text: str) -> str:
    """Return the verdict string from a review, or empty string if not found."""
    m = _VERDICT_RE.search(text)
    return m.group(1) if m else ""


def strip_verdict_line(text: str) -> str:
    """Remove the trailing verdict line(s) from a review pass."""
    lines = text.rstrip().splitlines()
    while lines and _VERDICT_RE.search(lines[-1]):
        lines.pop()
    return '\n'.join(lines)


def aggregate_reviews(reviews: list[str]) -> str:
    """
    Combine N per-batch reviews into a single output with a unified verdict.

    Each pass is labelled "Review pass N of M". The combined verdict is the
    worst-case across all passes (REQUEST CHANGES > APPROVE WITH NOTES > APPROVE).
    """
    verdicts = [extract_verdict(r) for r in reviews]
    ranked = [_VERDICT_RANK[v] for v in verdicts if v in _VERDICT_RANK]

    if ranked:
        worst = max(ranked)
        label = next(k for k, v in _VERDICT_RANK.items() if v == worst)
        verdict_line = f'{_VERDICT_EMOJI[label]} **AI Recommendation: {label}**'
    else:
        verdict_line = (
            "⚠️ Could not extract verdict from all review passes — "
            "review may be incomplete."
        )

    parts = [
        f'### Review pass {i} of {len(reviews)}\n\n{strip_verdict_line(r)}'
        for i, r in enumerate(reviews, 1)
    ]

    return '\n\n---\n\n'.join(parts) + f'\n\n---\n\n{verdict_line}'


# ── Review splitting ───────────────────────────────────────────────────────────

# Criterion sections start with ✅/⚠️ (per-criterion headers) or ### (multi-pass
# pass headers from chunked reviews).
_SECTION_RE = re.compile(r'^(✅|⚠️|###\s)', re.MULTILINE)

COMMENT_CHAR_LIMIT = 50_000  # GitHub's hard limit is 65,536; 50K gives a safe margin


def split_review_for_posting(review: str, char_limit: int = COMMENT_CHAR_LIMIT) -> list[str]:
    """
    Split a review into parts each ≤ char_limit characters, breaking at
    criterion-section boundaries (lines starting with ✅, ⚠️, or ###).

    If a single section exceeds char_limit it is placed in its own part rather
    than truncated — no content is dropped. The verdict line is always in the
    last part because splits occur at section *starts*, keeping each section
    with the content that follows it (including any trailing verdict).

    Returns a list of 1 or more non-empty strings.
    """
    if len(review) <= char_limit:
        return [review]

    boundaries = [m.start() for m in _SECTION_RE.finditer(review)]
    if not boundaries:
        # No section markers — hard split at char_limit
        return [review[i: i + char_limit] for i in range(0, len(review), char_limit)]

    parts: list[str] = []
    start = 0

    while start < len(review):
        end = start + char_limit
        if end >= len(review):
            parts.append(review[start:])
            break
        # Last section boundary strictly between start and end
        split_at = next((b for b in reversed(boundaries) if start < b < end), None)
        if split_at is None:
            # Current section alone exceeds limit — include it whole
            split_at = next((b for b in boundaries if b > end), len(review))
        parts.append(review[start:split_at].rstrip())
        start = split_at

    return parts or [review]
