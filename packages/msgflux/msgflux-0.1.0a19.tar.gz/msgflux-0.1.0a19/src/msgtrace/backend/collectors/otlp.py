"""OTLP collector for receiving traces."""

import asyncio
from typing import Callable, Optional

from msgtrace.backend.storage.base import TraceStorage
from msgtrace.core.parsers.otlp import OTLPParser
from msgtrace.logger import logger


class OTLPCollector:
    """Collector that receives and processes OTLP trace data."""

    def __init__(
        self,
        storage: TraceStorage,
        on_trace_received: Optional[Callable] = None,
    ):
        """Initialize OTLP collector.

        Args:
            storage: Storage backend for traces
            on_trace_received: Optional callback when traces are received
        """
        self.storage = storage
        self.parser = OTLPParser()
        self.on_trace_received = on_trace_received
        self._processing_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._worker_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        """Start the collector worker."""
        if self._running:
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._process_queue())
        logger.info("OTLP collector started")

    async def stop(self) -> None:
        """Stop the collector worker."""
        if not self._running:
            return

        self._running = False
        if self._worker_task:
            await self._processing_queue.join()
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("OTLP collector stopped")

    async def receive_traces(self, otlp_data: dict) -> None:
        """Receive and queue OTLP trace data for processing.

        Args:
            otlp_data: OTLP formatted trace data
        """
        try:
            await self._processing_queue.put(otlp_data)
        except asyncio.QueueFull:
            logger.warning("Processing queue full, dropping trace data")

    async def _process_queue(self) -> None:
        """Worker that processes queued trace data."""
        while self._running:
            try:
                otlp_data = await asyncio.wait_for(
                    self._processing_queue.get(), timeout=1.0
                )

                try:
                    await self._process_otlp_data(otlp_data)
                except Exception as e:
                    logger.error(f"Error processing OTLP data: {e}")
                finally:
                    self._processing_queue.task_done()

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in collector worker: {e}")

    async def _process_otlp_data(self, otlp_data: dict) -> None:
        """Process OTLP data and save to storage.

        Args:
            otlp_data: OTLP formatted trace data
        """
        # Parse OTLP data to spans
        spans = self.parser.parse_spans(otlp_data)

        if not spans:
            return

        # Get affected trace IDs
        trace_ids = list(set(s.trace_id for s in spans))

        # Save spans to storage
        await self.storage.save_spans(spans)

        logger.debug(f"Processed {len(spans)} spans from {len(trace_ids)} traces")

        # Notify callback if set
        if self.on_trace_received and trace_ids:
            try:
                if asyncio.iscoroutinefunction(self.on_trace_received):
                    await self.on_trace_received(trace_ids)
                else:
                    self.on_trace_received(trace_ids)
            except Exception as e:
                logger.error(f"Error in trace received callback: {e}")
