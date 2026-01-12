# models-dev

Up-to-date [models.dev](https://models.dev) data as a typed Python package. No HTTP calls needed.

Data is refreshed hourly via automated CI.

## Install

```bash
pip install models-dev
```

## Usage

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
