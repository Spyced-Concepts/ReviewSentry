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
| ✅ Pass | 10 |
| ❌ Fail | 0 |
| ⏭️ Skip | 0 |

**Overall:** ✅ PASS

---

## Prerequisites checklist

- [x] `Spyced-Concepts/corvex-strike` has `AI_API_KEY` secret configured ✓ 2026-05-09
- [x] `Spyced-Concepts/corvex-strike` `AI_MODEL` updated to `claude-sonnet-4-6` for UAT ✓ 2026-05-09 — **revert to `claude-haiku-4-5-20251001` after UAT completes**
- [x] `Spyced-Concepts/corvex-strike` has `.github/workflows/ai-review.yml` pointing at `functional-test` ✓ PR #3
- [x] Tester has access to create PRs and observe workflow runs in corvex-strike

---

## Test scenarios

### UAT-001 — Valid diff, Anthropic provider

**Setup:** corvex-strike PR #3 — migration from inline script to action.

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | ✅ | 16 seconds |
| Review comment posted on PR | ✅ | Posted by github-actions[bot] |
| Comment contains `## AI Code Review` header | ✅ | No vendor branding |
| Comment ends with one of the three verdicts | ✅ | APPROVE WITH NOTES |
| `*Automated review. Maintainer approval required.*` footer present | ✅ | |

**Result:** ✅ Pass
**Notes:** Review content was high quality — correctly identified retry logic gap, truncation behaviour, and checkout step intent. No false positives.

---

### UAT-001c — Valid diff, GitHub Models (zero cost)

**Setup:** corvex-strike PR #3 — `ai_provider: github-models`, `ai_api_key: ${{ secrets.GITHUB_TOKEN }}`, `ai_model: gpt-4o`. No external API key.

**Bugs found and fixed during this scenario:**
- BUG-001: `models: read` permission required in workflow permissions block — fixed in `setup-github-models.md`
- BUG-002: GitHub Models uses `/chat/completions` not `/v1/chat/completions` — fixed by creating dedicated `github-models` adapter
- BUG-003: `importlib.import_module("adapters.github-models")` fails (hyphen invalid in Python module names) — fixed by normalising with `.replace("-", "_")` in `review.py`

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | ✅ | After 3 bug fixes; run 25609481561 |
| Review comment posted on PR | ✅ | Posted by github-actions[bot] |
| No external API key used | ✅ | GITHUB_TOKEN only |

**Result:** ✅ Pass (3 bugs found and fixed — all corrected in UAT branch)
**Notes:** Sensitive data scan ran correctly as criterion 1. GPT-4o via GitHub Models produced a well-structured review. Header `## AI Code Review` — no vendor branding.

---

### UAT-002 — Large diff truncation note

**Setup:** Set `diff_lines: 10` in corvex-strike workflow. Run 25609669842.

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | ✅ | 26 seconds |
| Truncation note present in comment | ✅ | `> Diff was large — review based on first 10 lines only.` |
| Note references the correct line limit (10) | ✅ | |

**Result:** ✅ Pass

---

### UAT-003 — Missing AI_API_KEY

**Setup:** Passed empty string as `ai_api_key` in workflow (run 25609713760).

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | ✅ | 6 seconds |
| Error message clear and actionable | ✅ | `AI_API_KEY secret not configured` |
| No partial review posted | ✅ | |

**Result:** ✅ Pass

---

### UAT-004 — Missing AI_MODEL

**Setup:** Passed empty string as `ai_model` in workflow (run 25609732479).

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | ✅ | 6 seconds |
| Error message clear and actionable | ✅ | `AI_MODEL variable not configured` |

**Result:** ✅ Pass

---

### UAT-005 — Invalid API key

**Setup:** Set `ai_api_key` to a syntactically valid but invalid key.

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | ✅ | |
| HTTP error code visible in log | ✅ | `API HTTP error 401: authentication_error: invalid x-api-key` |
| No partial review posted | ✅ | |

**Result:** ✅ Pass

---

### UAT-006 — Unknown AI_PROVIDER value

**Setup:** Set `ai_provider: notarealai` in workflow.

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | ✅ | |
| Error lists all supported providers | ✅ | `Supported: anthropic, gemini, github-models, openai` |

**Result:** ✅ Pass


### UAT-007 — Sensitive data detected in diff

**Setup:** Added `sk-ant-api03-DEVTEST...` as a comment in `packages/scanner/src/ai/index.ts`. Run 25610271335.

| Check | Result | Notes |
|---|---|---|
| Review comment posted | ✅ | |
| Sensitive data finding in criterion 1 | ✅ | `🚨 CRITICAL — Hardcoded API Key in Source Code` |
| Severity classified as Critical | ✅ | |
| Finding appears before other criteria | ✅ | First finding in review |

**Result:** ✅ Pass
**Notes:** AI named exact file and line, called it a blocker, recommended key rotation + git history scrub. Also noted the irony of the `review_criteria` stating "no hardcoded secrets".

**Cleanup:** ✅ Dummy credential removed in commit `13b7db7`; confirmed clean by grep.

---

### UAT-008 — PR body with shell metacharacters

**Setup:** PR body updated via API to include `$(echo injected)`, `` `date` ``, `$HOME`, `$(cat /etc/passwd)`. Run 25610347704.

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | ✅ | |
| No unexpected shell execution in logs | ✅ | Strings appear verbatim in logs — no command substitution |
| Review comment posted normally | ✅ | |

**Result:** ✅ Pass
**Notes:** PR body passed as env var to Python, not shell-interpolated. AI reviewer flagged the metacharacter content as a concern about injection safety — correctly noted it depends on the action's internal handling.

**Cleanup:** ✅ PR body restored to normal description after test.

---

### UAT-009 — Custom review criteria

**Setup:** Added UAT-009 custom criterion to `review_criteria`. Added a TODO with deadline and implementation detail to `ai/index.ts` to give the criterion something to flag.

| Check | Result | Notes |
|---|---|---|
| Review comment posted | ✅ | |
| Custom criterion visible in review | ✅ | `🟡 UAT-009 — Hardcoded TODO with Deadline` — named criterion, quoted line, classified High |

**Result:** ✅ Pass
**Notes:** First run (workflow change only) had nothing to flag — correct behaviour. Second run with a TODO containing a deadline fired the criterion precisely.

**Cleanup:** ✅ TODO removed from `ai/index.ts`; UAT-009 criterion removed from workflow in final cleanup commit.

---

### UAT-010 — Custom sensitive data rules

**Setup:** Added `custom_rules: "CORVEX_INTERNAL"` to workflow; added `// CORVEX_INTERNAL: ...` comment to `ai/index.ts`.

| Check | Result | Notes |
|---|---|---|
| Custom term flagged in review | ✅ | Flagged as leaking internal naming convention — blocker |
| Finding appears in criterion 1 section | ✅ | Raised under sensitive data / internal identifiers |

**Result:** ✅ Pass
**Notes:** AI correctly identified `CORVEX_INTERNAL` and flagged it regardless of whether it came from `custom_rules` or `review_criteria` — both inputs processed together.

**Cleanup:** ✅ `CORVEX_INTERNAL` removed from source and workflow in final cleanup commit `e19e405`; confirmed clean by grep.

---

## Post-run cleanup checklist

**Test repo (corvex-strike workflow) — final state:**
- [x] UAT-001c: `ai_provider: github-models` → reverted to `anthropic` ✓
- [x] UAT-002: `diff_lines: "10"` → removed ✓
- [x] UAT-003: `ai_api_key: ""` → reverted to `${{ secrets.AI_API_KEY }}` ✓
- [x] UAT-004: `ai_model: ""` → reverted to `${{ vars.AI_MODEL }}` ✓
- [x] UAT-005: invalid inline key → reverted to `${{ secrets.AI_API_KEY }}` ✓
- [x] UAT-006: `ai_provider: notarealai` → reverted to `anthropic` ✓
- [x] UAT-007: dummy credential removed from ai/index.ts ✓
- [x] UAT-008: PR body restored to normal description ✓
- [x] UAT-009: TODO comment removed, UAT criterion removed from workflow ✓
- [x] UAT-010: CORVEX_INTERNAL removed from source and workflow ✓
- [ ] Final workflow action ref: change from `uat/v0.2.0-alpha-macbook` → `functional-test` once UAT complete
- [ ] `AI_MODEL` variable in corvex-strike: revert to `claude-haiku-4-5-20251001` (set to `claude-sonnet-4-6` for UAT)

**Test PRs:**
- [ ] corvex-strike PR #3: close or merge when corvex-strike UAT is separately approved

**UAT branch:**
- [ ] All scenario results recorded
- [ ] Result summary updated
- [ ] Sign-off completed

---

## Sign-off

| Field | Value |
|---|---|
| Tester | Stu Last |
| Date | 2026-05-09 |
| Overall result | ✅ PASS |
| Defects raised | BUG-001 (models:read permission), BUG-002 (GitHub Models endpoint path), BUG-003 (hyphen in module name) — all fixed during UAT |
| Post-run cleanup complete | ✅ Yes — confirmed by grep 2026-05-09 |
| Ready to merge to functional-test | ✅ Yes |
| Notes / defects raised | |
