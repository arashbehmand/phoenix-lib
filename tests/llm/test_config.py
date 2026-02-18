"""Tests for phoenix_lib.llm.config."""

from phoenix_lib.llm.config import LLMConfig


class TestLLMConfig:
    def test_default_model(self):
        cfg = LLMConfig()
        assert cfg.model == "openai/gpt-4o-mini"

    def test_default_params_empty(self):
        cfg = LLMConfig()
        assert cfg.params == {}

    def test_custom_model(self):
        cfg = LLMConfig(model="anthropic/claude-3-5-sonnet")
        assert cfg.model == "anthropic/claude-3-5-sonnet"

    def test_custom_params(self):
        cfg = LLMConfig(
            model="openai/gpt-4o", params={"temperature": 0.7, "max_tokens": 1024}
        )
        assert cfg.params["temperature"] == 0.7
        assert cfg.params["max_tokens"] == 1024

    def test_is_pydantic_model(self):
        from pydantic import BaseModel

        assert issubclass(LLMConfig, BaseModel)

    def test_serialization(self):
        cfg = LLMConfig(model="openai/gpt-4o", params={"temperature": 0.5})
        d = cfg.model_dump()
        assert d["model"] == "openai/gpt-4o"
        assert d["params"]["temperature"] == 0.5

    def test_from_dict(self):
        cfg = LLMConfig(
            **{"model": "openai/gpt-4o-mini", "params": {"temperature": 0.0}}
        )
        assert cfg.model == "openai/gpt-4o-mini"

    def test_thinking_level_in_params(self):
        cfg = LLMConfig(
            model="anthropic/claude-3-5-sonnet", params={"thinking_level": "high"}
        )
        assert cfg.params["thinking_level"] == "high"

    def test_independent_params_instances(self):
        # Ensure default_factory creates separate dicts for each instance
        cfg1 = LLMConfig()
        cfg2 = LLMConfig()
        cfg1.params["temperature"] = 0.9
        assert "temperature" not in cfg2.params
