from pydantic_settings import BaseSettings


class LLMProviderSettings(BaseSettings):
    temperature: float = 0
    max_tokens: int | None = None
    max_retries: int = 3
    base_url : str | None = None
