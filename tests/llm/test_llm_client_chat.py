"""Tests for LLMClient.generate_chat method."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


@pytest.mark.asyncio
async def test_SCHAT_LIB_001_generate_chat_returns_string():
    """generate_chat sends messages to LLM and returns normalized string."""
    from phoenix_lib.llm.client import LLMClient
    from phoenix_lib.llm.config import LLMConfig
    from phoenix_lib.llm.prompts import PromptLoader

    mock_loader = MagicMock(spec=PromptLoader)
    config = LLMConfig(model="openai/gpt-4o", params={})
    client = LLMClient(prompt_loader=mock_loader, default_llm_config=config)

    fake_llm = AsyncMock()
    fake_llm.ainvoke = AsyncMock(return_value=MagicMock(content="The answer is 42"))
    client._llm = fake_llm

    messages = [SystemMessage(content="You are helpful."), HumanMessage(content="What is 6*7?")]
    result = await client.generate_chat(messages)

    assert result == "The answer is 42"
    fake_llm.ainvoke.assert_called_once_with(messages)


@pytest.mark.asyncio
async def test_SCHAT_LIB_002_generate_chat_with_model_override():
    """generate_chat uses the model override when provided."""
    from phoenix_lib.llm.client import LLMClient
    from phoenix_lib.llm.config import LLMConfig
    from phoenix_lib.llm.prompts import PromptLoader

    mock_loader = MagicMock(spec=PromptLoader)
    config = LLMConfig(model="openai/gpt-4o", params={})
    client = LLMClient(prompt_loader=mock_loader, default_llm_config=config)

    messages = [HumanMessage(content="Hello")]
    with patch("phoenix_lib.llm.client.ChatLiteLLM") as MockLLM:
        instance = AsyncMock()
        instance.ainvoke = AsyncMock(return_value=MagicMock(content="Hi there"))
        MockLLM.return_value = instance
        result = await client.generate_chat(messages, model="anthropic/claude-3-5-sonnet")
        MockLLM.assert_called_once_with(model="anthropic/claude-3-5-sonnet", callbacks=None)
        assert result == "Hi there"
