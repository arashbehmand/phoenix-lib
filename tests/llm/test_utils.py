"""Tests for phoenix_lib.llm.utils (normalize_result)."""

from phoenix_lib.llm.utils import normalize_result


class _WithContent:
    def __init__(self, content):
        self.content = content


class _WithText:
    def __init__(self, text):
        self.text = text


class _WithChoices:
    def __init__(self, choices):
        self.choices = choices


class _Choice:
    def __init__(self, text=None, message=None):
        if text is not None:
            self.text = text
        if message is not None:
            self.message = message


class _WithGenerations:
    def __init__(self, generations):
        self.generations = generations


class _Generation:
    def __init__(self, text):
        self.text = text


class TestNormalizeResult:
    # --- Basic types ---

    def test_none_returns_empty_string(self):
        assert normalize_result(None) == ""

    def test_plain_string_returned_as_is(self):
        assert normalize_result("hello") == "hello"

    def test_integer_converted(self):
        result = normalize_result(42)
        assert "42" in result

    def test_float_converted(self):
        result = normalize_result(3.14)
        assert "3.14" in result

    def test_bool_converted(self):
        assert normalize_result(True) in ("True", "true", "1")

    # --- Objects with .content ---

    def test_object_with_string_content(self):
        obj = _WithContent("hello content")
        assert normalize_result(obj) == "hello content"

    def test_object_with_nested_content(self):
        inner = _WithContent("deep value")
        outer = _WithContent(inner)
        assert normalize_result(outer) == "deep value"

    def test_object_with_list_content(self):
        obj = _WithContent(["part1", "part2"])
        result = normalize_result(obj)
        assert "part1" in result
        assert "part2" in result

    # --- Objects with .text ---

    def test_object_with_text_attr(self):
        obj = _WithText("text value")
        assert normalize_result(obj) == "text value"

    # --- Objects with .choices ---

    def test_object_with_choices_text(self):
        choice = _Choice(text="choice text")
        obj = _WithChoices([choice])
        result = normalize_result(obj)
        assert "choice text" in result

    def test_object_with_choices_message(self):
        msg = _WithContent("message content")
        choice = _Choice(message=msg)
        obj = _WithChoices([choice])
        result = normalize_result(obj)
        assert "message content" in result

    # --- Dict payloads ---

    def test_dict_with_content_key(self):
        assert normalize_result({"content": "dict content"}) == "dict content"

    def test_dict_with_choices_list(self):
        payload = {"choices": [{"text": "choice one"}, {"text": "choice two"}]}
        result = normalize_result(payload)
        assert "choice one" in result
        assert "choice two" in result

    def test_dict_with_message_key(self):
        payload = {"message": "msg value"}
        assert normalize_result(payload) == "msg value"

    def test_dict_with_choices_message_key(self):
        payload = {"choices": [{"message": {"content": "msg"}}]}
        result = normalize_result(payload)
        assert "msg" in result

    def test_plain_dict_serialized(self):
        payload = {"key": "value"}
        result = normalize_result(payload)
        assert "key" in result
        assert "value" in result

    # --- .generations ---

    def test_object_with_generations(self):
        gen = _Generation("generated text")
        obj = _WithGenerations([[gen]])
        result = normalize_result(obj)
        assert "generated text" in result

    def test_object_with_flat_generations(self):
        gen = _Generation("flat gen")
        obj = _WithGenerations([gen])
        result = normalize_result(obj)
        assert "flat gen" in result

    # --- Markdown fence stripping ---

    def test_strips_markdown_fence_from_result(self):
        obj = _WithContent('```json\n{"key": 1}\n```')
        result = normalize_result(obj)
        assert not result.startswith("```")

    def test_plain_text_not_affected_by_fence_strip(self):
        assert normalize_result("just text") == "just text"
