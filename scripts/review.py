"""
ai-pr-review — core review script.

Provider-agnostic. Reads the PR diff, builds the review prompt, dispatches to
the configured adapter, and writes the result to GITHUB_OUTPUT.

Environment variables (set by action.yml):
    AI_API_KEY       — provider API key (from repository secret)
    AI_MODEL         — model identifier (from repository variable)
    AI_PROVIDER      — adapter: anthropic | openai | gemini | github-models (default: anthropic)
    AI_BASE_URL      — optional base URL override for OpenAI-compatible endpoints
    PR_TITLE         — pull request title
    PR_BODY          — pull request description (may be empty)
    PR_NUMBER        — pull request number
    REVIEW_CRITERIA  — additional criteria lines (optional)
    DIFF_LINES_LIMIT — max lines captured (for truncation note)
"""

import importlib
import os
import sys
import urllib.error

# ── Configuration ─────────────────────────────────────────────────────────────

API_KEY   = os.environ.get("AI_API_KEY", "")
MODEL     = os.environ.get("AI_MODEL", "")
PROVIDER  = os.environ.get("AI_PROVIDER", "anthropic").strip().lower()
BASE_URL  = os.environ.get("AI_BASE_URL", "").strip()
PR_TITLE  = os.environ.get("PR_TITLE", "")
PR_BODY   = os.environ.get("PR_BODY", "")
PR_NUM    = os.environ.get("PR_NUMBER", "")
EXTRA     = os.environ.get("REVIEW_CRITERIA", "")

SUPPORTED_PROVIDERS = {"anthropic", "openai", "gemini", "github-models"}

if not API_KEY:
    print("::error::AI_API_KEY secret not configured")
    sys.exit(1)
if not MODEL:
    print("::error::AI_MODEL variable not configured")
    sys.exit(1)
if PROVIDER not in SUPPORTED_PROVIDERS:
    print(
        f"::error::Unknown AI_PROVIDER '{PROVIDER}'. "
        f"Supported: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
    )
    sys.exit(1)

# ── Load diff ─────────────────────────────────────────────────────────────────

runner_temp = os.environ.get("RUNNER_TEMP", "/tmp")
diff_path   = os.path.join(runner_temp, "pr_diff.txt")

if not os.path.exists(diff_path):
    print(f"::error::Diff file not found at {diff_path}")
    sys.exit(1)

with open(diff_path, encoding="utf-8") as f:
    diff = f.read()

# ── Build prompt ──────────────────────────────────────────────────────────────

SYSTEM = (
    "You are an expert code reviewer. Review pull request diffs thoroughly, "
    "flag genuine issues clearly, and be concise. Distinguish blockers from "
    "minor observations. Never invent issues that are not present in the diff."
)

body_excerpt = PR_BODY[:500] if PR_BODY else "(no description)"
diff_block   = diff.strip() if diff.strip() else "(empty diff)"

criteria = [
    "1. **Sensitive data disclosure** — flag any credentials, API keys, personal information "
    "(real names, usernames, email addresses), file system paths revealing machine username, "
    "computer/host names, or private repo names/URLs. Severity: Critical (credentials), "
    "High (personal identifiers, private paths), Moderate (computer names, repo names). "
    "Report before all other findings.",
    "2. **Merge conflicts** — flag any conflict markers (<<<<<<, =======, >>>>>>>) as an immediate blocker.",
    "3. **Correctness** — does the code do what it claims? Are edge cases handled?",
    "4. **Cross-platform** — will it work on macOS, Linux, and Windows (Git Bash)?",
    "5. **Bash quality** — set -euo pipefail, quoting, portability, no bashisms.",
    "6. **Security** — no hardcoded secrets, no path injection, no unsafe variable expansion.",
    "7. **Code quality** — no magic numbers or strings, no code smells, correct approach.",
    "8. **Dependencies** — no unnecessary external modules; flag anything not from stdlib.",
    "9. **Documentation** — relevant docs updated alongside code changes.",
    "10. **PR scope** — single concern, or should it be split?",
]

if EXTRA:
    for i, line in enumerate(EXTRA.strip().splitlines(), start=len(criteria) + 1):
        if line.strip():
            criteria.append(f"{i}. {line.strip()}")

USER = (
    f"PR #{PR_NUM}: {PR_TITLE}\n\n"
    f"{body_excerpt}\n\n"
    "Diff:\n```diff\n"
    f"{diff_block}\n```\n\n"
    "Review against these criteria:\n"
    + "\n".join(criteria)
    + "\n\nEnd with exactly one of:\nAPPROVE\nAPPROVE WITH NOTES\nREQUEST CHANGES"
)

# ── Dispatch to adapter ───────────────────────────────────────────────────────

try:
    adapter = importlib.import_module(f"adapters.{PROVIDER}")
except ModuleNotFoundError:
    print(f"::error::Adapter module 'adapters/{PROVIDER}.py' not found")
    sys.exit(1)

try:
    review = adapter.call_api(
        api_key=API_KEY,
        model=MODEL,
        system=SYSTEM,
        user=USER,
        base_url=BASE_URL or None,
    )
except urllib.error.HTTPError as e:
    print(f"::error::API HTTP error {e.code}: {e.read().decode()}")
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"::error::Network error reaching AI API: {e.reason}")
    sys.exit(1)
except Exception as e:
    print(f"::error::{e}")
    sys.exit(1)

if not isinstance(review, str) or not review.strip():
    print("::error::Adapter returned empty or non-string review")
    sys.exit(1)

# ── Write output ──────────────────────────────────────────────────────────────

delimiter = "AI_REVIEW_EOF"
with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
    out.write(f"review<<{delimiter}\n{review}\n{delimiter}\n")

print("Review complete.")
