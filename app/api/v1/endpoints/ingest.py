from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.indicator import RawIndicator
from app.normalizer.stix_mapper import STIXMapper
from app.normalizer.scoring import calculate_time_decay_confidence
from app.services.deduplicator import upsert_indicators_batch

router = APIRouter()

@router.post("/import", status_code=201)
async def batch_import_indicators(
    iocs: List[RawIndicator], 
    db: AsyncSession = Depends(get_db)
):
    if not iocs:
        raise HTTPException(status_code=400, detail="Empty payload")

    # 🔥 FIX: Remove tzinfo to make it compatible with TIMESTAMP WITHOUT TIME ZONE
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    processed_data = []

    for item in iocs:
        stix_id = STIXMapper.generate_deterministic_id(item.ioc_type, item.ioc_value)
        confidence = calculate_time_decay_confidence(item.confidence, now, 1)
        
        if item.ioc_type == "ipv4-addr":
            stix_json = STIXMapper.map_ip_to_indicator(item.ioc_value, confidence, item.source)
        elif item.ioc_type == "url":
            stix_json = STIXMapper.map_url_to_indicator(item.ioc_value, confidence, item.source)
        elif item.ioc_type == "file:hashes.'SHA-256'":
            stix_json = STIXMapper.map_hash_to_indicator(item.ioc_value, confidence, item.source)
        else:
            continue
            
        processed_data.append({
            "stix_id": stix_id,
            "ioc_value": item.ioc_value,
            "ioc_type": item.ioc_type,
            "confidence_score": confidence,
            "sources": [item.source],
            "first_seen": now,
            "last_seen": now,
            "stix_payload": stix_json
        })

    upserted_count = await upsert_indicators_batch(db, processed_data)
    
    return {
        "message": "Batch import successful",
        "received": len(iocs),
        "processed": len(processed_data),
        "upserted": upserted_count
    }
