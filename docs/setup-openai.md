---
provider: openai
adapter: openai
requires_paid_account: true
api_key_source: platform.openai.com
setup_complexity: low
available_models: [gpt-4o, gpt-4o-mini, o1-mini]
compatible_endpoints: [groq, azure-openai, mistral, ollama, github-models]
prompt_caching: false
---

# Setup — OpenAI (and OpenAI-compatible providers)

The OpenAI adapter works with any provider that implements the OpenAI Chat Completions API — including Groq, Azure OpenAI, Mistral, Ollama, and others.

## OpenAI

### 1. Get your API key

1. Open [platform.openai.com](https://platform.openai.com)
2. Go to **API Keys** → **Create new secret key**
3. Copy the key (starts with `sk-`)

### 2. Add to your repository

- **Secret** `AI_API_KEY`: your OpenAI API key
- **Variable** `AI_MODEL`: model identifier (e.g. `gpt-4o`)

### 3. Model identifiers

| Model | Identifier | Notes |
|---|---|---|
| GPT-4o | `gpt-4o` | Best balance of speed and quality |
| GPT-4o mini | `gpt-4o-mini` | Faster; lower cost |
| o1-mini | `o1-mini` | Reasoning model |

### 4. Workflow file

```yaml
- uses: Spyced-Concepts/ReviewSentry@<commit-sha>  # see Releases for latest, e.g. v0.3.2-beta
  with:
    ai_api_key:   ${{ secrets.AI_API_KEY }}
    ai_model:     ${{ vars.AI_MODEL }}
    ai_provider:  openai
    pr_number:    ${{ github.event.pull_request.number }}
    pr_title:     ${{ github.event.pull_request.title }}
    pr_body:      ${{ github.event.pull_request.body }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

---

## Groq (fast inference)

Use the OpenAI adapter with a custom base URL:

```yaml
- uses: Spyced-Concepts/ReviewSentry@<commit-sha>  # see Releases for latest, e.g. v0.3.2-beta
  with:
    ai_api_key:   ${{ secrets.AI_API_KEY }}   # your Groq API key
    ai_model:     llama-3.3-70b-versatile
    ai_provider:  openai
    ai_base_url:  https://api.groq.com/openai
    pr_number:    ${{ github.event.pull_request.number }}
    pr_title:     ${{ github.event.pull_request.title }}
    pr_body:      ${{ github.event.pull_request.body }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

Get a Groq API key at [console.groq.com](https://console.groq.com).

---

## Azure OpenAI

```yaml
- uses: Spyced-Concepts/ReviewSentry@<commit-sha>  # see Releases for latest, e.g. v0.3.2-beta
  with:
    ai_api_key:   ${{ secrets.AI_API_KEY }}   # Azure OpenAI key
    ai_model:     your-deployment-name
    ai_provider:  openai
    ai_base_url:  https://YOUR_RESOURCE.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT
    pr_number:    ${{ github.event.pull_request.number }}
    pr_title:     ${{ github.event.pull_request.title }}
    pr_body:      ${{ github.event.pull_request.body }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

---

## Ollama (self-hosted)

For self-hosted Ollama accessible from your runner:

```yaml
- uses: Spyced-Concepts/ReviewSentry@<commit-sha>  # see Releases for latest, e.g. v0.3.2-beta
  with:
    ai_api_key:   ollama          # Ollama ignores the key; any value works
    ai_model:     qwen2.5-coder
    ai_provider:  openai
    ai_base_url:  http://your-ollama-host:11434/v1
    pr_number:    ${{ github.event.pull_request.number }}
    pr_title:     ${{ github.event.pull_request.title }}
    pr_body:      ${{ github.event.pull_request.body }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
```
