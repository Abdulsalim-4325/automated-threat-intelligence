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
    
    # Pydantic V2 config syntax
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


# Quick test if run directly
if __name__ == "__main__":
    # Test data
    test_data = {
        "id": 1,
        "ioc_type": "ipv4-addr", 
        "ioc_value": "192.168.1.1",
        "confidence_score": 85.5,
        "sighting_count": 5,
        "sources": ["abuseipdb", "threatfox"],
        "first_seen": "2024-01-01T00:00:00",
        "last_seen": "2024-01-15T12:30:00",
        "payload": {"type": "ipv4-addr", "value": "192.168.1.1"}
    }
    
    indicator = IndicatorResponse(**test_data)
    print("✅ Schema works!")
    # Fixed: Use model_dump_json instead of deprecated json method
    print(indicator.model_dump_json(indent=2))