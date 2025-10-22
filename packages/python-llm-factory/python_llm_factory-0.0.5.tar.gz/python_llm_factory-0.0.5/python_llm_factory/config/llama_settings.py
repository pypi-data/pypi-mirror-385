from pydantic_settings import BaseSettings

from python_llm_factory.config.base_settings import LLMProviderSettings
from python_llm_factory.consts.provider import LLMProvider


class LlamaBaseSettings(LLMProviderSettings):
    provider: str = LLMProvider.LLAMA.value
    api_key: str = "key"  # required, but not used
    default_model: str = "llama3"
    base_url: str = "http://localhost:11434/v1"


class Llama3Settings(LlamaBaseSettings):
    default_model: str = "llama3"


class LlamaSettings(BaseSettings):
    llama3: LLMProviderSettings = Llama3Settings()
