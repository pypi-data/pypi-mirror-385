"""Core functionality for the atla_insights package."""

import logging
import os
from contextlib import contextmanager
from typing import ContextManager, Optional, Sequence

from opentelemetry.instrumentation.instrumentor import (  # type: ignore[attr-defined]
    BaseInstrumentor,
)
from opentelemetry.sdk.environment_variables import OTEL_ATTRIBUTE_COUNT_LIMIT
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    SimpleSpanProcessor,
)
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.trace import Tracer, set_tracer_provider

from atla_insights.console_span_exporter import ConsoleSpanExporter
from atla_insights.constants import (
    DEFAULT_OTEL_ATTRIBUTE_COUNT_LIMIT,
    OTEL_MODULE_NAME,
)
from atla_insights.environment import resolve_environment
from atla_insights.id_generator import NoSeedIdGenerator
from atla_insights.metadata import set_global_metadata
from atla_insights.sampling import SamplerType, _TailSampler
from atla_insights.span_processors import AtlaRootSpanProcessor, get_atla_span_exporter
from atla_insights.utils import maybe_get_existing_tracer_provider

logger = logging.getLogger(OTEL_MODULE_NAME)


# Override the OTEL default attribute count limit (128), if not user-specified. This is
# because we use separate attributes to store e.g. message history, available tools, etc.
# see: https://opentelemetry-python.readthedocs.io/en/latest/sdk/environment_variables.html#opentelemetry.sdk.environment_variables.OTEL_ATTRIBUTE_COUNT_LIMIT
if os.environ.get(OTEL_ATTRIBUTE_COUNT_LIMIT) is None:
    os.environ[OTEL_ATTRIBUTE_COUNT_LIMIT] = str(DEFAULT_OTEL_ATTRIBUTE_COUNT_LIMIT)


class AtlaInsights:
    """Atla insights."""

    def __init__(self) -> None:
        """Initialize Atla insights."""
        self._active_instrumentors: dict[str, Sequence[BaseInstrumentor]] = {}

        self.configured = False

        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[Tracer] = None

    def configure(
        self,
        token: Optional[str] = None,
        sampler: SamplerType = ALWAYS_ON,
        metadata: Optional[dict[str, str]] = None,
        additional_span_processors: Optional[Sequence[SpanProcessor]] = None,
        verbose: bool = True,
        debug: bool = False,
        environment: Optional[str] = None,
    ) -> None:
        """Configure Atla insights.

        The configure method authenticates to the Atla Insights platform, and sets up
        the relevant OpenTelemetry components.

        This method is intended to be called once at the start of the application, before
        any other Atla Insights functionality is called.

        If an existing tracer provider is already set, the Atla Insights platform will
        be added to the existing functionality attached to this tracer provider.
        Otherwise, a new tracer provider will be created and set as the global tracer
        provider.

        ```py
        import os
        from atla_insights import configure

        configure(token=os.environ["ATLA_INSIGHTS_TOKEN"])
        ```

        :param token (Optional[str]): The Atla Insights token associated with your
            organization. This can be found in the [Atla Insights platform](https://app.atla-ai.com).
        :param sampler (SamplerType): The OpenTelemetry sampler to use. This must
            be a `ParentBased`, `StaticSampler` or `_TailSampler` to ensure that the
            Atla Insights platform never receives partial traces. Defaults to a static
            sampler that samples all traces.
        :param metadata (Optional[dict[str, str]]): A dictionary of metadata to be added
            to the trace.
        :param additional_span_processors (Optional[Sequence[SpanProcessor]]): Additional
            span processors. Defaults to `None`.
        :param verbose (bool): Whether to print verbose output to console.
            Defaults to `True`.
        :param debug (bool): Whether to log debug outputs. Defaults to `False`.
        :param environment (Optional[str]): The environment to use ("dev" or "prod").
            If not provided, will use ATLA_INSIGHTS_ENVIRONMENT environment variable,
            or default to "prod".
        """
        if self.configured:
            logger.warning("Atla insights already configured, skipping configuration.")
            return

        # Either use provided token, or read from environment variable.
        token = token or os.environ["ATLA_INSIGHTS_TOKEN"]

        if metadata is not None:
            set_global_metadata(metadata)

        self.tracer_provider = self._setup_tracer_provider(
            token=token,
            sampler=sampler,
            additional_span_processors=additional_span_processors,
            verbose=verbose,
            debug=debug,
            environment=resolve_environment(environment),
        )
        self.tracer = self.get_tracer()

        self.configured = True
        logger.info("Atla insights configured correctly ✅")

    def _setup_tracer_provider(
        self,
        token: str,
        sampler: SamplerType,
        additional_span_processors: Optional[Sequence[SpanProcessor]],
        verbose: bool,
        debug: bool,
        environment: str,
    ) -> TracerProvider:
        """Setup the tracer provider.

        If a (non-proxy) tracer provider is already set, we return it. All Atla-specific
        telemetry will be added to the existing functionality attached to this tracer
        provider.

        If no tracer provider is set, we create a new one and set it as the global tracer
        provider.

        :param token (str): The Atla Insights token associated with your
            organization. This can be found in the [Atla Insights platform](https://app.atla-ai.com).
        :param sampler (SamplerType): The OpenTelemetry sampler to use. This must
            be a `ParentBased`, `StaticSampler` or `_TailSampler` to ensure that the
            Atla Insights platform never receives partial traces. Defaults to a static
            sampler that samples all traces.
        :param additional_span_processors (Optional[Sequence[SpanProcessor]]): Additional
            span processors. Defaults to `None`.
        :param verbose (bool): Whether to print verbose output to console.
            Defaults to `True`.
        :param debug (bool): Whether to log debug outputs. Defaults to `False`.
        :param environment (str): The environment to use ("dev" or "prod").

        :return (TracerProvider): The tracer provider.
        """
        if existing_tracer_provider := maybe_get_existing_tracer_provider():
            tracer_provider = existing_tracer_provider
        else:
            # If no existing tracer provider is found, we create a new one and set it as
            # the global tracer provider.
            tracer_provider = TracerProvider()
            set_tracer_provider(tracer_provider)

        atla_exporter = get_atla_span_exporter(token)

        if isinstance(sampler, _TailSampler):
            # If the sampler is a tail sampler, we add it as a span processor and have the
            # sampler control the atla & console exporters.
            sampler.add_exporter(atla_exporter)
            if verbose:
                sampler.add_exporter(ConsoleSpanExporter())

            tracer_provider.add_span_processor(sampler)
        else:
            tracer_provider.sampler = sampler

            tracer_provider.add_span_processor(SimpleSpanProcessor(atla_exporter))
            if verbose:
                console_span_exporter = ConsoleSpanExporter()
                tracer_provider.add_span_processor(
                    BatchSpanProcessor(console_span_exporter)
                )

        tracer_provider.add_span_processor(AtlaRootSpanProcessor(debug, environment))

        if additional_span_processors:
            for span_processor in additional_span_processors:
                tracer_provider.add_span_processor(span_processor)

        tracer_provider.id_generator = NoSeedIdGenerator()
        return tracer_provider

    def get_tracer(self) -> Tracer:
        """Get the current active tracer.

        :return (Tracer): The tracer.
        """
        if self.tracer_provider is None:
            raise ValueError("Atla Insights must be configured before instrumenting")
        return self.tracer_provider.get_tracer(OTEL_MODULE_NAME)

    def instrument_service(
        self, service: str, instrumentors: Sequence[BaseInstrumentor]
    ) -> ContextManager[None]:
        """Instrument a service (i.e. framework or LLM provider).

        This function creates a context manager that instruments a service, within its
        context. It also registers the relevant instrumentors for the service, so that
        they can be uninstrumented later.

        :param service (str): The service to instrument.
        :param instrumentors (Sequence[BaseInstrumentor]): The instrumentors to use.
        :return (ContextManager[None]): A context manager that instruments the provider.
        """
        # If the service is already registered as instrumented, first uninstrument it.
        if service in self._active_instrumentors:
            logger.warning(f"Attempting to instrument already instrumented {service}")
            self.uninstrument_service(service)

        # Call each instrumentor for the service.
        for instrumentor in instrumentors:
            instrumentor.instrument()

        # Register the instrumentors for the service.
        self._active_instrumentors[service] = instrumentors

        # Create a instrumentation context manager that uninstruments on context end.
        @contextmanager
        def instrumented_context():
            try:
                yield
            finally:
                self.uninstrument_service(service)

        return instrumented_context()

    def uninstrument_service(self, service: str) -> None:
        """Uninstrument a service (i.e. framework or LLM provider).

        This function will look up a given service in its internal registry of
        instrumented services, and (if found) uninstrument it & remove it from the
        registry.

        :param service (str): The service to uninstrument.
        """
        # If service is unregistered, we can't uninstrument it.
        if service not in self._active_instrumentors.keys():
            logger.warning(
                f"Attempting to uninstrument {service} which was not instrumented."
            )
            return

        # Uninstrument the service's instrumentors & remove its mention from the registry.
        instrumentors = self._active_instrumentors.pop(service)
        for instrumentor in instrumentors:
            instrumentor.uninstrument()


ATLA_INSTANCE = AtlaInsights()

configure = ATLA_INSTANCE.configure
