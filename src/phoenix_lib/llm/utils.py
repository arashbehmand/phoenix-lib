"""LLM output normalization utilities."""

import json
from typing import Any

from phoenix_lib.utils.text import strip_markdown_code_fences


def normalize_result(result: Any) -> str:
    """Convert LangChain/LiteLLM return values into a plain string.

    Handles objects with .content, .choices, .message, .generations, dict payloads,
    and plain strings. This ensures downstream code (and Pydantic) only sees
    primitives.
    """
    # pylint: disable=too-many-nested-blocks

    def _extract_text(value: Any) -> str:
        """Best-effort text extraction without serializing rich third-party models."""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float, bool)):
            return str(value)
        if isinstance(value, dict):
            if "content" in value:
                return _extract_text(value["content"])
            normalized = {str(k): _extract_text(v) for k, v in value.items()}
            return json.dumps(normalized, ensure_ascii=False)
        if isinstance(value, (list, tuple)):
            parts = [_extract_text(v) for v in value]
            return "\n".join(p for p in parts if p)
        if hasattr(value, "content"):
            try:
                return _extract_text(value.content)
            except Exception:  # pylint: disable=broad-exception-caught
                return ""
        if hasattr(value, "text"):
            try:
                return _extract_text(value.text)
            except Exception:  # pylint: disable=broad-exception-caught
                return ""
        if hasattr(value, "model_dump"):
            try:
                dumped = value.model_dump(
                    mode="json", exclude_none=True, warnings=False
                )
            except TypeError:
                dumped = value.model_dump(mode="json", exclude_none=True)
            except Exception:  # pylint: disable=broad-exception-caught
                dumped = None
            if dumped is not None:
                return _extract_text(dumped)
        try:
            return repr(value)
        except Exception:  # pylint: disable=broad-exception-caught
            return ""

    output = ""

    if result is None:
        pass
    elif isinstance(result, str):
        output = result
    elif hasattr(result, "content"):
        output = _extract_text(result.content)
    elif hasattr(result, "choices"):
        choices = result.choices
        try:
            if isinstance(choices, (list, tuple)):
                texts = []
                for c in choices:
                    if hasattr(c, "message"):
                        texts.append(_extract_text(c.message))
                    elif hasattr(c, "text"):
                        texts.append(_extract_text(c.text))
                    else:
                        texts.append(_extract_text(c))
                output = "\n".join(t for t in texts if t)
            else:
                output = _extract_text(choices)
        except Exception:  # pylint: disable=broad-exception-caught
            output = _extract_text(result)
    elif isinstance(result, dict):
        if "choices" in result and isinstance(result["choices"], (list, tuple)):
            texts = []
            for item in result["choices"]:
                if isinstance(item, dict):
                    if "message" in item:
                        texts.append(_extract_text(item["message"]))
                    elif "text" in item:
                        texts.append(_extract_text(item["text"]))
                    else:
                        texts.append(_extract_text(item))
                elif hasattr(item, "message"):
                    texts.append(_extract_text(item.message))
                else:
                    texts.append(_extract_text(item))
            output = "\n".join(t for t in texts if t)
        elif "message" in result:
            output = _extract_text(result["message"])
        else:
            output = _extract_text(result)
    elif hasattr(result, "generations"):
        gens = result.generations
        try:
            texts = []
            for g in gens:
                if isinstance(g, (list, tuple)):
                    for e in g:
                        if hasattr(e, "text"):
                            texts.append(_extract_text(e.text))
                        elif hasattr(e, "content"):
                            texts.append(_extract_text(e.content))
                        else:
                            texts.append(_extract_text(e))
                else:
                    if hasattr(g, "text"):
                        texts.append(_extract_text(g.text))
                    elif hasattr(g, "content"):
                        texts.append(_extract_text(g.content))
                    else:
                        texts.append(_extract_text(g))
            output = "\n".join(t for t in texts if t)
        except Exception:  # pylint: disable=broad-exception-caught
            pass
    else:
        output = _extract_text(result)

    # Strip markdown code fences if the entire output is wrapped in them
    output = strip_markdown_code_fences(output)

    return output
