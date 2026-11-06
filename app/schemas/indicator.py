# app/schemas/indicator.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, List
from datetime import datetime

class IndicatorBase(BaseModel):
    """Base schema for indicator data"""
    ioc_type: str = Field(..., description="Type of indicator (ipv4-addr, url, etc)")
    ioc_value: str = Field(..., description="The actual indicator value")
    confidence_score: float = Field(ge=0.1, le=100.0, description="Confidence score 0.1-100")
    sighting_count: int = Field(default=1, ge=1)
    sources: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)

class IndicatorCreate(IndicatorBase):
    """Schema for creating new indicators"""
    pass

class IndicatorResponse(IndicatorBase):
    """Response schema with additional metadata"""
    id: int
    first_seen: datetime
    last_seen: datetime
    payload: Dict[str, Any] = Field(..., description="Full STIX 2.1 payload")
    
    model_config = ConfigDict(from_attributes=True)

class RawIndicator(BaseModel):
    """Schema for incoming raw indicators for batch manual import"""
    ioc_type: str = Field(..., description="Type of indicator (e.g., ipv4-addr, url)")
    ioc_value: str = Field(..., description="The indicator value")
    confidence: int = Field(ge=1, le=100, description="Base confidence score")
    source: str = Field(..., description="Source feed or manual author")
