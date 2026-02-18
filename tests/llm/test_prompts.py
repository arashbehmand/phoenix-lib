"""Tests for phoenix_lib.llm.prompts."""

import pytest

from phoenix_lib.llm.prompts import PromptLoader


class TestPromptLoader:
    def test_load_valid_prompt(self, tmp_path):
        prompt_file = tmp_path / "greeting.yaml"
        prompt_file.write_text("template: Hello, {{ name }}!", encoding="utf-8")
        loader = PromptLoader(tmp_path)
        result = loader.load("greeting")
        assert result == "Hello, {{ name }}!"

    def test_load_multiline_template(self, tmp_path):
        content = "template: |\n  Line 1\n  Line 2\n  Line 3"
        (tmp_path / "multi.yaml").write_text(content, encoding="utf-8")
        loader = PromptLoader(tmp_path)
        result = loader.load("multi")
        assert "Line 1" in result
        assert "Line 2" in result

    def test_file_not_found_raises(self, tmp_path):
        loader = PromptLoader(tmp_path)
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent")

    def test_missing_template_key_raises_value_error(self, tmp_path):
        (tmp_path / "bad.yaml").write_text(
            "description: no template here", encoding="utf-8"
        )
        loader = PromptLoader(tmp_path)
        with pytest.raises(ValueError, match="missing 'template' key"):
            loader.load("bad")

    def test_empty_template_raises_value_error(self, tmp_path):
        (tmp_path / "empty.yaml").write_text("template: ", encoding="utf-8")
        loader = PromptLoader(tmp_path)
        with pytest.raises(ValueError):
            loader.load("empty")

    def test_base_dir_stored(self, tmp_path):
        loader = PromptLoader(tmp_path)
        assert loader.base_dir == tmp_path

    def test_name_resolves_to_yaml_extension(self, tmp_path):
        # File must end in .yaml
        prompt_file = tmp_path / "mytest.yaml"
        prompt_file.write_text("template: test content", encoding="utf-8")
        loader = PromptLoader(tmp_path)
        result = loader.load("mytest")
        assert result == "test content"

    def test_extra_yaml_keys_ignored(self, tmp_path):
        content = "template: My prompt\nversion: 1.0\ndescription: Some description\n"
        (tmp_path / "rich.yaml").write_text(content, encoding="utf-8")
        loader = PromptLoader(tmp_path)
        result = loader.load("rich")
        assert result == "My prompt"

    def test_template_with_jinja_vars(self, tmp_path):
        (tmp_path / "jinja.yaml").write_text(
            "template: 'Summarize: {{ text }}'", encoding="utf-8"
        )
        loader = PromptLoader(tmp_path)
        result = loader.load("jinja")
        assert "{{ text }}" in result
