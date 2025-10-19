from collections.abc import Callable

from custom_python_logger import get_logger
from instructor.core import HookName

from python_llm_factory import LLMFactory

logger = get_logger(__name__)


def log_exception(exception: Exception) -> None:
    logger.debug(f"An exception occurred: {str(exception)}")


def add_error_hooks(client: LLMFactory, handler: Callable) -> None:
    client.client.on(HookName.COMPLETION_ERROR, handler)
    logger.info(f"Completion hook registered for {client.client.name}")


def stop_error_hooks(client: LLMFactory, handler: Callable) -> None:
    client.client.off(HookName.COMPLETION_ERROR, handler)
    logger.info(f"Completion hook stopped for {client.client.name}")
