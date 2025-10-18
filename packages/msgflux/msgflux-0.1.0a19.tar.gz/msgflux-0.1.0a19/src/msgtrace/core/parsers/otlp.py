"""Parser for OTLP (OpenTelemetry Protocol) data."""

from typing import Any, Dict, List

from msgtrace.core.models import Span, SpanEvent, SpanStatus


class OTLPParser:
    """Parser for OTLP trace data."""

    @staticmethod
    def parse_spans(otlp_data: Dict[str, Any]) -> List[Span]:
        """Parse OTLP data into Span objects.

        Args:
            otlp_data: OTLP formatted trace data

        Returns:
            List of Span objects
        """
        spans = []
        resource_spans = otlp_data.get("resourceSpans", [])

        for resource_span in resource_spans:
            resource_attrs = OTLPParser._parse_attributes(
                resource_span.get("resource", {}).get("attributes", [])
            )

            scope_spans = resource_span.get("scopeSpans", [])
            for scope_span in scope_spans:
                for otlp_span in scope_span.get("spans", []):
                    span = OTLPParser._parse_span(otlp_span, resource_attrs)
                    spans.append(span)

        return spans

    @staticmethod
    def _parse_span(otlp_span: Dict[str, Any], resource_attrs: Dict[str, Any]) -> Span:
        """Parse a single OTLP span."""
        span_id = OTLPParser._hex_to_string(otlp_span.get("spanId", ""))
        trace_id = OTLPParser._hex_to_string(otlp_span.get("traceId", ""))
        parent_span_id = OTLPParser._hex_to_string(otlp_span.get("parentSpanId", ""))

        if not parent_span_id:
            parent_span_id = None

        attributes = OTLPParser._parse_attributes(otlp_span.get("attributes", []))
        events = OTLPParser._parse_events(otlp_span.get("events", []))
        status = OTLPParser._parse_status(otlp_span.get("status", {}))

        # Map OTLP span kind to string
        kind_map = {
            0: "UNSPECIFIED",
            1: "INTERNAL",
            2: "SERVER",
            3: "CLIENT",
            4: "PRODUCER",
            5: "CONSUMER",
        }
        kind = kind_map.get(otlp_span.get("kind", 1), "INTERNAL")

        return Span(
            span_id=span_id,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            name=otlp_span.get("name", ""),
            kind=kind,
            start_time=int(otlp_span.get("startTimeUnixNano", 0)),
            end_time=int(otlp_span.get("endTimeUnixNano", 0)),
            attributes=attributes,
            events=events,
            status=status,
            resource_attributes=resource_attrs,
        )

    @staticmethod
    def _parse_attributes(otlp_attributes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse OTLP attributes into a dictionary."""
        attributes = {}
        for attr in otlp_attributes:
            key = attr.get("key", "")
            value_obj = attr.get("value", {})

            # Extract value based on type
            if "stringValue" in value_obj:
                value = value_obj["stringValue"]
            elif "intValue" in value_obj:
                value = int(value_obj["intValue"])
            elif "doubleValue" in value_obj:
                value = float(value_obj["doubleValue"])
            elif "boolValue" in value_obj:
                value = bool(value_obj["boolValue"])
            elif "bytesValue" in value_obj:
                value = value_obj["bytesValue"]
            elif "arrayValue" in value_obj:
                value = OTLPParser._parse_array_value(value_obj["arrayValue"])
            elif "kvlistValue" in value_obj:
                value = OTLPParser._parse_attributes(
                    value_obj["kvlistValue"].get("values", [])
                )
            else:
                value = None

            if value is not None:
                attributes[key] = value

        return attributes

    @staticmethod
    def _parse_array_value(array_value: Dict[str, Any]) -> List[Any]:
        """Parse OTLP array value."""
        values = []
        for value_obj in array_value.get("values", []):
            if "stringValue" in value_obj:
                values.append(value_obj["stringValue"])
            elif "intValue" in value_obj:
                values.append(int(value_obj["intValue"]))
            elif "doubleValue" in value_obj:
                values.append(float(value_obj["doubleValue"]))
            elif "boolValue" in value_obj:
                values.append(bool(value_obj["boolValue"]))
        return values

    @staticmethod
    def _parse_events(otlp_events: List[Dict[str, Any]]) -> List[SpanEvent]:
        """Parse OTLP events."""
        events = []
        for otlp_event in otlp_events:
            event = SpanEvent(
                name=otlp_event.get("name", ""),
                timestamp=int(otlp_event.get("timeUnixNano", 0)),
                attributes=OTLPParser._parse_attributes(
                    otlp_event.get("attributes", [])
                ),
            )
            events.append(event)
        return events

    @staticmethod
    def _parse_status(otlp_status: Dict[str, Any]) -> SpanStatus:
        """Parse OTLP status."""
        # Map OTLP status code to string
        status_code_map = {
            0: "UNSET",
            1: "OK",
            2: "ERROR",
        }
        code = status_code_map.get(otlp_status.get("code", 0), "UNSET")
        description = otlp_status.get("message")

        return SpanStatus(status_code=code, description=description)

    @staticmethod
    def _hex_to_string(hex_str: str) -> str:
        """Convert hex string to regular string (for span/trace IDs)."""
        if not hex_str:
            return ""
        # OTLP uses hex encoding for IDs, keep as hex string
        return hex_str
