from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Index
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from app.core.database import Base

class IndicatorModel(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stix_id = Column(String(255), unique=True, index=True, nullable=False)
    ioc_value = Column(String(512), nullable=False)
    ioc_type = Column(String(64), nullable=False)  # e.g., ipv4-addr, url, file:hashes.'SHA-256'
    confidence_score = Column(Integer, default=50, nullable=False)
    sighting_count = Column(Integer, default=1, nullable=False)
    sources = Column(ARRAY(String), nullable=False, default=list)

    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Full OASIS STIX 2.1 JSON representation
    stix_payload = Column(JSONB, nullable=False)

    __table_args__ = (
        # Composite unique constraint for atomic upsert deduplication
        Index("idx_ioc_type_value", "ioc_type", "ioc_value", unique=True),
        # PostgreSQL GIN index for high-performance JSONB querying
        Index("idx_stix_payload_gin", "stix_payload", postgresql_using="gin"),
    )