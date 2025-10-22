import logging
import os
from functools import lru_cache

from pydantic_settings import BaseSettings

from python_llm_factory.config.anthropic_settings import AnthropicSettings
from python_llm_factory.config.gemini_settings import GeminiSettings
from python_llm_factory.config.llama_settings import LlamaSettings
from python_llm_factory.config.open_ai_settings import OpenAISettings


class Settings(BaseSettings):
    app_name: str = "GenAI Project Template"
    openai: OpenAISettings = OpenAISettings()
    anthropic: AnthropicSettings = AnthropicSettings()
    gemini: GeminiSettings = GeminiSettings()
    llama: LlamaSettings = LlamaSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()


def set_logging_level(level: int = logging.INFO) -> None:
    logging.getLogger("instructor").setLevel(level=level)


def set_debug_mode() -> None:
    # https://python.useinstructor.com/debugging/#example-local-debug-run
    os.environ["LLM_LOGGING_LEVEL"] = "1"


def stop_debug_mode() -> None:
    os.environ["LLM_LOGGING_LEVEL"] = "0"
