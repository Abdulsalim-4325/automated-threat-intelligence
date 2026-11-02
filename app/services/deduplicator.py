from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from app.models.indicator import IndicatorModel
from app.services.cache_service import cache_service
from app.services.webhook_notifier import webhook_notifier
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Deduplicator:
    CRITICAL_CONFIDENCE_THRESHOLD = 85

    async def upsert_indicators_batch(
        self, 
        session: AsyncSession, 
        indicators: list[dict]
    ) -> list[dict]:
        """
        Atomic upsert of indicators with cache invalidation and webhook triggers
        """
        results = []
        
        for indicator_data in indicators:
            try:
                existing = await session.execute(
                    select(IndicatorModel).where(
                        IndicatorModel.ioc_value == indicator_data['ioc_value']
                    )
                )
                existing_indicator = existing.scalar_one_or_none()
                
                is_new = existing_indicator is None
                old_score = existing_indicator.confidence_score if existing_indicator else 0
                
                stmt = insert(IndicatorModel).values(**indicator_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=['ioc_value'],
                    set_={
                        'ioc_type': indicator_data['ioc_type'],
                        'last_seen': indicator_data['last_seen'],
                        'sighting_count': indicator_data['sighting_count'],
                        'sources': indicator_data['sources'],
                        'confidence_score': indicator_data['confidence_score'],
                        'updated_at': indicator_data['updated_at'],
                        'payload': indicator_data['payload']
                    }
                )
                await session.execute(stmt)
                await session.commit()
                
                new_score = indicator_data['confidence_score']
                
                if old_score != new_score:
                    await cache_service.invalidate_indicator(indicator_data['ioc_value'])
                
                if is_new or (
                    new_score >= self.CRITICAL_CONFIDENCE_THRESHOLD and 
                    old_score < self.CRITICAL_CONFIDENCE_THRESHOLD
                ):
                    await webhook_notifier.send_critical_alert(
                        indicator_data['ioc_value'],
                        indicator_data['ioc_type'],
                        new_score,
                        is_new
                    )
                
                results.append({
                    'ioc_value': indicator_data['ioc_value'],
                    'is_new': is_new,
                    'score_changed': old_score != new_score,
                    'old_score': old_score,
                    'new_score': new_score
                })
                
            except Exception as e:
                logger.error(f"Error upserting indicator {indicator_data.get('ioc_value')}: {e}")
                await session.rollback()
                continue
        
        return results