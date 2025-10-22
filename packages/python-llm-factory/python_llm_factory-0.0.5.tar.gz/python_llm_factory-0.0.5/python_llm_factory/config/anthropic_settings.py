import os

from pydantic_settings import BaseSettings

from python_llm_factory.config.base_settings import LLMProviderSettings
from python_llm_factory.consts.provider import LLMProvider


class AnthropicBaseSettings(LLMProviderSettings):
    provider: str = LLMProvider.ANTHROPIC.value
    api_key: str = os.getenv("ANTHROPIC_API_KEY") or ""
    default_model: str = "claude-3-5-sonnet-20240620"
    max_tokens: int = 1024


class AnthropicClaude35SonnetSettings(AnthropicBaseSettings):
    default_model: str = "claude-3-5-sonnet-20240620"


class AnthropicSettings(BaseSettings):
    claude_3_5_sonnet: LLMProviderSettings = AnthropicClaude35SonnetSettings()
