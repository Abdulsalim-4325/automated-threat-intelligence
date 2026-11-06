from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models.indicator import IndicatorModel

async def upsert_indicators_batch(db: AsyncSession, indicators_data: List[Dict[str, Any]]) -> int:
    """
    Performs an atomic bulk upsert into PostgreSQL.
    If the indicator (ioc_type, ioc_value) already exists:
      - Updates last_seen
      - Increments sighting_count
      - Overwrites stix_payload and confidence_score
    """
    if not indicators_data:
        return 0

    # Create the base INSERT statement
    stmt = insert(IndicatorModel).values(indicators_data)

    # Define the ON CONFLICT (ioc_type, ioc_value) DO UPDATE action
    update_stmt = stmt.on_conflict_do_update(
        index_elements=["ioc_type", "ioc_value"],
        set_={
            "confidence_score": stmt.excluded.confidence_score,
            "sighting_count": IndicatorModel.sighting_count + 1,
            "last_seen": stmt.excluded.last_seen,
            "sources": stmt.excluded.sources,
            "stix_payload": stmt.excluded.stix_payload
        }
    )

    # Execute the upsert
    result = await db.execute(update_stmt)
    await db.commit()
    
    return result.rowcount
