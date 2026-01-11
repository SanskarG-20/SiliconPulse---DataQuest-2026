from pydantic import BaseModel
from typing import Optional

# Query models
class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None

class QueryResponse(BaseModel):
    result: str
    timestamp: str

# Inject models
class InjectRequest(BaseModel):
    source: str
    title: str
    content: str
    company: Optional[str] = None
    impact_score: Optional[int] = None

class InjectResponse(BaseModel):
    id: str
    status: str
    timestamp: str

# Signal models
class Signal(BaseModel):
    id: str
    timestamp: str
    source: str
    title: str
    content: str
    impact_score: int
    company: str

# Radar models
class RadarStatus(BaseModel):
    company: str
    status: str
    trend: str
