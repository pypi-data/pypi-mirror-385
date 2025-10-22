from typing import Any

import instructor
from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel

from python_llm_factory.config.base_settings import LLMProviderSettings
from python_llm_factory.consts.provider import LLMProvider


class LLMFactory:
    def __init__(self, settings: LLMProviderSettings) -> None:
        self.settings = settings
        self.client = self._initialize_client()

    def _initialize_client(self) -> Any:
        if self.settings.provider == LLMProvider.OPENAI:
            return instructor.from_openai(
                OpenAI(
                    api_key=self.settings.api_key,
                    base_url=self.settings.base_url
                )
            )
        if self.settings.provider == LLMProvider.ANTHROPIC:
            return instructor.from_anthropic(
                Anthropic(
                    api_key=self.settings.api_key,
                    base_url=self.settings.base_url
                )
            )
        if self.settings.provider == LLMProvider.GEMINI:
            return instructor.from_openai(
                OpenAI(
                    api_key=self.settings.api_key,
                    base_url=self.settings.base_url
                ),
                mode=instructor.Mode.JSON,
            )
        if self.settings.provider == LLMProvider.LLAMA:
            return instructor.from_openai(
                OpenAI(
                    api_key=self.settings.api_key,
                    base_url=self.settings.base_url
                ),
                mode=instructor.Mode.JSON,
            )
        raise ValueError(f"Unsupported LLM provider: {self.settings.provider}")

    def completions_create(
        self,
        messages: list[dict[str, str]],
        response_model: type[list[BaseModel]] | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_retries: int | None = None,
        max_tokens: int | None = None,
        tools: list | None = None,
        tool_choice: list | None = None,
    ) -> Any:
        """
        Create a chat completion with the specified parameters.
        If no parameters are provided, defaults from settings are used.
        if tools and tool_choice are provided, the completion will utilize the specified tools.
        in this case, the "response_model" parameter should be None.
        """
        completion_params = {
            "model": model or self.settings.default_model,
            "temperature": temperature or self.settings.temperature,
            "max_retries": max_retries or self.settings.max_retries,
            "max_tokens": max_tokens or self.settings.max_tokens,
            "response_model": response_model,
            "messages": messages,
        }
        if tools:
            completion_params["tools"] = tools
        if tool_choice:
            completion_params["tool_choice"] = tool_choice
        return self.client.chat.completions.create(**completion_params)

    def completions_parse(
        self,
        response_format: type[BaseModel] | None,
        model: str | None = None,
        temperature: float | None = None,
        messages: list[dict[str, str]] | None = None,
        max_tokens: int | None = None,
    ) -> Any:
        """
        Parse a chat completion with the specified parameters.
        If no parameters are provided, defaults from settings are used.
        """
        completion_params = {
            "model": model or self.settings.default_model,
            "temperature": temperature or self.settings.temperature,
            "max_tokens": max_tokens or self.settings.max_tokens,
            "response_format": response_format,
            "messages": messages,
        }
        return self.client.beta.chat.completions.parse(**completion_params)

    def completions_tools(
        self,
        messages: list[dict[str, str]],
        response_format: type[BaseModel] | None = None,
        model: str | None = None,
        temperature: float | None = None,
        max_retries: int | None = None,
        max_tokens: int | None = None,
        tools: list | None = None,
        tool_choice: list | None = None,
        response_list: list | None = None,
    ) -> Any:
        res = self.completions_create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_retries=max_retries,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
        )
        if response_list is not None:
            response_list.append(res)

        res = self.completions_parse(
            response_format=response_format,
            model=model,
            temperature=temperature,
            messages=messages,
            max_tokens=max_tokens,
        )
        if response_list is not None:
            response_list.append(res)

        return res
