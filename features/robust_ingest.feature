Feature: Robust large-input handling — never fail silently on ingest
  Established by RS-E-188-F-189 (sub-feature A of the review-reliability epic).

  The tool must not hard-fail on realistic PRs, and must not report a silent
  no-review when one file dominates the diff. Two mechanisms cover the class:

    - Files matching `exclude_paths` (default: common lockfiles) are dropped
      before the model sees them; the exclusion is enumerated at the top of
      the review so it is honest.
    - A single file whose diff exceeds `chunk_threshold_lines` is split at
      hunk boundaries into multiple sub-batches, each carrying the file
      header so the reviewer knows what it is looking at.

  Closes #174 (single oversized file exceeds token limit).

  Background:
    Given the diff_utils module is available

  Scenario: Default exclude_paths drops package-lock.json before the model sees it
    Given a diff containing two files "src/foo.py" and "package-lock.json"
    When exclude_paths is set to the default lockfile suite
    Then "src/foo.py" is kept for review
    And "package-lock.json" is reported as excluded
    And the excluded entry records its line count

  Scenario: Empty exclude_paths preserves all files
    Given a diff containing two files "src/foo.py" and "package-lock.json"
    When exclude_paths is set to the empty list
    Then both files are kept for review
    And no files are reported as excluded

  Scenario: A glob pattern matches file basenames
    Given a diff containing "docs/README.md" and "src/foo.py"
    When exclude_paths is set to "*.md"
    Then "src/foo.py" is kept for review
    And "docs/README.md" is reported as excluded

  Scenario: A full-path glob pattern matches the file path
    Given a diff containing "src/foo.py" and "vendor/big.py"
    When exclude_paths is set to "vendor/*.py"
    Then "src/foo.py" is kept for review
    And "vendor/big.py" is reported as excluded

  Scenario: A small single-file diff passes through the chunker unchanged
    Given a small single-file diff with 10 lines
    When the file is chunked with a threshold of 100 lines
    Then a single sub-diff is returned
    And the sub-diff is identical to the original

  Scenario: An oversized single-file diff is split at hunk boundaries
    Given a single-file diff with three separate hunks totalling 30 lines
    When the file is chunked with a threshold of 15 lines
    Then multiple sub-diffs are returned
    And every sub-diff carries the file's "diff --git" header
    And every sub-diff begins its own hunks with a "@@" line

  Scenario: A file diff with no hunks (rename only) is returned unchanged
    Given a single-file diff with headers only and no hunks
    When the file is chunked with a threshold of 5 lines
    Then a single sub-diff is returned
    And the sub-diff is identical to the original

  Scenario: Split file diff header excludes any hunk content
    Given a single-file diff with one hunk
    When the file diff is split into header and hunks
    Then the header contains "diff --git" and does not contain "@@"
    And the first hunk starts with "@@"
