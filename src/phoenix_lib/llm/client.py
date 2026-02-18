"""Shared LLM client for Phoenix services."""

# pylint: disable=import-error,no-name-in-module

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

try:
    import langfuse as langfuse_module  # pylint: disable=invalid-name
except Exception:  # pylint: disable=broad-exception-caught
    langfuse_module = None  # pylint: disable=invalid-name

from langchain_core.prompts import PromptTemplate
from langchain_litellm import ChatLiteLLM

try:
    from langfuse.langchain import (  # type: ignore
        CallbackHandler as callback_handler_cls,  # pylint: disable=invalid-name
    )
except Exception:  # pylint: disable=broad-exception-caught
    callback_handler_cls = None  # pylint: disable=invalid-name

from phoenix_lib.llm.config import LLMConfig
from phoenix_lib.llm.prompts import PromptLoader
from phoenix_lib.llm.utils import normalize_result
from phoenix_lib.utils.time import utc_timestamp

import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with language models.

    Wraps ChatLiteLLM with Langfuse tracing, YAML prompt loading, and
    structured result normalization. Services instantiate this once and
    inject their service-specific LLMConfig.
    """

    def __init__(self, prompt_loader: PromptLoader, default_llm_config: LLMConfig):
        """Initialize the LLM client.

        Args:
            prompt_loader: Loader for YAML prompt templates.
            default_llm_config: Default model configuration (model + params).
        """
        self.prompt_loader = prompt_loader
        self._default_llm_config = default_llm_config
        self._llm: Optional[ChatLiteLLM] = None
        self._langfuse = None
        self._langfuse_initialized = False

    def _create_llm_from_config(self, llm_config: LLMConfig) -> ChatLiteLLM:
        """Create a ChatLiteLLM instance from an LLMConfig."""
        return ChatLiteLLM(
            model=llm_config.model,
            model_kwargs=llm_config.params if llm_config.params else None,
            callbacks=None,
        )

    def _get_default_llm(self) -> ChatLiteLLM:
        """Return the default LLM instance, creating it lazily if needed."""
        if self._llm is None:
            self._llm = self._create_llm_from_config(self._default_llm_config)
        return self._llm

    def _get_langfuse_client(self):
        """Return Langfuse client lazily, honouring tracing-disabled environments."""
        if self._langfuse_initialized:
            return self._langfuse

        self._langfuse_initialized = True
        tracing_flag = str(os.getenv("LANGCHAIN_TRACING_V2", "")).strip().lower()
        if tracing_flag in {"false", "0", "no", "off"}:
            return None
        if callback_handler_cls is None or langfuse_module is None:
            return None

        try:
            get_client_fn = getattr(langfuse_module, "get_client", None)
            if callable(get_client_fn):
                # pylint: disable=not-callable
                self._langfuse = get_client_fn()
            else:
                self._langfuse = None
        except Exception:  # pylint: disable=broad-exception-caught
            self._langfuse = None

        return self._langfuse

    @staticmethod
    def normalize_result(result: Any) -> str:
        """Convert LangChain/LiteLLM return values into a plain string."""
        return normalize_result(result)

    def render_prompt(self, prompt_name: str, context: Dict[str, Any]) -> str:
        """Render a prompt template with the given context without invoking the LLM.

        Args:
            prompt_name: Name of the YAML prompt template.
            context: Variables to populate the template.

        Returns:
            Rendered prompt string.
        """
        template_text = self.prompt_loader.load(prompt_name)
        prompt = PromptTemplate.from_template(template_text, template_format="jinja2")
        return prompt.format(**context)

    async def generate(
        self,
        prompt_name: str,
        context: Dict[str, Any],
        model: Optional[Union[str, LLMConfig]] = None,
    ) -> str:
        """Generate a text response using the LLM.

        Args:
            prompt_name: Name of the YAML prompt template to use.
            context: Variables to populate the template.
            model: Optional model override — either a model string or an LLMConfig.
                   If None, uses the default configured model.

        Returns:
            Normalized string response.
        """
        template_text = self.prompt_loader.load(prompt_name)
        prompt = PromptTemplate.from_template(template_text, template_format="jinja2")

        if model is not None:
            if isinstance(model, LLMConfig):
                llm_to_use = self._create_llm_from_config(model)
            else:
                llm_to_use = ChatLiteLLM(model=model, callbacks=None)
        else:
            llm_to_use = self._get_default_llm()

        chain = prompt | llm_to_use

        logger.info("llm.generate prompt=%s request_id=%s", prompt_name, context.get("request_id", utc_timestamp()))

        try:
            normalized = await self._invoke_with_tracing(chain, prompt_name, context)
        except Exception as e:
            logger.error("llm.generate.error prompt=%s error=%s", prompt_name, str(e))
            raise

        return normalized

    async def generate_structured(self, prompt_name: str, context: Dict[str, Any]) -> Any:
        """Generate a response and normalize it to primitives.

        Uses the default model. Useful when callers expect primitive types
        (str/dict) rather than LangChain message objects.
        """
        template_text = self.prompt_loader.load(prompt_name)
        prompt = PromptTemplate.from_template(template_text, template_format="jinja2")
        chain = prompt | self._get_default_llm()

        logger.info("llm.generate_structured prompt=%s request_id=%s", prompt_name, context.get("request_id", utc_timestamp()))

        try:
            normalized = await self._invoke_with_tracing(chain, prompt_name, context)
        except Exception as e:
            logger.error("llm.generate_structured.error prompt=%s error=%s", prompt_name, str(e))
            raise

        return normalized

    async def _invoke_with_tracing(self, chain, prompt_name: str, context: Dict[str, Any]) -> str:
        """Invoke a LangChain chain with optional Langfuse tracing."""
        langfuse_client = self._get_langfuse_client()

        if langfuse_client:
            try:
                with langfuse_client.start_as_current_span(  # pylint: disable=not-context-manager
                    name=prompt_name, input=context
                ) as span:
                    langfuse_handler = callback_handler_cls()
                    result = await chain.ainvoke(context, config={"callbacks": [langfuse_handler]})
                    normalized = normalize_result(result)
                    try:
                        span.update_trace(output={"content": normalized})
                    except Exception:  # pylint: disable=broad-exception-caught
                        logger.debug("langfuse.span.update.failed")
            except Exception as e:
                logger.debug("langfuse.span.creation.failed: %s", str(e))
                result = await chain.ainvoke(context)
                normalized = normalize_result(result)

            try:
                flush_fn = getattr(langfuse_client, "flush", None)
                if callable(flush_fn):
                    flush_fn()
            except Exception:  # pylint: disable=broad-exception-caught
                logger.debug("langfuse.flush.failed")
        else:
            result = await chain.ainvoke(context)
            normalized = normalize_result(result)

        return normalized
