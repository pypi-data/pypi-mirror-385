"""OpenTelemetry Tracer for AgentBill"""
import json
import time
import uuid
import httpx
from typing import Dict, Any, Optional
from .types import AgentBillConfig


class Span:
    """Represents an OpenTelemetry span"""
    
    def __init__(self, name: str, trace_id: str, span_id: str, attributes: Dict[str, Any]):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.attributes = attributes
        self.start_time = time.time_ns()
        self.end_time: Optional[int] = None
        self.status = {"code": 0}
    
    def set_attributes(self, attributes: Dict[str, Any]):
        self.attributes.update(attributes)
    
    def set_status(self, code: int, message: str = ""):
        self.status = {"code": code, "message": message}
    
    def end(self):
        self.end_time = time.time_ns()


class AgentBillTracer:
    """OpenTelemetry tracer for AgentBill"""
    
    def __init__(self, config: AgentBillConfig):
        self.config = config
        self.base_url = config.get("base_url", "https://uenhjwdtnxtchlmqarjo.supabase.co")
        self.api_key = config["api_key"]
        self.customer_id = config.get("customer_id")
        self.debug = config.get("debug", False)
        self.spans = []
    
    def start_span(self, name: str, attributes: Dict[str, Any]) -> Span:
        """Start a new span"""
        trace_id = str(uuid.uuid4()).replace("-", "")
        span_id = str(uuid.uuid4()).replace("-", "")[:16]
        
        attributes["service.name"] = "agentbill-python-sdk"
        if self.customer_id:
            attributes["customer.id"] = self.customer_id
        
        span = Span(name, trace_id, span_id, attributes)
        self.spans.append(span)
        return span
    
    def flush_sync(self):
        """Synchronous flush for non-async contexts"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, schedule the task
                asyncio.create_task(self.flush())
            else:
                # If no loop, run it
                loop.run_until_complete(self.flush())
        except RuntimeError:
            # No event loop exists, create one
            asyncio.run(self.flush())
    
    async def flush(self):
        """Flush spans to AgentBill"""
        if not self.spans:
            if self.debug:
                print("AgentBill: No spans to flush")
            return
        
        payload = self._build_otlp_payload()
        url = f"{self.base_url}/functions/v1/otel-collector"
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
        
        if self.debug:
            print(f"AgentBill: Flushing {len(self.spans)} spans to {url}")
            print(f"AgentBill: API Key: {self.api_key[:12]}...")
            print(f"AgentBill: Full headers being sent: {headers}")
            print(f"AgentBill: Payload preview: {str(payload)[:200]}...")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                
                if self.debug:
                    print(f"AgentBill flush response code: {response.status_code}")
                    print(f"AgentBill response headers: {dict(response.headers)}")
                    print(f"AgentBill response body: {response.text[:500]}")
                
                if response.status_code == 200:
                    self.spans.clear()
                    if self.debug:
                        print("AgentBill: ✅ Spans successfully flushed")
                else:
                    if self.debug:
                        print(f"AgentBill: ❌ Flush failed with status {response.status_code}")
            except Exception as e:
                if self.debug:
                    print(f"AgentBill flush error: {type(e).__name__}: {e}")
    
    def _build_otlp_payload(self) -> Dict[str, Any]:
        """Build OTLP export payload"""
        return {
            "resourceSpans": [{
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "agentbill-python-sdk"}},
                        {"key": "service.version", "value": {"stringValue": "1.0.0"}}
                    ]
                },
                "scopeSpans": [{
                    "scope": {"name": "agentbill", "version": "1.0.0"},
                    "spans": [self._span_to_otlp(span) for span in self.spans]
                }]
            }]
        }
    
    def _span_to_otlp(self, span: Span) -> Dict[str, Any]:
        """Convert span to OTLP format"""
        return {
            "traceId": span.trace_id,
            "spanId": span.span_id,
            "name": span.name,
            "kind": 1,  # CLIENT
            "startTimeUnixNano": str(span.start_time),
            "endTimeUnixNano": str(span.end_time or time.time_ns()),
            "attributes": [
                {"key": k, "value": self._value_to_otlp(v)}
                for k, v in span.attributes.items()
            ],
            "status": span.status
        }
    
    def _value_to_otlp(self, value: Any) -> Dict[str, Any]:
        """Convert value to OTLP format"""
        if isinstance(value, str):
            return {"stringValue": value}
        elif isinstance(value, (int, float)):
            return {"intValue": int(value)}
        elif isinstance(value, bool):
            return {"boolValue": value}
        else:
            return {"stringValue": str(value)}
