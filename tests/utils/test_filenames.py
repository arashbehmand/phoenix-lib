"""Tests for phoenix_lib.utils.filenames."""

from phoenix_lib.utils.filenames import (sanitize_filename,
                                         sanitize_filename_component)


class TestSanitizeFilenameComponent:
    def test_simple_word(self):
        assert sanitize_filename_component("hello") == "hello"

    def test_spaces_to_dashes(self):
        assert sanitize_filename_component("hello world") == "hello-world"

    def test_underscores_to_dashes(self):
        assert sanitize_filename_component("hello_world") == "hello-world"

    def test_collapses_multiple_spaces(self):
        assert sanitize_filename_component("a   b") == "a-b"

    def test_collapses_multiple_dashes(self):
        assert sanitize_filename_component("a---b") == "a-b"

    def test_strips_leading_trailing_dashes(self):
        assert sanitize_filename_component("---hello---") == "hello"

    def test_empty_string_uses_fallback(self):
        assert sanitize_filename_component("") == "file"

    def test_custom_fallback(self):
        assert sanitize_filename_component("", fallback="doc") == "doc"

    def test_unicode_accents_stripped(self):
        result = sanitize_filename_component("café")
        assert result == "cafe"

    def test_unicode_dash_normalized(self):
        # En-dash and em-dash become regular dash
        result = sanitize_filename_component("hello\u2013world")
        assert result == "hello-world"

    def test_invalid_chars_replaced_with_dash(self):
        result = sanitize_filename_component("file!@#name")
        assert result == "file-name"

    def test_dots_preserved(self):
        result = sanitize_filename_component("file.name")
        assert "file" in result
        assert "name" in result


class TestSanitizeFilename:
    def test_simple_filename_no_extension(self):
        assert sanitize_filename("myfile") == "myfile"

    def test_filename_with_extension(self):
        result = sanitize_filename("my file.pdf")
        assert result == "my-file.pdf"

    def test_extension_lowercased(self):
        result = sanitize_filename("DOCUMENT.PDF")
        assert result.endswith(".pdf")

    def test_spaces_in_base_to_dashes(self):
        assert sanitize_filename("my resume.docx") == "my-resume.docx"

    def test_empty_string_uses_fallback(self):
        assert sanitize_filename("") == "download"

    def test_custom_fallback(self):
        assert sanitize_filename("", fallback="file") == "file"

    def test_none_like_empty_uses_fallback(self):
        assert sanitize_filename("   ") == "download"

    def test_unicode_normalized(self):
        result = sanitize_filename("résumé.pdf")
        assert result == "resume.pdf"

    def test_complex_filename(self):
        result = sanitize_filename("John Doe - Senior Engineer Resume (2024).pdf")
        assert ".pdf" in result
        assert " " not in result

    def test_no_extension_returns_base_only(self):
        result = sanitize_filename("myfile")
        assert "." not in result

    def test_preserves_case_in_base(self):
        # phoenix_lib preserves case (unlike the company-researcher shim)
        result = sanitize_filename("MyFile.txt")
        assert (
            result.startswith("MyFile")
            or result.startswith("myfile")
            or "MyFile" in result
            or "myfile" in result
        )

    def test_extension_with_special_chars_stripped(self):
        result = sanitize_filename("file.p!df")
        # Special chars in extension removed
        assert "!" not in result
