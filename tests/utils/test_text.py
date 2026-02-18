"""Tests for phoenix_lib.utils.text."""

from phoenix_lib.utils.text import strip_markdown_code_fences


class TestStripMarkdownCodeFences:
    def test_plain_text_unchanged(self):
        assert strip_markdown_code_fences("hello world") == "hello world"

    def test_none_returned_as_is(self):
        assert strip_markdown_code_fences(None) is None

    def test_empty_string_unchanged(self):
        assert strip_markdown_code_fences("") == ""

    def test_non_string_returned_as_is(self):
        assert strip_markdown_code_fences(42) == 42

    def test_strips_json_fence(self):
        text = '```json\n{"key": "value"}\n```'
        assert strip_markdown_code_fences(text) == '{"key": "value"}'

    def test_strips_generic_fence(self):
        text = "```\nhello\n```"
        assert strip_markdown_code_fences(text) == "hello"

    def test_strips_uppercase_language_fence(self):
        text = "```JSON\n{}\n```"
        assert strip_markdown_code_fences(text) == "{}"

    def test_strips_python_fence(self):
        text = "```python\ndef foo(): pass\n```"
        assert strip_markdown_code_fences(text) == "def foo(): pass"

    def test_strips_fence_with_leading_whitespace(self):
        text = "  ```json\n{}\n```"
        # Stripped, then pattern checks
        assert strip_markdown_code_fences(text) == "{}"

    def test_no_strip_partial_fence_at_start(self):
        text = "some text\n```json\n{}\n```"
        assert strip_markdown_code_fences(text) == text

    def test_no_strip_no_closing_fence(self):
        text = "```json\n{}"
        assert strip_markdown_code_fences(text) == text

    def test_multiline_content_preserved(self):
        text = "```json\nline1\nline2\nline3\n```"
        result = strip_markdown_code_fences(text)
        assert "line1" in result
        assert "line2" in result
        assert "line3" in result

    def test_already_plain_json(self):
        text = '{"key": "value"}'
        assert strip_markdown_code_fences(text) == text

    def test_fence_with_hyphen_in_language(self):
        text = "```shell-session\nls -la\n```"
        assert strip_markdown_code_fences(text) == "ls -la"
