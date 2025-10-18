"""Unit tests for msgflux.telemetry.tracer module."""

import threading
from unittest.mock import MagicMock, Mock, patch

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import NoOpTracerProvider


class TestTracerManager:
    """Test suite for TracerManager class."""

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    def test_tracer_manager_initialization(self, mock_trace, mock_envs):
        """Test TracerManager initializes with correct defaults."""
        from msgflux.telemetry.tracer import TracerManager

        manager = TracerManager()
        assert manager._configured is False
        assert manager._tracer is None
        # RLock is a factory function, so we check the type name
        assert type(manager._lock).__name__ == "RLock"

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    def test_configure_tracer_with_noop_when_disabled(self, mock_trace, mock_envs):
        """Test that NoOp tracer is configured when telemetry is disabled."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_requires_trace = False
        mock_noop_provider = Mock(spec=NoOpTracerProvider)
        mock_trace.get_tracer.return_value = Mock()

        with patch(
            "msgflux.telemetry.tracer.NoOpTracerProvider",
            return_value=mock_noop_provider,
        ):
            manager = TracerManager()
            manager.configure_tracer()

            assert manager._configured is True
            mock_trace.set_tracer_provider.assert_called_once_with(mock_noop_provider)
            mock_trace.get_tracer.assert_called_once_with("msgflux.telemetry")

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    @patch("msgflux.telemetry.tracer.TracerProvider")
    @patch("msgflux.telemetry.tracer.Resource")
    @patch("msgflux.telemetry.tracer.OTLPSpanExporter")
    @patch("msgflux.telemetry.tracer.BatchSpanProcessor")
    def test_configure_tracer_with_otlp_exporter(
        self,
        mock_batch_processor,
        mock_otlp_exporter,
        mock_resource,
        mock_tracer_provider,
        mock_trace,
        mock_envs,
    ):
        """Test TracerManager configures OTLP exporter correctly."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_requires_trace = True
        mock_envs.telemetry_span_exporter_type = "otlp"
        mock_envs.telemetry_otlp_endpoint = "http://localhost:4318"
        mock_envs.telemetry_sampling_ratio = None

        mock_resource_instance = Mock()
        mock_resource.create.return_value = mock_resource_instance
        mock_provider_instance = Mock()
        mock_tracer_provider.return_value = mock_provider_instance
        mock_processor_instance = Mock()
        mock_batch_processor.return_value = mock_processor_instance

        manager = TracerManager()
        manager.configure_tracer()

        assert manager._configured is True
        mock_otlp_exporter.assert_called_once_with(
            endpoint="http://localhost:4318"
        )
        mock_provider_instance.add_span_processor.assert_called_once_with(
            mock_processor_instance
        )
        mock_trace.set_tracer_provider.assert_called_once_with(mock_provider_instance)

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    @patch("msgflux.telemetry.tracer.TracerProvider")
    @patch("msgflux.telemetry.tracer.Resource")
    @patch("msgflux.telemetry.tracer.ConsoleSpanExporter")
    @patch("msgflux.telemetry.tracer.BatchSpanProcessor")
    def test_configure_tracer_with_console_exporter(
        self,
        mock_batch_processor,
        mock_console_exporter,
        mock_resource,
        mock_tracer_provider,
        mock_trace,
        mock_envs,
    ):
        """Test TracerManager configures Console exporter correctly."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_requires_trace = True
        mock_envs.telemetry_span_exporter_type = "console"
        mock_envs.telemetry_sampling_ratio = None

        mock_resource_instance = Mock()
        mock_resource.create.return_value = mock_resource_instance
        mock_provider_instance = Mock()
        mock_tracer_provider.return_value = mock_provider_instance
        mock_processor_instance = Mock()
        mock_batch_processor.return_value = mock_processor_instance

        manager = TracerManager()
        manager.configure_tracer()

        assert manager._configured is True
        mock_console_exporter.assert_called_once()
        mock_provider_instance.add_span_processor.assert_called_once_with(
            mock_processor_instance
        )

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    def test_configure_tracer_with_unknown_exporter(self, mock_trace, mock_envs):
        """Test TracerManager falls back to NoOp for unknown exporter."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_requires_trace = True
        mock_envs.telemetry_span_exporter_type = "unknown"
        mock_noop_provider = Mock(spec=NoOpTracerProvider)

        with patch(
            "msgflux.telemetry.tracer.NoOpTracerProvider",
            return_value=mock_noop_provider,
        ):
            manager = TracerManager()
            manager.configure_tracer()

            assert manager._configured is True
            mock_trace.set_tracer_provider.assert_called_with(mock_noop_provider)

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    @patch("msgflux.telemetry.tracer.TracerProvider")
    @patch("msgflux.telemetry.tracer.Resource")
    @patch("msgflux.telemetry.tracer.ParentBased")
    @patch("msgflux.telemetry.tracer.TraceIdRatioBased")
    def test_build_sampler_with_valid_ratio(
        self,
        mock_ratio_based,
        mock_parent_based,
        mock_resource,
        mock_tracer_provider,
        mock_trace,
        mock_envs,
    ):
        """Test _build_sampler creates sampler with valid ratio."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_requires_trace = True
        mock_envs.telemetry_span_exporter_type = "console"
        mock_envs.telemetry_sampling_ratio = "0.5"

        mock_ratio_sampler = Mock()
        mock_ratio_based.return_value = mock_ratio_sampler
        mock_parent_sampler = Mock()
        mock_parent_based.return_value = mock_parent_sampler

        manager = TracerManager()
        sampler = manager._build_sampler()

        assert sampler == mock_parent_sampler
        mock_ratio_based.assert_called_once_with(0.5)
        mock_parent_based.assert_called_once_with(mock_ratio_sampler)

    @patch("msgflux.telemetry.tracer.envs")
    def test_build_sampler_with_invalid_ratio(self, mock_envs):
        """Test _build_sampler returns None for invalid ratio."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_sampling_ratio = "invalid"

        manager = TracerManager()
        sampler = manager._build_sampler()

        assert sampler is None

    @patch("msgflux.telemetry.tracer.envs")
    def test_build_sampler_with_no_ratio(self, mock_envs):
        """Test _build_sampler returns None when no ratio is set."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_sampling_ratio = None

        manager = TracerManager()
        sampler = manager._build_sampler()

        assert sampler is None

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    def test_configure_tracer_is_idempotent(self, mock_trace, mock_envs):
        """Test that configure_tracer can be called multiple times safely."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_requires_trace = False
        mock_noop_provider = Mock(spec=NoOpTracerProvider)

        with patch(
            "msgflux.telemetry.tracer.NoOpTracerProvider",
            return_value=mock_noop_provider,
        ):
            manager = TracerManager()
            manager.configure_tracer()
            manager.configure_tracer()
            manager.configure_tracer()

            # Should only set tracer provider once
            assert mock_trace.set_tracer_provider.call_count == 1

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    def test_get_tracer_auto_configures(self, mock_trace, mock_envs):
        """Test that get_tracer auto-configures if not configured."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_requires_trace = False
        mock_tracer = Mock()
        mock_trace.get_tracer.return_value = mock_tracer
        mock_noop_provider = Mock(spec=NoOpTracerProvider)

        with patch(
            "msgflux.telemetry.tracer.NoOpTracerProvider",
            return_value=mock_noop_provider,
        ):
            manager = TracerManager()
            tracer = manager.get_tracer()

            assert manager._configured is True
            assert tracer == mock_tracer

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    def test_get_tracer_thread_safety(self, mock_trace, mock_envs):
        """Test that get_tracer is thread-safe."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_requires_trace = False
        mock_tracer = Mock()
        mock_trace.get_tracer.return_value = mock_tracer
        mock_noop_provider = Mock(spec=NoOpTracerProvider)

        with patch(
            "msgflux.telemetry.tracer.NoOpTracerProvider",
            return_value=mock_noop_provider,
        ):
            manager = TracerManager()
            results = []

            def get_tracer_thread():
                results.append(manager.get_tracer())

            threads = [threading.Thread(target=get_tracer_thread) for _ in range(10)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            # All threads should get the same tracer
            assert all(tracer == mock_tracer for tracer in results)
            # Configuration should only happen once
            assert mock_trace.set_tracer_provider.call_count == 1

    @patch("msgflux.telemetry.tracer.tracer_manager")
    def test_get_tracer_convenience_function(self, mock_manager):
        """Test get_tracer convenience function."""
        from msgflux.telemetry.tracer import get_tracer

        mock_tracer = Mock()
        mock_manager.get_tracer.return_value = mock_tracer

        tracer = get_tracer()

        assert tracer == mock_tracer
        mock_manager.get_tracer.assert_called_once()

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    @patch("msgflux.telemetry.tracer.TracerProvider")
    @patch("msgflux.telemetry.tracer.Resource")
    @patch("msgflux.telemetry.tracer.ConsoleSpanExporter")
    @patch("msgflux.telemetry.tracer.BatchSpanProcessor")
    @patch("msgflux.telemetry.tracer.ParentBased")
    @patch("msgflux.telemetry.tracer.TraceIdRatioBased")
    def test_configure_tracer_with_sampler(
        self,
        mock_ratio_based,
        mock_parent_based,
        mock_batch_processor,
        mock_console_exporter,
        mock_resource,
        mock_tracer_provider,
        mock_trace,
        mock_envs,
    ):
        """Test TracerProvider is configured with sampler when ratio is set."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_requires_trace = True
        mock_envs.telemetry_span_exporter_type = "console"
        mock_envs.telemetry_sampling_ratio = "0.3"

        mock_ratio_sampler = Mock()
        mock_ratio_based.return_value = mock_ratio_sampler
        mock_parent_sampler = Mock()
        mock_parent_based.return_value = mock_parent_sampler
        mock_resource_instance = Mock()
        mock_resource.create.return_value = mock_resource_instance

        manager = TracerManager()
        manager.configure_tracer()

        # Verify TracerProvider was called with sampler
        mock_tracer_provider.assert_called_once_with(
            resource=mock_resource_instance, sampler=mock_parent_sampler
        )

    @patch("msgflux.telemetry.tracer.envs")
    @patch("msgflux.telemetry.tracer.trace")
    @patch("msgflux.telemetry.tracer.SERVICE_NAME", "test_service")
    @patch("msgflux.telemetry.tracer.Resource")
    def test_resource_creation_with_service_name(
        self, mock_resource, mock_trace, mock_envs
    ):
        """Test that Resource is created with correct service name."""
        from msgflux.telemetry.tracer import TracerManager

        mock_envs.telemetry_requires_trace = True
        mock_envs.telemetry_span_exporter_type = "console"
        mock_envs.telemetry_sampling_ratio = None

        with patch("msgflux.telemetry.tracer.TracerProvider"):
            with patch("msgflux.telemetry.tracer.ConsoleSpanExporter"):
                with patch("msgflux.telemetry.tracer.BatchSpanProcessor"):
                    manager = TracerManager()
                    manager.configure_tracer()

                    # Verify Resource.create was called with SERVICE_NAME
                    mock_resource.create.assert_called_once()
                    call_args = mock_resource.create.call_args
                    assert "test_service" in str(call_args)
