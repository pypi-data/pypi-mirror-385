"""Unit tests for msgflux.telemetry.span module."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import msgspec
import pytest
from opentelemetry.trace import SpanKind, StatusCode


class TestSpans:
    """Test suite for Spans class."""

    @patch("msgflux.telemetry.span.get_tracer")
    def test_spans_initialization(self, mock_get_tracer):
        """Test Spans class initializes with tracer."""
        from msgflux.telemetry.span import Spans

        mock_tracer = Mock()
        mock_get_tracer.return_value = mock_tracer

        spans = Spans()

        assert spans.tracer == mock_tracer
        mock_get_tracer.assert_called_once()

    @patch("msgflux.telemetry.span.get_tracer")
    def test_span_context(self, mock_get_tracer):
        """Test span_context creates and manages a span."""
        from msgflux.telemetry.span import Spans

        mock_tracer = Mock()
        mock_span = Mock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
            return_value=mock_span
        )
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
            return_value=False
        )

        spans = Spans()
        attributes = {"key1": "value1", "key2": "value2"}

        with spans.span_context("test_span", attributes=attributes) as span:
            assert span == mock_span

        mock_tracer.start_as_current_span.assert_called_once_with(
            "test_span", kind=SpanKind.INTERNAL
        )
        assert mock_span.set_attribute.call_count == 2
        mock_span.set_attribute.assert_any_call("key1", "value1")
        mock_span.set_attribute.assert_any_call("key2", "value2")

    @patch("msgflux.telemetry.span.get_tracer")
    def test_span_context_without_attributes(self, mock_get_tracer):
        """Test span_context works without attributes."""
        from msgflux.telemetry.span import Spans

        mock_tracer = Mock()
        mock_span = Mock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
            return_value=mock_span
        )
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
            return_value=False
        )

        spans = Spans()

        with spans.span_context("test_span") as span:
            assert span == mock_span

        mock_span.set_attribute.assert_not_called()

    @patch("msgflux.telemetry.span.get_tracer")
    @patch("msgflux.telemetry.span.msgflux_version", "1.0.0")
    @patch("msgflux.telemetry.span.envs")
    def test_init_flow(self, mock_envs, mock_get_tracer):
        """Test init_flow context manager."""
        from msgflux.telemetry.span import Spans

        mock_envs.telemetry_capture_platform = False
        mock_tracer = Mock()
        mock_span = Mock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
            return_value=mock_span
        )
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
            return_value=False
        )

        spans = Spans()
        message = {"metadata": {"user": "test"}}

        with spans.init_flow("test_workflow", message=message) as span:
            assert span == mock_span

        # Check that version and workflow name are set
        set_attr_calls = [call[0] for call in mock_span.set_attribute.call_args_list]
        assert ("msgflux.version", "1.0.0") in set_attr_calls
        assert ("msgflux.workflow.name", "test_workflow") in set_attr_calls
        assert ("msgflux.metadata", {"user": "test"}) in set_attr_calls

    @patch("msgflux.telemetry.span.get_tracer")
    @patch("msgflux.telemetry.span.msgflux_version", "1.0.0")
    @patch("msgflux.telemetry.span.envs")
    @patch("msgflux.telemetry.span.platform")
    @patch("msgflux.telemetry.span.os")
    def test_init_flow_with_platform_capture(
        self, mock_os, mock_platform, mock_envs, mock_get_tracer
    ):
        """Test init_flow captures platform info when enabled."""
        from msgflux.telemetry.span import Spans

        mock_envs.telemetry_capture_platform = True
        mock_platform.platform.return_value = "Linux-5.10.0"
        mock_platform.version.return_value = "5.10.0"
        mock_platform.python_version.return_value = "3.10.0"
        mock_os.cpu_count.return_value = 8

        mock_tracer = Mock()
        mock_span = Mock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
            return_value=mock_span
        )
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
            return_value=False
        )

        spans = Spans()

        with spans.init_flow("test_workflow") as span:
            assert span == mock_span

        set_attr_calls = [call[0] for call in mock_span.set_attribute.call_args_list]
        assert ("platform", "Linux-5.10.0") in set_attr_calls
        assert ("platform.version", "5.10.0") in set_attr_calls
        assert ("platform.python.version", "3.10.0") in set_attr_calls
        assert ("platform.num_cpus", 8) in set_attr_calls

    @patch("msgflux.telemetry.span.get_tracer")
    def test_init_module(self, mock_get_tracer):
        """Test init_module context manager."""
        from msgflux.telemetry.span import Spans

        mock_tracer = Mock()
        mock_span = Mock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
            return_value=mock_span
        )
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
            return_value=False
        )

        spans = Spans()

        with spans.init_module("test_module") as span:
            assert span == mock_span

        mock_span.set_attribute.assert_called_once_with(
            "msgflux.nn.module.name", "test_module"
        )

    @patch("msgflux.telemetry.span.get_tracer")
    def test_tool_usage(self, mock_get_tracer):
        """Test tool_usage context manager."""
        from msgflux.telemetry.span import Spans

        mock_tracer = Mock()
        mock_span = Mock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
            return_value=mock_span
        )
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
            return_value=False
        )

        spans = Spans()
        tool_callings = [
            ("id1", "tool1", {"param": "value1"}),
            ("id2", "tool2", {"param": "value2"}),
        ]

        with spans.tool_usage(tool_callings) as span:
            assert span == mock_span

        # Verify the encoded calls structure
        call_args = mock_span.set_attribute.call_args[0]
        assert call_args[0] == "msgflux.nn.tool.callings"
        # The second argument should be the encoded JSON
        encoded_calls = call_args[1]
        decoded = msgspec.json.decode(encoded_calls)
        assert len(decoded) == 2
        assert decoded[0]["id"] == "id1"
        assert decoded[0]["name"] == "tool1"
        assert decoded[1]["id"] == "id2"

    @pytest.mark.asyncio
    @patch("msgflux.telemetry.span.get_tracer")
    async def test_aspan_context(self, mock_get_tracer):
        """Test async span_context creates and manages a span."""
        from msgflux.telemetry.span import Spans

        mock_tracer = Mock()
        mock_span = Mock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
            return_value=mock_span
        )
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
            return_value=False
        )

        spans = Spans()
        attributes = {"key1": "value1"}

        async with spans.aspan_context("async_test_span", attributes=attributes) as span:
            assert span == mock_span

        mock_span.set_attribute.assert_called_once_with("key1", "value1")

    @pytest.mark.asyncio
    @patch("msgflux.telemetry.span.get_tracer")
    @patch("msgflux.telemetry.span.msgflux_version", "1.0.0")
    @patch("msgflux.telemetry.span.envs")
    async def test_ainit_flow(self, mock_envs, mock_get_tracer):
        """Test async init_flow context manager."""
        from msgflux.telemetry.span import Spans

        mock_envs.telemetry_capture_platform = False
        mock_tracer = Mock()
        mock_span = Mock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
            return_value=mock_span
        )
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
            return_value=False
        )

        spans = Spans()

        async with spans.ainit_flow("async_workflow") as span:
            assert span == mock_span

        set_attr_calls = [call[0] for call in mock_span.set_attribute.call_args_list]
        assert ("msgflux.workflow.name", "async_workflow") in set_attr_calls

    @pytest.mark.asyncio
    @patch("msgflux.telemetry.span.get_tracer")
    async def test_ainit_module(self, mock_get_tracer):
        """Test async init_module context manager."""
        from msgflux.telemetry.span import Spans

        mock_tracer = Mock()
        mock_span = Mock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
            return_value=mock_span
        )
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
            return_value=False
        )

        spans = Spans()

        async with spans.ainit_module("async_module") as span:
            assert span == mock_span

        mock_span.set_attribute.assert_called_once_with(
            "msgflux.nn.module.name", "async_module"
        )

    @pytest.mark.asyncio
    @patch("msgflux.telemetry.span.get_tracer")
    async def test_atool_usage(self, mock_get_tracer):
        """Test async tool_usage context manager."""
        from msgflux.telemetry.span import Spans

        mock_tracer = Mock()
        mock_span = Mock()
        mock_get_tracer.return_value = mock_tracer
        mock_tracer.start_as_current_span.return_value.__enter__ = Mock(
            return_value=mock_span
        )
        mock_tracer.start_as_current_span.return_value.__exit__ = Mock(
            return_value=False
        )

        spans = Spans()
        tool_callings = [("id1", "async_tool", {"param": "value"})]

        async with spans.atool_usage(tool_callings) as span:
            assert span == mock_span

        call_args = mock_span.set_attribute.call_args[0]
        assert call_args[0] == "msgflux.nn.tool.callings"


class TestInstrumentDecorator:
    """Test suite for instrument decorator."""

    @patch("msgflux.telemetry.span.envs")
    @patch("msgflux.telemetry.span.spans")
    def test_instrument_sync_function(self, mock_spans, mock_envs):
        """Test instrument decorator on synchronous function."""
        from msgflux.telemetry.span import instrument

        mock_envs.telemetry_requires_trace = True
        mock_span = Mock()
        mock_spans.span_context.return_value.__enter__ = Mock(return_value=mock_span)
        mock_spans.span_context.return_value.__exit__ = Mock(return_value=False)

        @instrument(name="test_function", attributes={"key": "value"})
        def test_func(x):
            return x * 2

        result = test_func(5)

        assert result == 10
        mock_spans.span_context.assert_called_once_with(
            "test_function", attributes={"key": "value"}
        )

    @patch("msgflux.telemetry.span.envs")
    @patch("msgflux.telemetry.span.spans")
    def test_instrument_sync_function_uses_func_name(self, mock_spans, mock_envs):
        """Test instrument uses function name when name not provided."""
        from msgflux.telemetry.span import instrument

        mock_envs.telemetry_requires_trace = True
        mock_span = Mock()
        mock_spans.span_context.return_value.__enter__ = Mock(return_value=mock_span)
        mock_spans.span_context.return_value.__exit__ = Mock(return_value=False)

        @instrument()
        def my_function():
            return "result"

        result = my_function()

        assert result == "result"
        mock_spans.span_context.assert_called_once_with(
            "my_function", attributes=None
        )

    @patch("msgflux.telemetry.span.envs")
    def test_instrument_sync_zero_overhead_when_disabled(self, mock_envs):
        """Test instrument has zero overhead when telemetry is disabled."""
        from msgflux.telemetry.span import instrument

        mock_envs.telemetry_requires_trace = False

        @instrument(name="test_function")
        def test_func(x):
            return x * 3

        result = test_func(4)

        assert result == 12
        # No span operations should occur

    @patch("msgflux.telemetry.span.envs")
    @patch("msgflux.telemetry.span.spans")
    def test_instrument_sync_function_exception(self, mock_spans, mock_envs):
        """Test instrument records exceptions in sync functions."""
        from msgflux.telemetry.span import instrument

        mock_envs.telemetry_requires_trace = True
        mock_span = Mock()
        mock_spans.span_context.return_value.__enter__ = Mock(return_value=mock_span)
        mock_spans.span_context.return_value.__exit__ = Mock(return_value=False)

        @instrument()
        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_func()

        mock_span.record_exception.assert_called_once()
        mock_span.set_status.assert_called_once()
        # Verify status code is ERROR
        status_call = mock_span.set_status.call_args[0][0]
        assert status_call.status_code == StatusCode.ERROR

    @pytest.mark.asyncio
    @patch("msgflux.telemetry.span.envs")
    @patch("msgflux.telemetry.span.spans")
    async def test_instrument_async_function(self, mock_spans, mock_envs):
        """Test instrument decorator on async function."""
        from msgflux.telemetry.span import instrument

        mock_envs.telemetry_requires_trace = True
        mock_span = Mock()
        mock_spans.span_context.return_value.__enter__ = Mock(return_value=mock_span)
        mock_spans.span_context.return_value.__exit__ = Mock(return_value=False)

        @instrument(name="async_test")
        async def async_func(x):
            return x * 2

        result = await async_func(5)

        assert result == 10
        mock_spans.span_context.assert_called_once_with(
            "async_test", attributes=None
        )

    @pytest.mark.asyncio
    @patch("msgflux.telemetry.span.envs")
    async def test_instrument_async_zero_overhead_when_disabled(self, mock_envs):
        """Test instrument has zero overhead for async when disabled."""
        from msgflux.telemetry.span import instrument

        mock_envs.telemetry_requires_trace = False

        @instrument()
        async def async_func(x):
            return x * 3

        result = await async_func(4)

        assert result == 12

    @pytest.mark.asyncio
    @patch("msgflux.telemetry.span.envs")
    @patch("msgflux.telemetry.span.spans")
    async def test_instrument_async_function_exception(self, mock_spans, mock_envs):
        """Test instrument records exceptions in async functions."""
        from msgflux.telemetry.span import instrument

        mock_envs.telemetry_requires_trace = True
        mock_span = Mock()
        mock_spans.span_context.return_value.__enter__ = Mock(return_value=mock_span)
        mock_spans.span_context.return_value.__exit__ = Mock(return_value=False)

        @instrument()
        async def async_failing_func():
            raise RuntimeError("Async error")

        with pytest.raises(RuntimeError, match="Async error"):
            await async_failing_func()

        mock_span.record_exception.assert_called_once()
        mock_span.set_status.assert_called_once()


class TestInstrumentToolLibraryCall:
    """Test suite for instrument_tool_library_call decorator."""

    @patch("msgflux.telemetry.span.envs")
    def test_instrument_tool_library_call_disabled(self, mock_envs):
        """Test decorator has zero overhead when telemetry disabled."""
        from msgflux.telemetry.span import instrument_tool_library_call

        mock_envs.telemetry_requires_trace = False

        def forward(self, tool_callings, model_state, vars):
            return "result"

        decorated = instrument_tool_library_call(forward)

        class MockSelf:
            pass

        result = decorated(MockSelf(), [], None, None)
        assert result == "result"

    @patch("msgflux.telemetry.span.envs")
    def test_instrument_tool_library_call_with_telemetry(self, mock_envs):
        """Test decorator instruments tool library calls."""
        from msgflux.telemetry.span import instrument_tool_library_call

        mock_envs.telemetry_requires_trace = True
        mock_envs.telemetry_capture_tool_call_responses = True

        mock_span = Mock()
        mock_spans = Mock()
        mock_spans.tool_usage.return_value.__enter__ = Mock(return_value=mock_span)
        mock_spans.tool_usage.return_value.__exit__ = Mock(return_value=False)

        def forward(self, tool_callings, model_state, vars):
            mock_result = Mock()
            mock_result.to_json.return_value = '{"result": "success"}'
            return mock_result

        decorated = instrument_tool_library_call(forward)

        class MockSelf:
            _spans = mock_spans

        tool_callings = [("id1", "tool1", {})]
        result = decorated(MockSelf(), tool_callings, None, {})

        mock_spans.tool_usage.assert_called_once_with(tool_callings)
        mock_span.set_attribute.assert_called_once_with(
            "msgflux.nn.tool.responses", '{"result": "success"}'
        )


class TestAinstrumentToolLibraryCall:
    """Test suite for ainstrument_tool_library_call decorator."""

    @pytest.mark.asyncio
    @patch("msgflux.telemetry.span.envs")
    async def test_ainstrument_tool_library_call_disabled(self, mock_envs):
        """Test async decorator has zero overhead when disabled."""
        from msgflux.telemetry.span import ainstrument_tool_library_call

        mock_envs.telemetry_requires_trace = False

        async def aforward(self, tool_callings, model_state, vars):
            return "async_result"

        decorated = ainstrument_tool_library_call(aforward)

        class MockSelf:
            pass

        result = await decorated(MockSelf(), [], None, None)
        assert result == "async_result"

    @pytest.mark.asyncio
    @patch("msgflux.telemetry.span.envs")
    async def test_ainstrument_tool_library_call_with_telemetry(self, mock_envs):
        """Test async decorator instruments tool library calls."""
        from msgflux.telemetry.span import ainstrument_tool_library_call

        mock_envs.telemetry_requires_trace = True
        mock_envs.telemetry_capture_tool_call_responses = True

        mock_span = Mock()
        mock_spans = Mock()
        mock_spans.atool_usage.return_value.__aenter__ = AsyncMock(
            return_value=mock_span
        )
        mock_spans.atool_usage.return_value.__aexit__ = AsyncMock(return_value=False)

        async def aforward(self, tool_callings, model_state, vars):
            mock_result = Mock()
            mock_result.to_json.return_value = '{"result": "async_success"}'
            return mock_result

        decorated = ainstrument_tool_library_call(aforward)

        class MockSelf:
            _spans = mock_spans

        tool_callings = [("id1", "async_tool", {})]
        result = await decorated(MockSelf(), tool_callings, None, {})

        mock_spans.atool_usage.assert_called_once_with(tool_callings)
        mock_span.set_attribute.assert_called_once_with(
            "msgflux.nn.tool.responses", '{"result": "async_success"}'
        )


class TestInstrumentAgentPrepareModelExecution:
    """Test suite for instrument_agent_prepare_model_execution decorator."""

    @patch("msgflux.telemetry.span.envs")
    def test_decorator_disabled(self, mock_envs):
        """Test decorator has zero overhead when disabled."""
        from msgflux.telemetry.span import instrument_agent_prepare_model_execution

        mock_envs.telemetry_requires_trace = False

        def prepare_execution(self):
            return {"messages": [], "tool_schemas": []}

        decorated = instrument_agent_prepare_model_execution(prepare_execution)

        class MockSelf:
            pass

        result = decorated(MockSelf())
        assert result == {"messages": [], "tool_schemas": []}

    @patch("msgflux.telemetry.span.envs")
    def test_decorator_with_telemetry(self, mock_envs):
        """Test decorator instruments agent preparation."""
        from msgflux.telemetry.span import instrument_agent_prepare_model_execution

        mock_envs.telemetry_requires_trace = True
        mock_envs.telemetry_capture_agent_prepare_model_execution = True

        mock_span = Mock()
        mock_spans = Mock()
        mock_spans.span_context.return_value.__enter__ = Mock(return_value=mock_span)
        mock_spans.span_context.return_value.__exit__ = Mock(return_value=False)

        def prepare_execution(self):
            return {
                "messages": [{"role": "user", "content": "test"}],
                "tool_schemas": [{"name": "tool1"}],
                "system_prompt": "You are a helpful assistant",
            }

        decorated = instrument_agent_prepare_model_execution(prepare_execution)

        class MockSelf:
            _spans = mock_spans

        result = decorated(MockSelf())

        mock_spans.span_context.assert_called_once()
        # Verify span attributes were set
        assert mock_span.set_attribute.call_count == 3

    @patch("msgflux.telemetry.span.envs")
    def test_decorator_with_none_system_prompt(self, mock_envs):
        """Test decorator handles None system_prompt."""
        from msgflux.telemetry.span import instrument_agent_prepare_model_execution

        mock_envs.telemetry_requires_trace = True
        mock_envs.telemetry_capture_agent_prepare_model_execution = True

        mock_span = Mock()
        mock_spans = Mock()
        mock_spans.span_context.return_value.__enter__ = Mock(return_value=mock_span)
        mock_spans.span_context.return_value.__exit__ = Mock(return_value=False)

        def prepare_execution(self):
            return {
                "messages": [],
                "tool_schemas": [],
                "system_prompt": None,
            }

        decorated = instrument_agent_prepare_model_execution(prepare_execution)

        class MockSelf:
            _spans = mock_spans

        result = decorated(MockSelf())

        # Verify empty string was used for None system_prompt
        set_attr_calls = [call[0] for call in mock_span.set_attribute.call_args_list]
        system_prompt_calls = [
            call for call in set_attr_calls if "system_prompt" in call[0]
        ]
        assert len(system_prompt_calls) == 1
        assert system_prompt_calls[0][1] == ""
