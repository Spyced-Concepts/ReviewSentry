# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| Latest release on `main` | ✅ |
| Older releases | ✗ — update to the latest release |

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Email: **security@spycedconcepts.co.uk**

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

## Your responsibilities

The authors of this software accept no liability for:
- The content you transmit to third-party AI providers
- The data handling or privacy practices of those providers
- Compliance with any laws, regulations, or contractual obligations applicable to your use case

You are solely responsible for ensuring that your use of this action — and the transmission of code content to your chosen AI provider — complies with your applicable legal obligations, IP rights, confidentiality agreements, and your provider's terms of service.

See the **Data Handling Notice** in [LICENSE](LICENSE) for the full terms.

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

## Pinning the action version

Pin to a release tag rather than `@main` to protect your pipeline from unexpected changes:

```yaml
# Recommended
- uses: Spyced-Concepts/ai-pr-review@v1

# Maximum supply-chain security — pin to a specific commit SHA
- uses: Spyced-Concepts/ai-pr-review@<commit-sha>

# Not recommended — tracks moving HEAD
- uses: Spyced-Concepts/ai-pr-review@main
```

Check the [releases page](https://github.com/Spyced-Concepts/ai-pr-review/releases) for the latest stable version.
