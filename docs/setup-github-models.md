---
provider: github-models
adapter: github-models
requires_paid_account: false
api_key_source: GITHUB_TOKEN
setup_complexity: minimal
available_models: [gpt-4o, gpt-4o-mini, Meta-Llama-3.1-70B-Instruct, Mistral-large, Phi-3-medium-128k-instruct]
---

# Setup — GitHub Models (zero additional cost)

GitHub Models provides access to leading AI models — including GPT-4o, Llama, Mistral, and Phi — using your existing GitHub token. **No additional account, no billing, no API key to manage.**

If you have a GitHub account, you have everything you need.

---

## Why use GitHub Models

- **Free** — included with your GitHub account (subject to rate limits)
- **No extra credentials** — uses the `GITHUB_TOKEN` that GitHub Actions already provides
- **Wide model choice** — GPT-4o, Meta Llama 3.1, Mistral, Phi-3, and more
- **No data leaves GitHub's infrastructure** for token-based requests

---

## Setup

No secrets or variables to add. The `GITHUB_TOKEN` is automatically available in every GitHub Actions workflow.

### Workflow file

```yaml
# .github/workflows/ai-review.yml
name: AI PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

concurrency:
  group: reviewsentry-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  review:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      pull-requests: write
      models: read          # required for GitHub Models access
    steps:
      - uses: Spyced-Concepts/ReviewSentry@<commit-sha>  # see Releases for latest, e.g. v0.3.3-beta
        with:
          ai_api_key:   ${{ secrets.GITHUB_TOKEN }}
          ai_model:     gpt-4o
          ai_provider:  github-models
          pr_number:    ${{ github.event.pull_request.number }}
          pr_title:     ${{ github.event.pull_request.title }}
          pr_body:      ${{ github.event.pull_request.body }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

That's it. No secrets configuration needed.

---

## Available models

| Model | Identifier | Notes |
|---|---|---|
| GPT-4o | `gpt-4o` | Recommended — strong code understanding |
| GPT-4o mini | `gpt-4o-mini` | Faster, lighter |
| Meta Llama 3.1 70B | `Meta-Llama-3.1-70B-Instruct` | Open weights |
| Meta Llama 3.1 405B | `Meta-Llama-3.1-405B-Instruct` | Largest available |
| Mistral Large | `Mistral-large` | Strong reasoning |
| Phi-3 Medium | `Phi-3-medium-128k-instruct` | Microsoft's compact model |

Check [github.com/marketplace/models](https://github.com/marketplace/models) for the full current list and to test models before committing.

---

## Rate limits

GitHub Models has usage limits that vary by plan and model. If you hit rate limits on large PRs, reduce `diff_lines` or switch to a smaller model. See GitHub's [rate limit documentation](https://docs.github.com/en/github-models/prototyping-with-ai-models#rate-limits) for current limits.

---

## Data handling

Usage of GitHub Models is governed by [GitHub's Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service) and the terms of the underlying model provider. Review these before using with private or sensitive codebases.
