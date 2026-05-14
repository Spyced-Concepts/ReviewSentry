---
provider: gemini
adapter: gemini
requires_paid_account: false
api_key_source: aistudio.google.com
setup_complexity: low
available_models: [gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash]
free_tier: true
prompt_caching: false
---

# Setup — Google Gemini

## Prerequisites

- A Google account with [Google AI Studio](https://aistudio.google.com) access

## 1. Get your API key

1. Open [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API key** → **Create API key**
3. Copy the key

## 2. Add to your repository

- **Secret** `AI_API_KEY`: your Gemini API key
- **Variable** `AI_MODEL`: model identifier (e.g. `gemini-2.0-flash`)

## 3. Model identifiers

| Model | Identifier | Notes |
|---|---|---|
| Gemini 2.0 Flash | `gemini-2.0-flash` | Recommended — fast and capable |
| Gemini 1.5 Pro | `gemini-1.5-pro` | Higher quality; slower |
| Gemini 1.5 Flash | `gemini-1.5-flash` | Lower cost |

Check [ai.google.dev/models](https://ai.google.dev/gemini-api/docs/models/gemini) for the current model list.

## 4. Workflow file

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
    steps:
      - uses: actions/checkout@v4
      - uses: Spyced-Concepts/ReviewSentry@<commit-sha>  # see Releases for latest, e.g. v0.3.2-beta
        with:
          ai_api_key:   ${{ secrets.AI_API_KEY }}
          ai_model:     ${{ vars.AI_MODEL }}
          ai_provider:  gemini
          pr_number:    ${{ github.event.pull_request.number }}
          pr_title:     ${{ github.event.pull_request.title }}
          pr_body:      ${{ github.event.pull_request.body }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

## Pricing

See [ai.google.dev/pricing](https://ai.google.dev/pricing). Gemini 2.0 Flash has a generous free tier.
