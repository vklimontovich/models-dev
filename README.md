# models-dev

Up-to-date [models.dev](https://models.dev) data as typed packages. No HTTP calls needed.

Available for **Python** and **Node.js**.

## About models.dev

[models.dev](https://models.dev) is a community-maintained catalog of LLM models
([source](https://github.com/anomalyco/models.dev/tree/dev)). It tracks 2000+ models from 75+ providers
(OpenAI, Anthropic, Google, Mistral, etc.) with metadata like pricing, context limits, modalities,
and capabilities. The catalog is updated frequently as new models are released.

This package checks for updates hourly and publishes a new version when changes are detected.

---

## Python

**Zero runtime dependencies** | **~75 KB** installed

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

## Node.js

**Zero runtime dependencies** | **~100 KB** bundle | Works in Node.js and browsers

### Installation

```bash
npm install models-dev
```

### Usage

```typescript
import { providers, getProviderInfo, getModel } from 'models-dev';

// List all providers
for (const p of await providers()) {
  console.log(`${p.name}: ${Object.keys(p.models).length} models`);
}

// Get provider details
const openai = await getProviderInfo('openai');
console.log(openai.env);  // ["OPENAI_API_KEY"]
console.log(openai.doc);  // "https://platform.openai.com/docs/models"

// Get model details
const gpt4o = await getModel('openai', 'gpt-4o');
console.log(gpt4o.cost?.input);       // 2.5 (USD per 1M tokens)
console.log(gpt4o.limit.context);     // 128000
console.log(gpt4o.modalities.input);  // ["text", "image"]
console.log(gpt4o.reasoning);         // false

// Filter models
const all = await providers();
const reasoningModels = all.flatMap(p =>
  Object.values(p.models).filter(m => m.reasoning)
);
```

> **Note:** If you're using Vercel AI SDK, use its built-in registry: `import { openai } from '@ai-sdk/openai'`
