"""Text utility functions."""

import re


def strip_markdown_code_fences(text: str) -> str:
    """Strip markdown code fences from text if the entire content is wrapped in them.

    Handles patterns like:
    - ```json\\n{...}\\n```
    - ```\\n{...}\\n```
    - ```JSON\\n{...}\\n```

    Only strips if the text starts with ``` and ends with ```.
    """
    if not text or not isinstance(text, str):
        return text

    stripped = text.strip()

    if not stripped.startswith("```"):
        return text

    # Match ``` with optional language identifier at start, content, and ``` at end
    pattern = r"^```[a-zA-Z0-9_-]*\n(.+)\n?```$"
    match = re.match(pattern, stripped, re.DOTALL)
    if match:
        return match.group(1).strip()

    # Also try without language identifier but with newline
    pattern_no_lang = r"^```\n(.+)\n?```$"
    match_no_lang = re.match(pattern_no_lang, stripped, re.DOTALL)
    if match_no_lang:
        return match_no_lang.group(1).strip()

    return text
