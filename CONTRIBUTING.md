# Contributing to ReviewSentry

Thanks for your interest in contributing. This document covers how to raise issues, propose changes, and submit pull requests.

---

## Before you start

- Check [open issues](https://github.com/Spyced-Concepts/ReviewSentry/issues) — your idea may already be tracked.
- For significant changes, open an issue first to discuss the approach before writing code. This avoids wasted effort.

## Reporting bugs

Open an issue with:
- A clear description of the unexpected behaviour
- The workflow snippet you're using (redact any secrets)
- The error output from the GitHub Actions log
- Which `ai_provider` and model you're using

## Proposing features

Open an issue describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

## Pull requests

**External contributors — keep it simple.** Open a single PR against `main` with a clear description of what changed and why. The maintainer will sequence your accepted change through the project's internal release workflow; you do not need to dual-PR or target release branches.

1. Fork the repository
2. Create a branch from `main` — `feature/short-description`, `fix/short-description`, or `docs/short-description`
3. Make your changes (see [Adapter development](#adapter-development) below if adding a new provider)
4. Verify the syntax check passes locally:
   ```bash
   python3 -c "import ast; ast.parse(open('scripts/review.py').read()); print('review.py OK')"
   python3 -c "import ast; ast.parse(open('scripts/adapters/your_adapter.py').read()); print('adapter OK')"
   python3 -c "import yaml; yaml.safe_load(open('action.yml')); print('action.yml OK')"
   ```
5. Update `CHANGELOG.md` under `[Unreleased]`
6. Open a PR against `main` with a clear description of what changed and why

**First-time contributors:** GitHub Actions workflow runs on your first PR may be blocked pending maintainer approval. This is a security policy, not a rejection — workflows from forks can otherwise run unreviewed code, and a security-focused project takes that risk seriously. Your run will be approved alongside your PR review.

## Release model

Releases are **not scheduled** — they ship when there is something to ship.

Version numbers follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html), applied by **type of change**:

| Bump | When |
|---|---|
| `vX.0.0` — MAJOR | Breaking changes (input contract changes, behaviour changes that consumers must adapt to) |
| `v0.X.0` — MINOR | New features (additive, non-breaking) — new provider adapters, new optional inputs, new criteria |
| `v0.X.Y` — PATCH | Bug fixes, hotfixes, security fixes, documentation-only changes |

## Internal release workflow

For maintainers cutting a release (this section is informational for contributors so the process is transparent):

1. Cut `feature/*` or `fix/*` from `main`. Open dual PRs: one to `functional-test` (testing lane) and one to the current `release/vX.Y.Z` branch (release prep lane).
2. After both merge, run regression on `functional-test`. Bug fixes go on a new `fix/*` branch from `main` with the same dual-PR pattern — never patch directly on a test or release branch.
3. When the release is ready, merge `release/vX.Y.Z` → `main`, tag the SHA, sync `main` → `functional-test`, cut `release/vX.Y.{Z+1}` (or appropriate next-version branch) from `main` for the next batch of work.

Stu owns release-namespace actions (creating release branches, tagging, merging PRs through the release sequence). Contributors do not need to perform any of these steps.

## Security

**Do not open a public issue for a security vulnerability.** See [SECURITY.md](SECURITY.md) for the private reporting channel.

A few project-wide standards every contributor should know:

- **No secrets in code, ever.** API keys, tokens, internal hostnames, customer identifiers — none of these belong in source, comments, tests, or example files.
- **No external Python dependencies.** ReviewSentry is stdlib-only on the runner; no `pip install`. New adapters must use `urllib` and stdlib JSON.
- **Pin every external action by full commit SHA, not by tag.** Applies to anything we depend on (e.g. `actions/checkout`) and is the pattern we recommend to our own users — see `SECURITY.md`. Pinning a tag in any new workflow file will be flagged in review.
- **No shell interpolation of user-controlled values.** PR title, body, and any external string is passed through environment variables to Python, never interpolated into shell.

## Adapter development

To add support for a new AI provider:

1. Create `scripts/adapters/<provider_name>.py`
2. Export exactly one function:
   ```python
   def call_api(
       api_key: str,
       model: str,
       system: str,
       user: str,
       base_url: str | None = None,
   ) -> str:
       """Call the provider API and return the review text as a string."""
   ```
3. The function must:
   - Return the review text as a plain string
   - Raise `urllib.error.HTTPError` or `urllib.error.URLError` on network/API failure
   - Use only Python stdlib (no `pip install`)
4. Add the provider name to `SUPPORTED_PROVIDERS` in `scripts/review.py`
5. Add a setup guide at `docs/setup-<provider>.md`
6. Update `README.md` — add the provider to the Supported providers table and the `ai_provider` input description in the Usage section

## Code style

- Python stdlib only — no external dependencies
- `set -euo pipefail` on all bash steps
- No hardcoded secrets, model identifiers, or provider URLs in `scripts/review.py` (core)
- All user-facing content (error messages, review criteria) stays in `review.py` — adapters contain only API call logic

## Licence

By contributing, you agree that your contribution will be licensed under the MIT licence that covers this project.
