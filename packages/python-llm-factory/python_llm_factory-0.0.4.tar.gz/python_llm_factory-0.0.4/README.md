# llm-factory
A flexible Python factory for working with multiple Large Language Model (LLM) providers (OpenAI, Anthropic, Gemini, Llama) using a unified interface, with robust configuration and extensibility.

---

## Features
- ✅ Unified interface for multiple LLM providers (OpenAI, Anthropic, Gemini, Llama)
- ✅ Easy provider switching via configuration
- ✅ Pydantic-based response validation
- ✅ Environment variable-based secure configuration
- ✅ Extensible for new providers
- ✅ Supports model, temperature, max tokens, and retries per provider

---

## Installation
```bash
pip install python-llm-factory
```

---

## Configuration
The package uses environment variables for authentication and configuration. You can set these in a `.env` file or your environment:

```bash
# Required environment variables for each provider
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## Examples

### Basic Usage: Creating a Completion

```python
from pydantic import BaseModel, Field
from python_llm_factory import LLMFactory
from python_llm_factory import Settings


class CompletionModel(BaseModel):
    response: str = Field(description="Your response to the user.")
    reasoning: str = Field(description="Explain your reasoning for the response.")


messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "If it takes 2 hours to dry 1 shirt out in the sun, how long will it take to dry 5 shirts?"},
]

llm = LLMFactory(
    settings=Settings().gemini.gemini_2_5_flash,
)
completion = llm.completions_create(
    response_model=CompletionModel,
    messages=messages,
)
print(f"Response: {completion.response}\n")
print(f"Reasoning: {completion.reasoning}")
```

---

## 🤝 Contributing
If you have a helpful tool, pattern, or improvement to suggest:
- Fork the repo <br>
- Create a new branch <br>
- Submit a pull request <br>
I welcome additions that promote clean, productive, and maintainable development. <br>

---

## 🙏 Thanks
Thanks for exploring this repository! <br>
Happy coding! <br>
