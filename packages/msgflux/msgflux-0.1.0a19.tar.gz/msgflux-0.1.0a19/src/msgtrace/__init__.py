"""msgtrace - Trace visualization and observability for msgflux.

A lightweight, self-hosted observability platform for msgflux AI systems.
Captures, stores, and visualizes OpenTelemetry traces from msgflux workflows.
"""

__version__ = "0.1.0"

from msgtrace.core.client import start_observer
from msgtrace.core.config import MsgTraceConfig

__all__ = [
    "start_observer",
    "MsgTraceConfig",
    "__version__",
]
