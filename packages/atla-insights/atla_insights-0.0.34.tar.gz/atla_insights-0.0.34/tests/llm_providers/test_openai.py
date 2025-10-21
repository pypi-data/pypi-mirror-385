"""Test the OpenAI instrumentation."""

import pytest
from openai import AsyncAzureOpenAI, AsyncOpenAI, AzureOpenAI, OpenAI

from tests._otel import BaseLocalOtel


class TestOpenAIInstrumentation(BaseLocalOtel):
    """Test the OpenAI instrumentation."""

    def test_basic(self, mock_openai_client: OpenAI) -> None:
        """Test that the OpenAI instrumentation is traced."""
        from atla_insights import instrument_openai

        with instrument_openai():
            mock_openai_client.chat.completions.create(
                model="some-model",
                messages=[{"role": "user", "content": "hello world"}],
            )

        spans = self.get_finished_spans()

        assert len(spans) == 1
        [span] = spans

        assert span.attributes is not None
        assert span.attributes.get("llm.input_messages.0.message.role") == "user"
        assert (
            span.attributes.get("llm.input_messages.0.message.content") == "hello world"
        )
        assert span.attributes.get("llm.output_messages.0.message.role") == "assistant"
        assert (
            span.attributes.get("llm.output_messages.0.message.content") == "hello world"
        )

    @pytest.mark.asyncio
    async def test_async(self, mock_async_openai_client: AsyncOpenAI) -> None:
        """Test that the OpenAI instrumentation is traced."""
        from atla_insights import instrument_openai

        with instrument_openai():
            await mock_async_openai_client.chat.completions.create(
                model="some-model",
                messages=[{"role": "user", "content": "hello world"}],
            )

        spans = self.get_finished_spans()

        assert len(spans) == 1
        [span] = spans

        assert span.attributes is not None
        assert span.attributes.get("llm.input_messages.0.message.role") == "user"
        assert (
            span.attributes.get("llm.input_messages.0.message.content") == "hello world"
        )
        assert span.attributes.get("llm.output_messages.0.message.role") == "assistant"
        assert (
            span.attributes.get("llm.output_messages.0.message.content") == "hello world"
        )

    def test_nested_instrumentation(self, mock_openai_client: OpenAI) -> None:
        """Test that the OpenAI instrumentation is traced."""
        from atla_insights import instrument, instrument_openai

        @instrument("root_span")
        def test_function():
            with instrument_openai():
                mock_openai_client.chat.completions.create(
                    model="some-model",
                    messages=[{"role": "user", "content": "hello world"}],
                )

            return "test result"

        test_function()

        spans = self.get_finished_spans()

        assert len(spans) == 2
        root_span, generation_span = spans

        assert root_span.name == "root_span"
        assert root_span.attributes is not None

        assert generation_span.attributes is not None
        assert (
            generation_span.attributes.get("llm.input_messages.0.message.role") == "user"
        )
        assert (
            generation_span.attributes.get("llm.input_messages.0.message.content")
            == "hello world"
        )
        assert (
            generation_span.attributes.get("llm.output_messages.0.message.role")
            == "assistant"
        )
        assert (
            generation_span.attributes.get("llm.output_messages.0.message.content")
            == "hello world"
        )

    def test_nested_instrumentation_marked(self, mock_openai_client: OpenAI) -> None:
        """Test that the OpenAI instrumentation is traced."""
        from atla_insights import instrument, instrument_openai, mark_success
        from atla_insights.constants import SUCCESS_MARK

        @instrument("root_span")
        def test_function():
            with instrument_openai():
                mock_openai_client.chat.completions.create(
                    model="some-model",
                    messages=[{"role": "user", "content": "hello world"}],
                )

            mark_success()

            return "test result"

        test_function()

        spans = self.get_finished_spans()

        assert len(spans) == 2
        root_span, _ = spans

        assert root_span.attributes is not None
        assert root_span.attributes.get(SUCCESS_MARK) == 1

    def test_failing_instrumentation(self, mock_failing_openai_client: OpenAI) -> None:
        """Test that the OpenAI instrumentation is traced."""
        from atla_insights import instrument_openai
        from atla_insights.constants import SUCCESS_MARK

        with instrument_openai():
            mock_failing_openai_client.chat.completions.create(
                model="some-model",
                messages=[{"role": "user", "content": "hello world"}],
            )

        spans = self.get_finished_spans()

        assert len(spans) == 1
        [span] = spans

        assert span.attributes is not None

        assert span.attributes.get("llm.input_messages.0.message.role") == "user"
        assert (
            span.attributes.get("llm.input_messages.0.message.content") == "hello world"
        )
        assert span.attributes.get("llm.output_messages.0.message.role") is None
        assert span.attributes.get("llm.output_messages.0.message.content") is None

        assert span.attributes.get("response_data") is None

        assert span.attributes.get(SUCCESS_MARK) == -1

    def test_failing_instrumentation_marked(
        self, mock_failing_openai_client: OpenAI
    ) -> None:
        """Test that the OpenAI instrumentation is traced."""
        from atla_insights import instrument, instrument_openai, mark_success
        from atla_insights.constants import SUCCESS_MARK

        @instrument("root_span")
        def test_function():
            with instrument_openai():
                mock_failing_openai_client.chat.completions.create(
                    model="some-model",
                    messages=[{"role": "user", "content": "hello world"}],
                )

            mark_success()

            return "test result"

        test_function()

        spans = self.get_finished_spans()

        assert len(spans) == 2
        root_span, _ = spans

        assert root_span.attributes is not None
        assert root_span.attributes.get(SUCCESS_MARK) == 1

    def test_responses_api(self, mock_openai_client: OpenAI) -> None:
        """Test responses API."""
        from atla_insights import instrument_openai

        with instrument_openai():
            mock_openai_client.responses.create(
                model="some-model",
                input="hello world",
            )

        spans = self.get_finished_spans()

        assert len(spans) == 1
        [span] = spans

        assert span.attributes is not None
        assert span.attributes.get("llm.input_messages.1.message.role") == "user"
        assert (
            span.attributes.get("llm.input_messages.1.message.content") == "hello world"
        )
        assert span.attributes.get("llm.output_messages.0.message.role") == "assistant"
        assert (
            span.attributes.get(
                "llm.output_messages.0.message.contents.0.message_content.type"
            )
            == "text"
        )
        assert (
            span.attributes.get(
                "llm.output_messages.0.message.contents.0.message_content.text"
            )
            == "hello world"
        )

    def test_azure_openai(self, mock_azure_openai_client: AzureOpenAI) -> None:
        """Test responses API."""
        from atla_insights import instrument_openai

        with instrument_openai():
            mock_azure_openai_client.chat.completions.create(
                model="some-model",
                messages=[{"role": "user", "content": "hello world"}],
            )

        spans = self.get_finished_spans()

        assert len(spans) == 1
        [span] = spans

        assert span.attributes is not None
        assert span.attributes.get("llm.input_messages.0.message.role") == "user"
        assert (
            span.attributes.get("llm.input_messages.0.message.content") == "hello world"
        )
        assert span.attributes.get("llm.output_messages.0.message.role") == "assistant"
        assert (
            span.attributes.get("llm.output_messages.0.message.content") == "hello world"
        )

    @pytest.mark.asyncio
    async def test_async_azure_openai(
        self, mock_async_azure_openai_client: AsyncAzureOpenAI
    ) -> None:
        """Test responses API."""
        from atla_insights import instrument_openai

        with instrument_openai():
            await mock_async_azure_openai_client.chat.completions.create(
                model="some-model",
                messages=[{"role": "user", "content": "hello world"}],
            )

        spans = self.get_finished_spans()

        assert len(spans) == 1
        [span] = spans

        assert span.attributes is not None
        assert span.attributes.get("llm.input_messages.0.message.role") == "user"
        assert (
            span.attributes.get("llm.input_messages.0.message.content") == "hello world"
        )
        assert span.attributes.get("llm.output_messages.0.message.role") == "assistant"
        assert (
            span.attributes.get("llm.output_messages.0.message.content") == "hello world"
        )

    def test_streaming(self, mock_openai_stream_client: OpenAI) -> None:
        """Test streaming with OpenAI."""
        from atla_insights import instrument_openai

        with instrument_openai():
            for _ in mock_openai_stream_client.chat.completions.create(
                model="some-model",
                messages=[{"role": "user", "content": "hello world"}],
                stream=True,
            ):
                pass

        spans = self.get_finished_spans()

        assert len(spans) == 1
        [span] = spans

        assert span.attributes is not None
        assert span.attributes.get("llm.input_messages.0.message.role") == "user"
        assert (
            span.attributes.get("llm.input_messages.0.message.content") == "hello world"
        )

    @pytest.mark.asyncio
    async def test_async_streaming(
        self, mock_async_openai_stream_client: AsyncOpenAI
    ) -> None:
        """Test async streaming with OpenAI."""
        from atla_insights import instrument_openai

        with instrument_openai():
            async for _ in await mock_async_openai_stream_client.chat.completions.create(
                model="some-model",
                messages=[{"role": "user", "content": "hello world"}],
                stream=True,
            ):
                pass

        spans = self.get_finished_spans()

        assert len(spans) == 1
        [span] = spans

        assert span.attributes is not None
        assert span.attributes.get("llm.input_messages.0.message.role") == "user"
        assert (
            span.attributes.get("llm.input_messages.0.message.content") == "hello world"
        )

    def test_responses_streaming(self, mock_openai_stream_client: OpenAI) -> None:
        """Test streaming with Responses API."""
        from atla_insights import instrument_openai

        with instrument_openai():
            for _ in mock_openai_stream_client.responses.create(
                model="some-model",
                input="hello world",
                stream=True,
            ):
                pass

        spans = self.get_finished_spans()

        assert len(spans) == 1
        [span] = spans

        assert span.attributes is not None
        assert span.attributes.get("llm.input_messages.1.message.role") == "user"
        assert (
            span.attributes.get("llm.input_messages.1.message.content") == "hello world"
        )

    @pytest.mark.asyncio
    async def test_async_responses_streaming(
        self, mock_async_openai_stream_client: AsyncOpenAI
    ) -> None:
        """Test async streaming with Responses API."""
        from atla_insights import instrument_openai

        with instrument_openai():
            async for _ in await mock_async_openai_stream_client.responses.create(
                model="some-model",
                input="hello world",
                stream=True,
            ):
                pass

        spans = self.get_finished_spans()

        assert len(spans) == 1
        [span] = spans

        assert span.attributes is not None
        assert span.attributes.get("llm.input_messages.1.message.role") == "user"
        assert (
            span.attributes.get("llm.input_messages.1.message.content") == "hello world"
        )

    def test_context_manager(self, mock_openai_client: OpenAI) -> None:
        """Test that instrumentation only applies within context."""
        from atla_insights import instrument_openai

        with instrument_openai():
            mock_openai_client.chat.completions.create(
                model="some-model",
                messages=[{"role": "user", "content": "hello world"}],
            )

        # This call should not be instrumented (outside context)
        mock_openai_client.chat.completions.create(
            model="some-model",
            messages=[{"role": "user", "content": "hello again"}],
        )

        spans = self.get_finished_spans()
        assert len(spans) == 1
