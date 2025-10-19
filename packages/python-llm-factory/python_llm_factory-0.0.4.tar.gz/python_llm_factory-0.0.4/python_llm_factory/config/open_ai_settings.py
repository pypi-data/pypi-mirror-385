import os

from pydantic_settings import BaseSettings

from python_llm_factory.config.base_settings import LLMProviderSettings
from python_llm_factory.consts.provider import LLMProvider


class OpenAIBaseSettings(LLMProviderSettings):
    provider: str = LLMProvider.OPENAI.value
    api_key: str = os.getenv("OPENAI_API_KEY") or ""
    default_model: str = "gpt-4o"


class Gpt4oSettings(OpenAIBaseSettings):
    default_model: str = "gpt-4o"
    temperature: float = 0.7


class OpenAISettings(BaseSettings):
    gpt_4o: LLMProviderSettings = Gpt4oSettings()
