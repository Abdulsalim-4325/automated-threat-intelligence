from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()


@router.get("/lookup")
async def lookup_indicator(
    ioc: str = Query(..., min_length=3, description="Indicator value (IP, domain, or hash)")
):
    """
    Temporary lookup endpoint stub.
    """
    # Placeholder return for testing routing
    return {
        "message": f"Lookup endpoint reached for IoC: {ioc}",
        "status": "pending_implementation"
    }