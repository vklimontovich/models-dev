"""Load and deserialize models.dev data into typed objects."""

import gzip
import json
from functools import cache
from pathlib import Path
from typing import Any

from ._types import (
    Cost,
    Interleaved,
    Limit,
    Modalities,
    Model,
    ModelProvider,
    Provider,
)

_DATA_PATH = Path(__file__).parent / "data.json.gz"


def _load_raw_data() -> dict[str, Any]:
    with gzip.open(_DATA_PATH, "rt", encoding="utf-8") as f:
        return json.load(f)


def _load_cost(data: dict[str, Any] | None) -> Cost | None:
    if data is None:
        return None
    return Cost(
        input=data.get("input"),
        output=data.get("output"),
        cache_read=data.get("cache_read"),
        cache_write=data.get("cache_write"),
        reasoning=data.get("reasoning"),
        input_audio=data.get("input_audio"),
        output_audio=data.get("output_audio"),
        context_over_200k=data.get("context_over_200k"),
    )


def _load_limit(data: dict[str, Any]) -> Limit:
    return Limit(
        context=data.get("context"),
        input=data.get("input"),
        output=data.get("output"),
    )


def _load_modalities(data: dict[str, Any]) -> Modalities:
    return Modalities(
        input=tuple(data.get("input", [])),
        output=tuple(data.get("output", [])),
    )


def _load_interleaved(data: dict[str, Any] | bool | None) -> Interleaved | None:
    if data is None or data is False:
        return None
    if data is True:
        return Interleaved()
    return Interleaved(field=data.get("field"))


def _load_model_provider(data: dict[str, Any] | None) -> ModelProvider | None:
    if data is None:
        return None
    return ModelProvider(npm=data["npm"])


def _load_model(data: dict[str, Any]) -> Model:
    return Model(
        id=data["id"],
        name=data["name"],
        attachment=data["attachment"],
        reasoning=data["reasoning"],
        tool_call=data["tool_call"],
        open_weights=data["open_weights"],
        release_date=data["release_date"],
        last_updated=data["last_updated"],
        modalities=_load_modalities(data["modalities"]),
        limit=_load_limit(data["limit"]),
        family=data.get("family"),
        structured_output=data.get("structured_output"),
        temperature=data.get("temperature"),
        knowledge=data.get("knowledge"),
        cost=_load_cost(data.get("cost")),
        status=data.get("status"),
        interleaved=_load_interleaved(data.get("interleaved")),
        provider=_load_model_provider(data.get("provider")),
    )


def _load_provider(data: dict[str, Any]) -> Provider:
    models = {mid: _load_model(mdata) for mid, mdata in data["models"].items()}
    return Provider(
        id=data["id"],
        name=data["name"],
        env=tuple(data["env"]),
        npm=data["npm"],
        doc=data["doc"],
        models=models,
        api=data.get("api"),
    )


@cache
def _get_providers() -> dict[str, Provider]:
    raw = _load_raw_data()
    return {pid: _load_provider(pdata) for pid, pdata in raw.items()}
