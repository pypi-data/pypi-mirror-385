"""Type definitions for AgentBill SDK"""
from typing import TypedDict, Optional


class AgentBillConfig(TypedDict):
    """Configuration for AgentBill SDK"""
    api_key: str  # Required
    base_url: Optional[str]  # Optional
    customer_id: Optional[str]  # Optional
    debug: Optional[bool]  # Optional


class TraceContext(TypedDict):
    """Trace context information"""
    trace_id: str
    span_id: str
    customer_id: Optional[str]
