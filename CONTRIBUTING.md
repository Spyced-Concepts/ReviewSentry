# Contributing to ai-pr-review

Thanks for your interest in contributing. This document covers how to raise issues, propose changes, and submit pull requests.

---

## Before you start

- Check [open issues](https://github.com/Spyced-Concepts/ai-pr-review/issues) — your idea may already be tracked.
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

1. Fork the repository
2. Create a branch from `main` — `feature/short-description`
3. Make your changes (see [Adapter development](#adapter-development) below if adding a new provider)
4. Verify the syntax check passes locally:
   ```bash
   python3 -c "import ast; ast.parse(open('scripts/review.py').read()); print('review.py OK')"
   python3 -c "import ast; ast.parse(open('scripts/adapters/your_adapter.py').read()); print('adapter OK')"
   python3 -c "import yaml; yaml.safe_load(open('action.yml')); print('action.yml OK')"
   ```
5. Update `CHANGELOG.md` under `[Unreleased]`
6. Open a PR against `main` with a clear description of what changed and why

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
