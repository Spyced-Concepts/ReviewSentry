# Changelog

All notable changes to ReviewSentry are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html) — applied by *type of change*, not by a fixed release cadence:

- **MAJOR** (`vX.0.0`) — breaking changes
- **MINOR** (`v0.X.0`) — new features
- **PATCH** (`v0.X.Y`) — bug fixes, hotfixes, and documentation-only changes

Releases are not scheduled — they ship when there is something to ship.

> **Prior name.** Before 2026-05-09 (v0.2.2-alpha) this project was called `ai-pr-review`. The action's `name:` field has been `ReviewSentry` since v0.2.2-alpha; the GitHub repository slug was renamed to `Spyced-Concepts/ReviewSentry` on 2026-05-14. Historical CHANGELOG entries and UAT records below preserve their original wording.

---

## [0.3.2-beta] — 2026-05-14

### Security
- **Removed the `@v0` floating tag** to eliminate the supply-chain risk class. Floating tags are mutable — the maintainer (or anyone gaining write access) can rewrite where they point, and consumers' next run silently executes the new code with their secrets. SHA pinning is now the only supported pattern. See `SECURITY.md`.

### Changed
- **All documentation now recommends SHA pinning with a version comment** (Dependabot-readable). Tag pinning, including version tags, is no longer documented as a supported pattern.
- **Repository renamed from `ai-pr-review` to `ReviewSentry`** to match the marketplace listing and the action's `name:` field. GitHub Actions does NOT redirect `uses:` references for renamed action repositories (deliberate security policy) — every consumer must update their `uses:` line to the new slug.
- Documentation, issue/discussion templates, and code docstrings updated to use the current name `ReviewSentry` throughout. Historical CHANGELOG entries and UAT records preserved unchanged.

---

## [Unreleased] — v0.2.0-alpha

### Added
- **Provider adapter architecture** — `scripts/adapters/` package; core `review.py` is now provider-agnostic with zero AI-vendor references; dispatches via `AI_PROVIDER` env var
- **Anthropic adapter** (`adapters/anthropic.py`) — extracted from original `review.py`; prompt caching retained
- **OpenAI adapter** (`adapters/openai.py`) — OpenAI Chat Completions API; also works with Groq, Azure OpenAI, Mistral, Ollama, and **GitHub Models** via `ai_base_url`
- **Gemini adapter** (`adapters/gemini.py`) — Google Gemini generateContent API
- **`ai_provider` input** — selects the adapter; default `anthropic` (backwards-compatible)
- **`ai_base_url` input** — optional base URL override for OpenAI-compatible endpoints
- **`custom_rules` input** — user-definable sensitive data scan rules (FR-009)
- **Sensitive data disclosure scan** — always-on, always-first criterion (FR-008): credentials, personal identifiers, private paths, computer/host names, private repo names; severity-classified Critical → High → Moderate
- **GitHub Models support** — free AI code review using `GITHUB_TOKEN`; documented in `docs/setup-github-models.md`
- **Schema metadata** — YAML frontmatter in all `docs/setup-*.md` files (provider, adapter, cost, available models, complexity)
- **Provider setup docs** — `docs/setup-anthropic.md`, `docs/setup-openai.md`, `docs/setup-gemini.md`, `docs/setup-github-models.md`
- `CHANGELOG.md` (this file)
- `CONTRIBUTING.md`
- **`SECURITY.md`** — includes per-provider data handling policy links, what data is transmitted, and user responsibility statement
- **Data Handling Notice** in `LICENSE` — explicit user responsibility clauses for third-party AI data transmission

### Changed
- `action.yml` description updated — leads with security-first and zero-cost positioning for GitHub Marketplace
- `README.md` rewritten — differentiation table, security-first positioning, GitHub Models as the zero-cost quick start, architecture diagram, provider comparison table
- Review criteria renumbered — sensitive data disclosure is criterion 1 (was absent in v0.1.0)

### Breaking change

**`ai_provider` is now required.** There is no default. This is an intentional choice — as an open-source, provider-agnostic tool we do not favour any particular AI. Existing workflows that did not set `ai_provider` will now fail with a clear error listing the supported providers.

**Migration:** add `ai_provider: anthropic` (or your chosen provider) to any workflow that previously omitted it.

### Changed
- Review criteria renumbered — sensitive data disclosure is now criterion 1 (was absent); all others shifted by one
- `review.py` docstring updated — removes AI-vendor references; reflects new adapter architecture

### Migration guide (v0.1.0 → v0.2.0)

No breaking changes. Existing workflows that don't set `ai_provider` default to `anthropic` and behave identically to v0.1.0. To opt in to a different provider, add `ai_provider: openai` (or `gemini`) to your workflow step.

---

## [0.1.0] — 2026-05-05

### Added
- Initial release
- `action.yml` — composite GitHub Action
- `scripts/review.py` — single-file review script (Anthropic default)
- `README.md`, `LICENSE` (MIT, England and Wales governing law)
- Product specification (`docs/` — vault-side)
