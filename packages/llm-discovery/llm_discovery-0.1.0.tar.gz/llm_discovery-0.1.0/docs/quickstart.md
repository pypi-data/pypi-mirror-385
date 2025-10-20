---
title: Quick Start
description: Quick start guide for llm-discovery
---

# Quick Start

This guide walks you through setting up llm-discovery and running your first commands.

## Zero Configuration Quick Start

Try `llm-discovery` instantly without any API keys using prebuilt model data (updated daily):

```bash
# Display models using prebuilt data (no API keys required)
$ uvx llm-discovery list
```

Expected output:

```
Provider       Model ID              Model Name
─────────────────────────────────────────────────
OpenAI         gpt-4                 GPT-4
OpenAI         gpt-3.5-turbo         GPT-3.5 Turbo
Google         gemini-pro            Gemini Pro
Anthropic      claude-3-opus         Claude 3 Opus

Total models: 42

Data Source: PREBUILT
Last Updated: 2025-10-19 00:00 UTC
Age: 10.5 hours
```

The data source information shows:
- **Data Source**: Whether data comes from `API` (real-time) or `PREBUILT` (daily snapshot)
- **Last Updated**: When the data was generated
- **Age**: How old the data is in hours

:::{note}
Prebuilt data is automatically updated daily at 00:00 UTC via GitHub Actions.
Maximum data age is 24 hours. For real-time data, configure API keys (see below).
:::

:::{warning}
If data is older than 24 hours, a yellow warning will appear.
If data is older than 7 days, a red warning will appear with a recommendation to run `update`.
:::

## Environment Variables (For Real-time Data)

Set up API keys for the LLM providers you want to monitor.

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
```

### Google AI Studio

```bash
export GOOGLE_API_KEY="AIza..."
```

### Google Vertex AI

As an alternative to Google AI Studio, you can use Vertex AI:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gcp-credentials.json"
```

:::{warning}
Never commit API keys to version control.
Store them securely using environment variables or secret management tools.
:::

:::{note}
You can configure any combination of providers.
llm-discovery will fetch models from all providers with configured credentials.
:::

## Basic Commands

### Update: Fetch and Cache Models

Fetch the latest model data from all configured providers:

```bash
$ uvx llm-discovery update
```

Expected output:

```
OpenAI: 15, Google: 20, Anthropic: 7 / Total: 42 / Cached to: ~/.cache/llm-discovery/models_cache.toml
```

:::{tip}
Use `uvx` to run llm-discovery without installation.
This ensures you always use the latest version.
:::

### List: Display Cached Models

Display models in a formatted table:

```bash
$ uvx llm-discovery list
```

Expected output:

```
Provider       Model ID              Model Name
─────────────────────────────────────────────────
OpenAI         gpt-4                 GPT-4
OpenAI         gpt-3.5-turbo         GPT-3.5 Turbo
Google         gemini-pro            Gemini Pro
Anthropic      claude-3-opus         Claude 3 Opus
```

### Export: Save Model Data

Export model data in various formats:

```bash
# Export to JSON
$ uvx llm-discovery export --format json --output models.json

# Export to CSV
$ uvx llm-discovery export --format csv --output models.csv

# Export to YAML
$ uvx llm-discovery export --format yaml --output models.yaml

# Export to Markdown
$ uvx llm-discovery export --format markdown --output models.md

# Export to TOML
$ uvx llm-discovery export --format toml --output models.toml
```

**Data Source Metadata in Exports**:

All export formats include data source information:
- **JSON**: `metadata.data_source`, `metadata.source_timestamp`, `metadata.data_age_hours`
- **CSV**: `data_source` and `source_timestamp` columns
- **Markdown**: "Data Source" section header
- **YAML/TOML**: Standard model data (no additional metadata)

Example JSON export with data source info:

```text
{
  "metadata": {
    "version": "1.0",
    "generated_at": "2025-10-19T10:30:00Z",
    "total_models": 42,
    "providers": ["openai", "google", "anthropic"],
    "data_source": "prebuilt",
    "source_timestamp": "2025-10-19T00:00:00Z",
    "data_age_hours": 10.5
  },
  "models": {
    "openai": [...],
    "google": [...],
    "anthropic": [...]
  }
}
```

## Python API Basic Usage

Use llm-discovery as a library in your Python applications.

### Fetch All Models

```python
import asyncio
from llm_discovery import DiscoveryClient
from llm_discovery.models.config import Config

async def main():
    # Load configuration from environment variables
    config = Config.from_env()
    client = DiscoveryClient(config)

    # Fetch models from all providers
    provider_snapshots = await client.fetch_all_models()

    # Display all models
    for provider in provider_snapshots:
        print(f"\nProvider: {provider.provider_name}")
        print(f"Total models: {len(provider.models)}")
        for model in provider.models:
            print(f"  - {model.model_id}: {model.model_name}")

asyncio.run(main())
```

### Filter Models by Provider

```python
import asyncio
from llm_discovery import DiscoveryClient
from llm_discovery.models.config import Config

async def main():
    config = Config.from_env()
    client = DiscoveryClient(config)

    # Fetch all models
    provider_snapshots = await client.fetch_all_models()

    # Filter OpenAI models only
    openai_models = [
        model for snapshot in provider_snapshots
        if snapshot.provider_name == "openai"
        for model in snapshot.models
    ]

    print(f"OpenAI models: {len(openai_models)}")
    for model in openai_models:
        print(f"  - {model.model_id}")

asyncio.run(main())
```

:::{tip}
The Python API uses `async/await` for efficient concurrent fetching from multiple providers.
Always use `asyncio.run()` or run within an existing async context.
:::

## Offline Mode

llm-discovery operates in cache-first mode, allowing offline usage after initial data fetch.

```bash
# Fetch data while online
$ uvx llm-discovery update

# Use cached data offline (no internet required)
$ uvx llm-discovery list
$ uvx llm-discovery export --format json --output models.json
```

Cache location: `~/.cache/llm-discovery/models_cache.toml`

## Change Detection

Track model additions and removals over time:

```bash
$ uvx llm-discovery update --detect-changes
```

Expected output when changes detected:

```
Added models (3): openai/gpt-4.5, google/gemini-2.0, anthropic/claude-3.5-opus
Removed models (1): openai/gpt-3.5-turbo-0301
```

Changes are recorded in:
- `~/.cache/llm-discovery/changes.json`
- `~/.cache/llm-discovery/CHANGELOG.md`

## Next Steps

For more detailed documentation:

- **API Reference**: See technical contract at `specs/001-llm-model-discovery/contracts/python-api.md`
- **CLI Reference**: See technical contract at `specs/001-llm-model-discovery/contracts/cli-interface.md`
- **Contributing**: See `CONTRIBUTING.md` in the repository root for development guidelines
