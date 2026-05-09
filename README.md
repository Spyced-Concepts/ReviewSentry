# ReviewSentry

**Security-first automated code review for every pull request. Free with GitHub Models — or bring your own Anthropic, OpenAI, or Gemini key.**

No dashboards. No per-review billing. No vendor lock-in. MIT licensed.

> Built by [Spyced Concepts Ltd.](https://spycedconcepts.co.uk) — a security-focused software company.

---

## Why ai-pr-review

Most AI code review tools focus on code quality. This one leads with **security**.

Every review starts with a sensitive data disclosure scan — catching credentials, personal identifiers, private paths, and computer names before they reach your commit history. This criterion runs first, always, before any other finding is reported.

| | ai-pr-review | Typical AI review action |
|---|---|---|
| Sensitive data scan | ✅ First criterion, always | ✗ Not included |
| Free with existing GitHub account | ✅ GitHub Models | ✗ Requires paid AI subscription |
| Multiple providers (your key) | ✅ 5 providers + any OpenAI-compatible | Usually 1–2 |
| Custom scan rules | ✅ Add your own patterns | Rarely |
| MIT open source | ✅ | Sometimes |
| No dashboard or account required | ✅ | Often required |

---

## Supported providers

| Provider | `ai_provider` | Cost | Notes |
|---|---|---|---|
| **GitHub Models** | `github-models` | **Free** | Uses your `GITHUB_TOKEN` — no extra account needed |
| Anthropic | `anthropic` | Per-token | Prompt caching enabled — lower cost on repeated reviews |
| OpenAI | `openai` | Per-token | |
| Google Gemini | `gemini` | Per-token / free tier | |
| Groq | `openai` + `ai_base_url` | Per-token / free tier | Fast inference |
| Azure OpenAI | `openai` + `ai_base_url` | Per-token | Enterprise data handling |
| Ollama (self-hosted) | `openai` + `ai_base_url` | Free | Run locally or on your own server |

**Required fields per provider:**

| Provider | `ai_provider` | `ai_api_key` | `ai_model` | `ai_base_url` | `permissions` |
|---|---|---|---|---|---|
| GitHub Models | `github-models` | `${{ secrets.GITHUB_TOKEN }}` | e.g. `gpt-4o` | not needed | `models: read` |
| Anthropic | `anthropic` | `${{ secrets.AI_API_KEY }}` | e.g. `claude-sonnet-4-6` | not needed | standard |
| OpenAI | `openai` | `${{ secrets.AI_API_KEY }}` | e.g. `gpt-4o` | not needed | standard |
| Groq | `openai` | `${{ secrets.AI_API_KEY }}` | e.g. `llama-3.3-70b-versatile` | `https://api.groq.com/openai` | standard |
| Azure OpenAI | `openai` | `${{ secrets.AI_API_KEY }}` | your deployment name | your Azure endpoint | standard |
| Gemini | `gemini` | `${{ secrets.AI_API_KEY }}` | e.g. `gemini-2.0-flash` | not needed | standard |
| Ollama | `openai` | any value | e.g. `qwen2.5-coder` | your Ollama host | standard |

> **Standard permissions:** `pull-requests: write` and `contents: read`. GitHub Models additionally requires `models: read`.
>
> **Secret and variable names are yours to choose.** The names `AI_API_KEY` and `AI_MODEL` used throughout this documentation are examples only. Store your key under any name you like and reference it with `${{ secrets.YOUR_CHOSEN_NAME }}`. The action only reads what you pass to its inputs — it has no dependency on specific environment variable names.

**Full setup guides:** [`docs/`](docs/)

---

## Quick start

Choose your provider and add the workflow. `ai_provider` is required — no default is set so you make an explicit, informed choice.

**GitHub Models** — free, uses your existing `GITHUB_TOKEN`, no extra account:
```yaml
          ai_api_key:  ${{ secrets.GITHUB_TOKEN }}
          ai_model:    gpt-4o
          ai_provider: github-models
```
> Requires `models: read` in your workflow permissions block.

**Anthropic:**
```yaml
          ai_api_key:  ${{ secrets.YOUR_API_KEY }}
          ai_model:    claude-sonnet-4-6
          ai_provider: anthropic
```

**OpenAI:**
```yaml
          ai_api_key:  ${{ secrets.YOUR_API_KEY }}
          ai_model:    gpt-4o
          ai_provider: openai
```

**Gemini:**
```yaml
          ai_api_key:  ${{ secrets.YOUR_API_KEY }}
          ai_model:    gemini-2.0-flash
          ai_provider: gemini
```

**Full workflow file:**
```yaml
# .github/workflows/ai-review.yml
name: AI PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read
      # models: read   # add this line if using github-models
    steps:
      - uses: actions/checkout@v4
      - uses: Spyced-Concepts/ai-pr-review@v1
        with:
          ai_api_key:   ${{ secrets.YOUR_API_KEY }}
          ai_model:     your-model-identifier
          ai_provider:  your-provider     # anthropic | openai | gemini | github-models
          pr_number:    ${{ github.event.pull_request.number }}
          pr_title:     ${{ github.event.pull_request.title }}
          pr_body:      ${{ github.event.pull_request.body }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

See the [setup guides](docs/) for provider-specific instructions and model lists.

---

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `ai_api_key` | ✓ | — | AI provider API key. Use `${{ secrets.GITHUB_TOKEN }}` for GitHub Models. |
| `ai_model` | ✓ | — | Model identifier — see provider setup guide |
| `ai_provider` | | `anthropic` | Adapter: `anthropic`, `openai`, or `gemini` |
| `ai_base_url` | | `""` | Base URL override for OpenAI-compatible endpoints (GitHub Models, Groq, Azure, Ollama) |
| `pr_number` | ✓ | — | Pull request number |
| `pr_title` | ✓ | — | Pull request title |
| `pr_body` | | `""` | Pull request description |
| `diff_lines` | | `1500` | Max diff lines to send for review. If the diff exceeds this limit it is truncated and the review comment includes a visible warning: `> Diff was large — review based on first N lines only.` The action never fails due to diff size — it always posts a review, with the truncation note prepended when applicable. Reduce this value if you hit AI provider token limits; increase it for large refactors. |
| `review_criteria` | | `""` | Additional review criteria, one per line |
| `custom_rules` | | `""` | Custom sensitive data scan patterns, one per line |
| `github_token` | ✓ | — | GitHub token for posting the review comment |

## Outputs

| Output | Description |
|---|---|
| `review` | The full review text posted as a PR comment |

---

## Review criteria

Every review checks these criteria in order:

1. **Sensitive data disclosure** *(security-first)* — credentials, API keys, personal information, file paths revealing usernames, computer/host names, private repo names. Severity-classified: Critical → High → Moderate. Always reported before any other finding.
2. **Merge conflicts** — immediate blocker
3. **Correctness** — edge cases, logic errors
4. **Cross-platform compatibility** — macOS, Linux, Windows (Git Bash)
5. **Bash quality** — `set -euo pipefail`, quoting, portability
6. **Security** — injection risks, unsafe variable expansion
7. **Code quality** — magic values, code smells, correct approach
8. **Dependencies** — external modules flagged
9. **Documentation** — docs updated alongside code changes
10. **PR scope** — single concern?

Add custom criteria via `review_criteria`. Add domain-specific sensitive data patterns via `custom_rules` (e.g. internal product names, employee identifiers).

---

## Architecture

```
scripts/
  review.py            # Provider-agnostic core — zero vendor references
  adapters/
    anthropic.py       # Anthropic Claude
    openai.py          # OpenAI + any OpenAI-compatible endpoint
    gemini.py          # Google Gemini
docs/
  setup-anthropic.md
  setup-openai.md
  setup-gemini.md
  setup-github-models.md
```

Adding a new provider means implementing one function in a new adapter file. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security and data handling

This action transmits only the PR diff and PR title/body to your chosen AI provider. See [SECURITY.md](SECURITY.md) for:
- Exactly what data is transmitted
- Per-provider data handling policy links
- Your responsibilities when using with private or regulated codebases

**Important:** You are responsible for ensuring your use of this action — and the transmission of code content to third-party AI providers — complies with your applicable legal obligations, IP rights, and your provider's terms of service. See the [Data Handling Notice](LICENSE) in the licence.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). To add a new AI provider, implement `call_api()` in `scripts/adapters/<provider>.py` and add a setup guide in `docs/`. The adapter interface is fully documented.

---

## Licence

MIT — see [LICENSE](LICENSE). Governing law: England and Wales.

Made by [Spyced Concepts Ltd.](https://spycedconcepts.co.uk)
