"""OpenAI Agents SDK instrumentation."""

from typing import ContextManager

from atla_insights.constants import LLM_PROVIDER_TYPE
from atla_insights.frameworks.utils import get_instrumentors_for_provider
from atla_insights.main import ATLA_INSTANCE
from atla_insights.suppression import NoOpContextManager, is_instrumentation_suppressed


def instrument_openai_agents(
    llm_provider: LLM_PROVIDER_TYPE = "openai",
    exclusive_processor: bool = False,
) -> ContextManager[None]:
    """Instrument the OpenAI Agents SDK.

    This function creates a context manager that instruments the OpenAI Agents SDK, within
    its context.

    See [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/) for usage
    details on the SDK itself.

    ```py
    from atla_insights import instrument_openai_agents

    with instrument_openai_agents():
        # My OpenAI Agents SDK code here
    ```

    :param llm_provider (LLM_PROVIDER_TYPE): The LLM provider(s) to instrument. Defaults
        to "openai".
    :param exclusive_processor (bool): Whether to use Atla as the exclusive trace
        processor. When enabled, traces will only be sent to Atla and not to OpenAI.
        Defaults to False.
    :return (ContextManager[None]): A context manager that instruments OpenAI Agents SDK.
    """
    if is_instrumentation_suppressed():
        return NoOpContextManager()

    from atla_insights.frameworks.instrumentors.openai_agents import (
        AtlaOpenAIAgentsInstrumentor,
    )

    # Create an instrumentor for the OpenAI Agents SDK.
    openai_agents_instrumentor = AtlaOpenAIAgentsInstrumentor(exclusive_processor)

    # Create an instrumentor for the underlying LLM provider(s).
    llm_provider_instrumentors = get_instrumentors_for_provider(llm_provider)

    return ATLA_INSTANCE.instrument_service(
        service=AtlaOpenAIAgentsInstrumentor.name,
        instrumentors=[openai_agents_instrumentor, *llm_provider_instrumentors],
    )


def uninstrument_openai_agents() -> None:
    """Uninstrument the OpenAI Agents SDK."""
    if is_instrumentation_suppressed():
        return

    from atla_insights.frameworks.instrumentors.openai_agents import (
        AtlaOpenAIAgentsInstrumentor,
    )

    return ATLA_INSTANCE.uninstrument_service(AtlaOpenAIAgentsInstrumentor.name)
