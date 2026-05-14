# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| Latest release on `main` | ✅ |
| Older releases | ✗ — update to the latest release |

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Use our contact form: **[spycedconcepts.co.uk/contact](https://spycedconcepts.co.uk/contact)**

Include: a description of the vulnerability, steps to reproduce, potential impact, and any suggested remediation. We will acknowledge within 48 hours and aim to release a fix within 7 days for critical issues.

---

## What data is transmitted to AI providers

This action transmits **only the PR diff and PR metadata** (title, body excerpt up to 500 characters) to your configured AI provider. It does **not** transmit:

- The full codebase or any files outside the diff
- Repository secrets, environment variables, or credentials
- GitHub tokens (the AI API key is stored separately as a repository secret)
- Any other repository data

The diff contains only the lines changed in the pull request, plus context lines. For public repositories this is already public information. For private repositories, you are choosing to send your code changes to a third-party AI provider — see **Your responsibilities** below.

---

## AI provider data handling policies

Review your chosen provider's policy before using this action with private or sensitive codebases.

| Provider | Data handling summary | Policy link |
|---|---|---|
| **Anthropic** | API inputs/outputs not used to train models by default for API customers | [anthropic.com/legal/privacy](https://www.anthropic.com/legal/privacy) |
| **OpenAI** | API data not used for training by default; Zero Data Retention available for enterprise | [openai.com/policies/api-data-usage-policies](https://openai.com/policies/api-data-usage-policies) |
| **Google Gemini** | API data may be used to improve models unless you opt out or use an enterprise agreement | [ai.google.dev/gemini-api/terms](https://ai.google.dev/gemini-api/terms) |
| **GitHub Models** | Governed by GitHub's Terms of Service and the underlying model provider's policy | [docs.github.com/en/site-policy/github-terms/github-terms-of-service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) |
| **Azure OpenAI** | Your data is not used to train or improve Microsoft or third-party models | [learn.microsoft.com/en-us/legal/cognitive-services/openai/data-privacy](https://learn.microsoft.com/en-us/legal/cognitive-services/openai/data-privacy) |
| **Groq / others** | Check the specific provider's terms | — |

> **These summaries are provided for convenience and may not be current.** Always read your provider's full terms before use, especially for regulated industries or sensitive codebases.

---

## This action is only as secure as the AI you plug in

This action provides a secure integration layer — how it handles your GitHub token, runs Python, posts comments, and manages secrets is entirely within our control and documented above. What happens **inside** your chosen AI provider is not.

The security, privacy, data retention, and compliance posture of your code review depends entirely on the AI provider you configure. We make no representation about the security practices of any provider, and we accept no liability for how they handle the content you send them. Choosing a provider for use with sensitive, regulated, or proprietary code is a security decision you own.

Things that are in **our** control:
- How secrets are handled within the action (documented above)
- What data is captured and transmitted (diff + PR metadata only)
- The security of the action code itself

Things that are **your** responsibility:
- Which AI provider you connect
- Which model you use and what its data handling policy is
- Whether that provider is appropriate for your codebase's classification
- How you configure the action (API keys as secrets, not hardcoded)
- Compliance with your organisation's data handling policies and applicable law

## Your responsibilities

You are solely responsible for:

- **Provider selection** — choosing an AI provider whose data handling and privacy practices are appropriate for your codebase
- **Configuration** — storing API keys as repository secrets, not in workflow files or code
- **Legal compliance** — ensuring your use complies with applicable laws and regulations, IP rights, confidentiality agreements, and your provider's terms of service
- **Organisational policy** — confirming use of a third-party AI service is permitted under your organisation's policies before connecting it to your codebase

The authors of this software accept no liability for the content you transmit to third-party AI providers, their data handling practices, or any consequences arising from your configuration and usage decisions.

See the **Data Handling Notice** in [LICENSE](LICENSE) for the full terms. Questions? [spycedconcepts.co.uk/contact](https://spycedconcepts.co.uk/contact)

---

## Security design of this action

- **No secrets in code** — API keys sourced exclusively from repository secrets; never logged or written to any output
- **No shell interpolation of user content** — PR title, body, and review text are passed as environment variables to Python, not shell-interpolated
- **Review posted via file** — review body written to a temp file and posted via `--body-file`; no shell expansion of review content
- **stdlib only** — no external Python dependencies on the runner; zero pip installs
- **Minimal GitHub token scope** — `pull-requests: write` and `contents: read` only; never pushes, merges, or modifies repository settings
- **Adapter isolation** — provider-specific code is in `scripts/adapters/`; the core has no outbound network calls
- **Sensitive data scan first** — every review checks for credentials, personal identifiers, and private paths before any other criterion

---

## Pinning the action version — SHA only

**SHA pinning is the only supported pattern.** Tags are mutable; the maintainer (or anyone who gains access to the repository) can rewrite where a tag points, and consumers' next workflow run would silently execute the new code with their secrets. The widely-publicised `tj-actions/changed-files` compromise (March 2025) is the canonical example of this failure mode. Pinning to a full commit SHA gives cryptographic immutability — the exact code you reviewed is the exact code that will run.

```yaml
# Recommended — pin to a full commit SHA; the comment is human metadata read by Dependabot
- uses: Spyced-Concepts/ReviewSentry@<full-40-char-sha>  # v0.3.2-beta

# Not recommended — any floating or mutable reference
- uses: Spyced-Concepts/ReviewSentry@v0           # floating major-version tag
- uses: Spyced-Concepts/ReviewSentry@v0.3.2-beta  # version tag (still mutable on the producer side)
- uses: Spyced-Concepts/ReviewSentry@main         # tracks moving HEAD
```

The `@v0` floating tag was removed on 2026-05-14 to remove the supply-chain risk class entirely. Anyone still referencing `@v0` should switch to a pinned SHA; their workflow will fail with `repository not found / ref not found` until they do.

**Finding the SHA:** Open the [Releases page](https://github.com/Spyced-Concepts/ReviewSentry/releases), click the release, and copy the full commit SHA. Paste the SHA into your `uses:` line and the version label into the trailing comment.

**Auto-updates with Dependabot:** Add the action to your `.github/dependabot.yml`. Dependabot reads the trailing version comment, compares against the latest release on this repo, and opens a PR updating both the SHA and the comment when a newer release ships. You review the PR like any other.
