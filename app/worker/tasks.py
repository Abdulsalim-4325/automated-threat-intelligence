import asyncio
from datetime import datetime, timezone
from app.worker.celery_app import celery_app
from app.collectors.abuseipdb_collector import AbuseIPDBCollector
from app.collectors.threatfox_collector import ThreatFoxCollector
from app.normalizer.stix_mapper import STIXMapper
from app.normalizer.scoring import calculate_time_decay_confidence
from app.services.deduplicator import upsert_indicators_batch
from app.core.database import AsyncSessionLocal
from app.services.webhook_notifier import webhook_notifier
from app.core.config import settings

async def process_iocs(raw_iocs):
    """Normalizes raw IoCs, triggers alerts for critical threats, and batch upserts."""
    if not raw_iocs:
        return 0
        
    now = datetime.now(timezone.utc)
    processed_data = []
    
    for item in raw_iocs:
        stix_id = STIXMapper.generate_deterministic_id(item["ioc_type"], item["ioc_value"])
        confidence = calculate_time_decay_confidence(item["confidence"], now, 1)
        
        # 🔥 NEW: Trigger Webhook for Critical Threats 🔥
        if confidence >= settings.CRITICAL_CONFIDENCE_THRESHOLD:
            # Fire and forget (don't block the loop)
            asyncio.create_task(
                webhook_notifier.send_alert(
                    ioc_value=item["ioc_value"],
                    ioc_type=item["ioc_type"],
                    confidence=confidence,
                    sources=[item["source"]]
                )
            )
        
        if item["ioc_type"] == "ipv4-addr":
            stix_json = STIXMapper.map_ip_to_indicator(item["ioc_value"], confidence, item["source"])
        elif item["ioc_type"] == "url":
            stix_json = STIXMapper.map_url_to_indicator(item["ioc_value"], confidence, item["source"])
        elif item["ioc_type"] == "file:hashes.'SHA-256'":
            stix_json = STIXMapper.map_hash_to_indicator(item["ioc_value"], confidence, item["source"])
        else:
            continue
            
        processed_data.append({
            "stix_id": stix_id,
            "ioc_value": item["ioc_value"],
            "ioc_type": item["ioc_type"],
            "confidence_score": confidence,
            "sources": [item["source"]],
            "first_seen": now,
            "last_seen": now,
            "stix_payload": stix_json
        })
        
    async with AsyncSessionLocal() as db:
        upserted_count = await upsert_indicators_batch(db, processed_data)
        
    return upserted_count

@celery_app.task(name="app.worker.tasks.task_poll_abuseipdb")
def task_poll_abuseipdb():
    async def run():
        collector = AbuseIPDBCollector()
        iocs = await collector.get_blacklist()
        count = await process_iocs(iocs)
        return f"Processed {count} IoCs from AbuseIPDB"
    return asyncio.run(run())

@celery_app.task(name="app.worker.tasks.task_poll_threatfox")
def task_poll_threatfox():
    async def run():
        collector = ThreatFoxCollector()
        iocs = await collector.get_recent_iocs()
        count = await process_iocs(iocs)
        return f"Processed {count} IoCs from ThreatFox"
    return asyncio.run(run())
