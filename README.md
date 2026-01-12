# models-dev

Up-to-date [models.dev](https://models.dev) data as typed packages. No HTTP calls needed.

Available for **Python** and **Node.js** (coming soon).

## About models.dev

[models.dev](https://models.dev) is a community-maintained catalog of LLM models
([source](https://github.com/anomalyco/models.dev/tree/dev)). It tracks 2000+ models from 75+ providers
(OpenAI, Anthropic, Google, Mistral, etc.) with metadata like pricing, context limits, modalities,
and capabilities. The catalog is updated frequently as new models are released.

This package checks for updates hourly and publishes a new version when changes are detected.

---

## Python

### Installation

```bash
pip install models-dev
```

### Usage

```python
from models_dev import providers, get_provider, get_model

# List all providers
for p in providers():
    print(f"{p.name}: {len(p.models)} models")

# Get provider details
openai = get_provider("openai")
print(openai.env)  # ["OPENAI_API_KEY"]
print(openai.doc)  # "https://platform.openai.com/docs/models"

# Get model details
gpt4o = get_model("openai", "gpt-4o")
print(gpt4o.cost.input)        # 2.5 (USD per 1M tokens)
print(gpt4o.limit.context)     # 128000
print(gpt4o.modalities.input)  # ("text", "image")
print(gpt4o.reasoning)         # False

# Filter models
reasoning_models = [
    m for p in providers()
    for m in p.models.values()
    if m.reasoning
]
```

---

## Node.js (coming soon)

The Node.js package will be isomorphic - works in both Node.js and browser environments.

```typescript
import { providers, getProvider, getModel } from 'models-dev';

const openai = getProvider('openai');
const gpt4o = getModel('openai', 'gpt-4o');
```

> **Note:** If you're using Vercel AI SDK, use its built-in registry: `import { openai } from '@ai-sdk/openai'`
