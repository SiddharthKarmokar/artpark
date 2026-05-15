from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict

class QueryRequest(BaseModel):
    question: str = Field(..., example="What was the closing price of INFY on 2026-04-10?")

class Citation(BaseModel):
    source: str
    record_id: Optional[int] = None
    note: Optional[str] = None

class DisagreementMetadata(BaseModel):
    ticker: str
    date: str
    conflict_type: str
    decision_rule: str
    sources_involved: List[str]

class QueryResponse(BaseModel):
    query_id: str
    answer: str
    value: Optional[float] = None
    chart: Optional[Dict[str, Any]] = None
    citations: List[Citation] = []
    disagreements: List[DisagreementMetadata] = []
    dataset_version: int
    trace_id: str
    execution_time_ms: float
    cache_hit: bool
