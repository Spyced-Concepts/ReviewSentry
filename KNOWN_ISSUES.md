# Known Issues — ReviewSentry

Issues you may encounter during normal use. These are documented limitations,
not undetected bugs. Each entry links to the tracking issue where applicable.

---

## KI-001 — Large PR diffs cause incomplete reviews

**Affects:** Any PR whose diff exceeds the AI provider's token limit for a single request.

**What you see:** The review comment is posted but ends mid-sentence, with no verdict line. The workflow check emits a warning annotation but exits with code 0 — it does not block the merge.

**Why it happens:** ReviewSentry sends the PR diff to the AI in one request. If the diff is too large for the model's context window, the model stops generating before producing the verdict.

**What to do:**
- Reduce PR scope — smaller, single-concern PRs review more reliably and are easier to reason about.
- Increase `diff_lines` in your workflow configuration to send more lines to the model. Note that higher values consume more tokens and may require a higher-tier model subscription depending on your provider.

---

## KI-002 — Self-review check stays red on feature branch PRs during active development

**Affects:** Contributors developing ReviewSentry itself, using the self-review workflow.

**What you see:** A PR's AI review check fails even when the code is correct, because the action runs from `functional-test` (not the feature branch being reviewed). A fix on the feature branch does not take effect in the self-review until that PR merges to `functional-test`.

**Why it happens:** The self-review workflow uses `Spyced-Concepts/ReviewSentry@functional-test` as the action reference. GitHub Actions runs the referenced version, not the version in the PR.

**What to do:** This is expected during development. The required status checks (Syntax check, Unit and integration tests) are the merge gates — the AI review check is advisory. Merge once the required checks pass and the review verdict (where present) is acceptable.

**Affects:** Maintainers only. End users of ReviewSentry are not affected.

---

## KI-003 — Test suite uses gherkin-official 29.0.0 (current release: 39.x)

**Affects:** Contributors running the test suite locally or reading `tests/requirements-dev.txt`.

**What you see:** The pinned version of `gherkin-official` is significantly behind the current stable release.

**Why it happens:** `pytest-bdd 8.1.0` requires `gherkin-official>=29.0.0,<30.0.0`. The version is constrained by the framework, not by a deliberate choice to lag behind.

**What to do:** The test suite works correctly with the pinned version. No action required. Research into upgrading is tracked in [issue #81](https://github.com/Spyced-Concepts/ReviewSentry/issues/81).

## KI-004 — Review does not re-run when a draft PR is marked ready for review

**Affects:** Teams using the `ready_for_review` event to trigger a final review before merge.

**What you see:** Converting a pull request from draft to ready for review does not trigger a new ReviewSentry run. The `ready_for_review` GitHub event is not currently included in the workflow trigger.

**Why it happens:** The default `ai-review.yml` workflow triggers on `opened`, `synchronize`, and `reopened`. The `ready_for_review` event (fired when a draft PR is marked ready) is a distinct event type and is not included.

**What to do:** Push a trivial commit to the PR branch after marking it ready for review. This fires the `synchronize` event and triggers a fresh review. Alternatively, close and re-open the PR — this fires `reopened`.

**Planned:** A future release will add a `review_on_ready` input so teams can opt in to automatic re-review on the `ready_for_review` event.

---

*If you encounter a problem not listed here, please [open an issue](https://github.com/Spyced-Concepts/ReviewSentry/issues).*
