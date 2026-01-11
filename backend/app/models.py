from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    """Request model for querying SiliconPulse intelligence"""
    query: str = Field(..., description="The query string to search for")
    k: int = Field(default=5, description="Number of top results to return")


class EvidenceItem(BaseModel):
    """Evidence item from the data stream"""
    timestamp: Optional[str] = Field(None, description="Timestamp of the event")
    source: Optional[str] = Field(None, description="Source of the information")
    title: str = Field(..., description="Title of the evidence")
    snippet: str = Field(..., description="Content snippet or description")
    company: Optional[str] = Field(None, description="Related company name")
    event_type: Optional[str] = Field(None, description="Type of event")


class QueryResponse(BaseModel):
    """Response model for SiliconPulse query results"""
    query: str = Field(..., description="The original query")
    evidence: list[EvidenceItem] = Field(..., description="List of evidence items")
    signal_strength: int = Field(..., description="Strength of the signal (0-100)")
    last_updated: str = Field(..., description="Timestamp of last update")


class InjectRequest(BaseModel):
    """Request model for manually injecting data into the stream"""
    title: str = Field(..., description="Title of the injected item")
    content: str = Field(..., description="Content of the injected item")
    timestamp: Optional[str] = Field(None, description="Timestamp (auto-generated if not provided)")
    source: str = Field(default="ManualInject", description="Source identifier")


class InjectResponse(BaseModel):
    """Response model for data injection"""
    status: str = Field(..., description="Status of the injection operation")
    injected_at: str = Field(..., description="Timestamp when the data was injected")
