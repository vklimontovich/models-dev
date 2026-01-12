"""Tests for models_dev data integrity."""

import gzip
import json
from pathlib import Path

import pytest

from models_dev import Model, Provider, get_provider, providers

DATA_PATH = Path(__file__).parent.parent / "src" / "models_dev" / "data.json.gz"


class TestDataIntegrity:
    """Test that data.json.gz is valid and loads correctly."""

    def test_data_file_exists(self) -> None:
        assert DATA_PATH.exists(), "data.json.gz must exist"

    def test_data_is_valid_gzip(self) -> None:
        with gzip.open(DATA_PATH, "rt") as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_all_providers_load(self) -> None:
        provider_list = list(providers())
        assert len(provider_list) > 0
        for p in provider_list:
            assert isinstance(p, Provider)
            assert p.id
            assert p.name

    def test_all_models_have_required_fields(self) -> None:
        for provider in providers():
            for model in provider.models.values():
                assert isinstance(model, Model)
                assert model.id
                assert model.name
                assert model.modalities is not None
                assert model.limit is not None


class TestKnownProviders:
    """Test that known providers exist and have expected data."""

    @pytest.mark.parametrize("provider_id", ["openai", "anthropic", "google"])
    def test_major_providers_exist(self, provider_id: str) -> None:
        provider = get_provider(provider_id)
        assert provider.id == provider_id
        assert len(provider.models) > 0

    def test_openai_has_gpt4(self) -> None:
        openai = get_provider("openai")
        model_ids = list(openai.models.keys())
        assert any("gpt-4" in m for m in model_ids)

    def test_anthropic_has_claude(self) -> None:
        anthropic = get_provider("anthropic")
        model_ids = list(anthropic.models.keys())
        assert any("claude" in m for m in model_ids)


class TestModelFields:
    """Test model field types and values."""

    def test_cost_fields_are_numeric(self) -> None:
        for provider in providers():
            for model in provider.models.values():
                if model.cost:
                    if model.cost.input is not None:
                        assert isinstance(model.cost.input, (int, float))
                    if model.cost.output is not None:
                        assert isinstance(model.cost.output, (int, float))

    def test_limit_fields_are_integers(self) -> None:
        for provider in providers():
            for model in provider.models.values():
                if model.limit.context is not None:
                    assert isinstance(model.limit.context, int)
                if model.limit.output is not None:
                    assert isinstance(model.limit.output, int)

    def test_modalities_are_valid(self) -> None:
        valid_input = {"text", "image", "audio", "video", "pdf"}
        valid_output = {"text", "image", "audio", "video"}
        for provider in providers():
            for model in provider.models.values():
                for m in model.modalities.input:
                    assert m in valid_input, f"Invalid input modality: {m}"
                for m in model.modalities.output:
                    assert m in valid_output, f"Invalid output modality: {m}"
