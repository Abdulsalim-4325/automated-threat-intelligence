from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
from app.core.database import get_db
from app.models.indicator import IndicatorModel

router = APIRouter()

@router.get("/bundle")
async def get_stix_bundle(limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Returns a valid STIX 2.1 Bundle containing the highest-confidence indicators.
    """
    # Fetch the highest confidence indicators from the database
    stmt = (
        select(IndicatorModel)
        .order_by(IndicatorModel.confidence_score.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    indicators = result.scalars().all()

    # Extract the STIX payloads from the database records
    stix_objects = [ioc.stix_payload for ioc in indicators if ioc.stix_payload]

    # Wrap in a standard STIX 2.1 Bundle format
    bundle = {
        "type": "bundle",
        "id": f"bundle--{uuid.uuid4()}",
        "objects": stix_objects
    }

    return bundle