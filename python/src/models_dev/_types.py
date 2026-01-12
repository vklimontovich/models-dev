"""Type definitions for models.dev data structures."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

InputModality = Literal["text", "image", "audio", "video", "pdf"]
OutputModality = Literal["text", "image", "audio", "video"]
Status = Literal["alpha", "deprecated"]


@dataclass(frozen=True, slots=True)
class Cost:
    """Model pricing in USD per 1M tokens."""

    input: float | None = None
    output: float | None = None
    cache_read: float | None = None
    cache_write: float | None = None
    reasoning: float | None = None
    input_audio: float | None = None
    output_audio: float | None = None
    context_over_200k: float | None = None


@dataclass(frozen=True, slots=True)
class Limit:
    """Model token limits."""

    context: int | None = None
    input: int | None = None
    output: int | None = None


@dataclass(frozen=True, slots=True)
class Modalities:
    """Supported input/output modalities."""

    input: tuple[InputModality, ...]
    output: tuple[OutputModality, ...]


@dataclass(frozen=True, slots=True)
class Interleaved:
    """Streaming reasoning configuration."""

    field: str | None = None


@dataclass(frozen=True, slots=True)
class ModelProvider:
    """SDK override for cross-provider models."""

    npm: str


@dataclass(frozen=True, slots=True)
class Model:
    """AI model metadata."""

    id: str
    name: str
    attachment: bool
    reasoning: bool
    tool_call: bool
    open_weights: bool
    release_date: str
    last_updated: str
    modalities: Modalities
    limit: Limit
    family: str | None = None
    structured_output: bool | None = None
    temperature: bool | None = None
    knowledge: str | None = None
    cost: Cost | None = None
    status: Status | None = None
    interleaved: Interleaved | None = None
    provider: ModelProvider | None = None


@dataclass(frozen=True, slots=True)
class Provider:
    """AI provider metadata."""

    id: str
    name: str
    env: tuple[str, ...]
    npm: str
    doc: str
    models: Mapping[str, Model]
    api: str | None = None

    def get_model_by_id(self, model_id: str) -> Model:
        """Get model by ID. Raises KeyError if not found."""
        return self.models[model_id]

    def get_model_by_name(self, name: str) -> Model:
        """Get model by name. Raises KeyError if not found."""
        for model in self.models.values():
            if model.name == name:
                return model
        raise KeyError(f"Model with name '{name}' not found")
