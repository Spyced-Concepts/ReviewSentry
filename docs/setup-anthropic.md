---
provider: anthropic
adapter: anthropic
requires_paid_account: true
api_key_source: console.anthropic.com
setup_complexity: low
available_models: [claude-sonnet-4-6, claude-opus-4-7, claude-haiku-4-5-20251001]
prompt_caching: true
---

# Setup — Anthropic

## Prerequisites

- An [Anthropic account](https://console.anthropic.com) with API access

## 1. Get your API key

1. Open [console.anthropic.com](https://console.anthropic.com)
2. Go to **API Keys** → **Create Key**
3. Copy the key (starts with `sk-ant-`)

## 2. Add to your repository

In your GitHub repository:

- **Settings → Secrets and variables → Actions → Secrets**
  - Name: `AI_API_KEY`
  - Value: your API key

- **Settings → Secrets and variables → Actions → Variables**
  - Name: `AI_MODEL`
  - Value: the model identifier (see below)

## 3. Model identifiers

| Model | Identifier | Notes |
|---|---|---|
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | Recommended — best balance of speed and quality |
| Claude Opus 4.7 | `claude-opus-4-7` | Highest quality; slower and more expensive |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | Fastest; lower cost |

Check [docs.anthropic.com/models](https://docs.anthropic.com/en/docs/about-claude/models) for the current model list.

## 4. Workflow file

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
    steps:
      - uses: Spyced-Concepts/ReviewSentry@<commit-sha>  # see Releases for latest, e.g. v0.3.3-beta
        with:
          ai_api_key:   ${{ secrets.AI_API_KEY }}
          ai_model:     ${{ vars.AI_MODEL }}
          ai_provider:  anthropic
          pr_number:    ${{ github.event.pull_request.number }}
          pr_title:     ${{ github.event.pull_request.title }}
          pr_body:      ${{ github.event.pull_request.body }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

## Prompt caching

The Anthropic adapter uses [prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) on the system prompt. This reduces cost and latency when reviewing multiple PRs with the same prompt structure.

## Pricing

See [anthropic.com/pricing](https://www.anthropic.com/pricing). With prompt caching, the system prompt is only billed on cache miss.
