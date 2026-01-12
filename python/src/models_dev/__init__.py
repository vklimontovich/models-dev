"""Typed Python interface to models.dev API data.

Example usage:
    from models_dev import providers, get_provider, get_model_by_id

    # Iterate all providers
    for provider in providers():
        print(provider.name, len(provider.models))

    # Get specific provider
    openai = get_provider("openai")
    print(openai.name)  # "OpenAI"

    # Get model by ID
    gpt4o = get_model_by_id("openai", "gpt-4o")
    print(gpt4o.cost.input)  # price per 1M tokens

    # Get model by name
    gpt4o = openai.get_model_by_name("GPT-4o")
"""

from collections.abc import Iterator

from ._loader import _get_providers
from ._types import (
    Cost,
    InputModality,
    Interleaved,
    Limit,
    Modalities,
    Model,
    ModelProvider,
    OutputModality,
    Provider,
    Status,
)

__all__ = [
    "Cost",
    "InputModality",
    "Interleaved",
    "Limit",
    "Modalities",
    "Model",
    "ModelProvider",
    "OutputModality",
    "Provider",
    "Status",
    "get_model_by_id",
    "get_model_by_name",
    "get_provider",
    "providers",
]


def providers() -> Iterator[Provider]:
    """Iterate over all providers."""
    yield from _get_providers().values()


def get_provider(provider_id: str) -> Provider:
    """Get a provider by ID. Raises KeyError if not found."""
    return _get_providers()[provider_id]


def get_model_by_id(provider_id: str, model_id: str) -> Model:
    """Get a model by provider ID and model ID. Raises KeyError if not found."""
    return get_provider(provider_id).models[model_id]


def get_model_by_name(provider_id: str, name: str) -> Model:
    """Get a model by provider ID and model name. Raises KeyError if not found."""
    return get_provider(provider_id).get_model_by_name(name)
