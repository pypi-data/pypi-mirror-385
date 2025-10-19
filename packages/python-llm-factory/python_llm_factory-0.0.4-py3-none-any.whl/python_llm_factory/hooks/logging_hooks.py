from collections.abc import Callable
from typing import Any

from custom_python_logger import get_logger, json_pretty_format
from instructor.core import HookName

from python_llm_factory import LLMFactory

logger = get_logger(__name__)


def log_kwargs(**kwargs: Any) -> None:
    logger.debug(f"Function called with kwargs: {json_pretty_format(kwargs)}")


def log_completion_response(messages: list[dict[str, str]]) -> None:
    logger.debug(f"Completion response: {json_pretty_format(messages)}")


def add_logging_hooks(client: LLMFactory, handler: Callable) -> None:
    client.client.on(HookName.COMPLETION_KWARGS, handler)
    logger.info("Completion logging hook registered")


def stop_logging_hooks(client: LLMFactory, handler: Callable) -> None:
    client.client.off(HookName.COMPLETION_KWARGS, handler)
    logger.info("Completion logging hook stopped")
