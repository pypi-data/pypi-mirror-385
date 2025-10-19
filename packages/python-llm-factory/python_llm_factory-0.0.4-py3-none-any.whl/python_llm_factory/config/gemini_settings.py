import os

from pydantic_settings import BaseSettings

from python_llm_factory.config.base_settings import LLMProviderSettings
from python_llm_factory.consts.provider import LLMProvider


class GeminiBaseSettings(LLMProviderSettings):
    provider: str = LLMProvider.GEMINI.value
    api_key: str = os.getenv("GEMINI_API_KEY") or ""
    default_model: str = "gemini-1.5-flash"
    # default_model: str = "gemini-2.5-flash"
    max_tokens: int = 4096
    base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"


class Gemini15FlashSettings(GeminiBaseSettings):
    default_model: str = "gemini-1.5-flash"
    # default_model: str = "gemini-2.5-flash"


class Gemini25FlashSettings(GeminiBaseSettings):
    default_model: str = "gemini-2.5-flash"


class GeminiSettings(BaseSettings):
    gemini_1_5_flash: LLMProviderSettings = Gemini15FlashSettings()
    gemini_2_5_flash: LLMProviderSettings = Gemini25FlashSettings()
