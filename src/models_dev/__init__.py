"""Typed Python interface to models.dev API data.

Example usage:
    from models_dev import providers, get_provider, get_model

    # Iterate all providers
    for provider in providers():
        print(provider.name, len(provider.models))

    # Get specific provider
    openai = get_provider("openai")
    print(openai.name)  # "OpenAI"

    # Get specific model
    gpt4o = get_model("openai", "gpt-4o")
    print(gpt4o.cost.input)  # price per 1M tokens
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
    "get_model",
    "get_provider",
    "providers",
]


def providers() -> Iterator[Provider]:
    """Iterate over all providers."""
    yield from _get_providers().values()


def get_provider(provider_id: str) -> Provider:
    """Get a provider by ID.

    Args:
        provider_id: Provider identifier (e.g., "openai", "anthropic")

    Returns:
        Provider object

    Raises:
        KeyError: If provider not found
    """
    return _get_providers()[provider_id]


def get_model(provider_id: str, model_id: str) -> Model:
    """Get a model by provider and model ID.

    Args:
        provider_id: Provider identifier (e.g., "openai")
        model_id: Model identifier (e.g., "gpt-4o")

    Returns:
        Model object

    Raises:
        KeyError: If provider or model not found
    """
    return get_provider(provider_id).models[model_id]
