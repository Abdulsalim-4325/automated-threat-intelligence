from fastapi import APIRouter, HTTPException, Query, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.indicator import IndicatorModel
from app.services.cache_service import cache_service

router = APIRouter()

@router.get("/lookup")
async def lookup_indicator(
    response: Response,
    ioc: str = Query(..., min_length=3, description="Indicator value (IP, domain, or hash)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Look up a specific indicator by its value.
    Checks Redis cache first. On miss, queries PostgreSQL and caches the result.
    """
    # 1. Check Redis Cache
    cached_data = await cache_service.get_indicator(ioc)
    if cached_data:
        response.headers["X-Cache"] = "HIT"
        return cached_data

    # 2. Cache Miss: Query PostgreSQL
    stmt = select(IndicatorModel).where(IndicatorModel.ioc_value == ioc)
    result = await db.execute(stmt)
    indicator = result.scalar_one_or_none()

    if not indicator:
        raise HTTPException(status_code=404, detail=f"Indicator '{ioc}' not found in database")

    # 3. Format the response data
    response_data = {
        "id": indicator.id,
        "stix_id": indicator.stix_id,
        "ioc_type": indicator.ioc_type,
        "ioc_value": indicator.ioc_value,
        "confidence_score": indicator.confidence_score,
        "sighting_count": indicator.sighting_count,
        "sources": indicator.sources,
        "first_seen": indicator.first_seen.isoformat(),
        "last_seen": indicator.last_seen.isoformat(),
        "payload": indicator.stix_payload
    }

    # 4. Store in Cache and Return
    await cache_service.set_indicator(ioc, response_data)
    response.headers["X-Cache"] = "MISS"
    
    return response_data
