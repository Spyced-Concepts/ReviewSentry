# UAT Run — ai-pr-review v0.2.0-alpha — MacBook Pro

> Copied from `docs/uat/UAT-TEMPLATE.md`. Results recorded on branch `uat/v0.2.0-alpha-macbook`.

---

## Run metadata

| Field | Value |
|---|---|
| Version | v0.2.0-alpha |
| Platform | macbook-pro |
| Tester | Stu Last |
| Date | 2026-05-09 |
| Action ref tested | `Spyced-Concepts/ai-pr-review@functional-test` |
| Provider(s) tested | anthropic, github-models |
| Test repo | Spyced-Concepts/corvex-strike |
| Branch | uat/v0.2.0-alpha-macbook |

## Result summary

| Result | Count |
|---|---|
| ✅ Pass | |
| ❌ Fail | |
| ⏭️ Skip | |

**Overall:** IN PROGRESS

---

## Prerequisites checklist

- [ ] `Spyced-Concepts/corvex-strike` has `AI_API_KEY` secret configured
- [ ] `Spyced-Concepts/corvex-strike` has `AI_MODEL` variable configured
- [ ] `Spyced-Concepts/corvex-strike` has `.github/workflows/ai-review.yml` pointing at `functional-test`
- [ ] Tester has access to create PRs and observe workflow runs in corvex-strike

---

## Test scenarios

### UAT-001 — Valid diff, Anthropic provider

**Setup:** Open a PR in corvex-strike with at least one changed file and a clean diff.

**Expected:** Workflow completes. Review comment posted starting with `## AI Code Review`, ending with a verdict.

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | | |
| Review comment posted on PR | | |
| Comment contains `## AI Code Review` header | | |
| Comment ends with one of the three verdicts | | |
| `*Automated review. Maintainer approval required.*` footer present | | |

**Result:**
**Notes:**

---

### UAT-001c — Valid diff, GitHub Models (zero cost)

**Setup:** Change workflow to use `ai_api_key: ${{ secrets.GITHUB_TOKEN }}`, `ai_provider: openai`, `ai_base_url: https://models.inference.ai.azure.com`, `ai_model: gpt-4o`. No extra secret needed.

**Expected:** Review comment posted using the GitHub-provided token.

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | | |
| Review comment posted on PR | | |
| No external API key used | | |

**Result:**
**Notes:**

---

### UAT-002 — Large diff truncation note

**Setup:** Set `diff_lines: 10` in the workflow to force truncation on any PR.

**Expected:** Review comment contains `> Diff was large — review based on first 10 lines only.`

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | | |
| Truncation note present in comment | | |
| Note references the correct line limit (10) | | |

**Result:**
**Notes:**

---

### UAT-003 — Missing AI_API_KEY

**Setup:** Temporarily remove the `AI_API_KEY` secret from corvex-strike. Re-run or open a new PR.

**Expected:** Workflow fails. Log contains `::error::AI_API_KEY secret not configured`.

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | | |
| Error message clear and actionable | | |
| No partial review posted | | |

**Result:**
**Notes:**

---

### UAT-004 — Missing AI_MODEL

**Setup:** Remove the `AI_MODEL` variable from corvex-strike. Open a PR or re-run.

**Expected:** Workflow fails with `::error::AI_MODEL variable not configured`.

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | | |
| Error message clear and actionable | | |

**Result:**
**Notes:**

---

### UAT-005 — Invalid API key

**Setup:** Set `AI_API_KEY` to `sk-ant-INVALID000000000000000000000` in corvex-strike secrets.

**Expected:** Workflow fails with HTTP 401 error visible in log.

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | | |
| HTTP error code visible in log | | |
| No partial review posted | | |

**Result:**
**Notes:**

---

### UAT-006 — Unknown AI_PROVIDER value

**Setup:** Set `ai_provider: notarealai` in the workflow file temporarily.

**Expected:** Workflow fails with `::error::Unknown AI_PROVIDER 'notarealai'. Supported: anthropic, gemini, openai`.

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | | |
| Error lists all supported providers | | |

**Result:**
**Notes:**

---

### UAT-007 — Sensitive data detected in diff

**Setup:** Open a PR that adds a line containing a dummy key pattern, e.g.: `# TEST_KEY=sk-ant-test1234567890abcdefghijklmnop` in a comment.

**Expected:** Review flags the pattern as Critical in criterion 1 before all other findings.

| Check | Result | Notes |
|---|---|---|
| Review comment posted | | |
| Sensitive data finding in criterion 1 | | |
| Severity classified as Critical | | |
| Finding appears before other criteria | | |

**Result:**
**Notes:**

---

### UAT-008 — PR body with shell metacharacters

**Setup:** Open a PR with body text containing: `$(echo injected)` and `` `date` ``.

**Expected:** Workflow completes normally. No shell injection. Metacharacters appear safely.

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | | |
| No unexpected shell execution in logs | | |
| Review comment posted normally | | |

**Result:**
**Notes:**

---

### UAT-009 — Custom review criteria

**Setup:** Add `review_criteria: "Check for hardcoded TODO comments"` to the workflow. Open a PR.

**Expected:** Review includes the custom criterion in its output.

| Check | Result | Notes |
|---|---|---|
| Review comment posted | | |
| Custom criterion visible in review | | |

**Result:**
**Notes:**

---

### UAT-010 — Custom sensitive data rules

**Setup:** Add `custom_rules: "CORVEX_INTERNAL"` to the workflow. Open a PR adding the string `CORVEX_INTERNAL` somewhere in the diff.

**Expected:** Sensitive data scan flags `CORVEX_INTERNAL` as a finding.

| Check | Result | Notes |
|---|---|---|
| Custom term flagged in review | | |
| Finding appears in criterion 1 section | | |

**Result:**
**Notes:**

---

## Sign-off

| Field | Value |
|---|---|
| Tester | Stu Last |
| Date | 2026-05-09 |
| Overall result | |
| Ready to merge to functional-test | |
| Notes / defects raised | |
