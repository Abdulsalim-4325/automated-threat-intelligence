# Automated Threat Intelligence Aggregator & STIX 2.1 Normalization Engine

Asynchronous OSINT threat intelligence ingestion, OASIS STIX 2.1 normalization (`stix2` v3.0.2), PostgreSQL `JSONB` deduplication, Redis cache-aside lookup API, and event-driven SOC webhook alerting.

## Core Architecture
- **Ingestion Layer:** Scheduled OSINT collectors (AlienVault OTX, AbuseIPDB, abuse.ch ThreatFox) orchestrated via **Celery Beat** and **Redis**.
- **Normalization & Scoring Layer:** Deterministic UUIDv5 **OASIS STIX 2.1** SDO/SCO mapping with exponential time-decay confidence scoring.
- **Storage & Deduplication Layer:** Idempotent **PostgreSQL 16** bulk upserts (`ON CONFLICT DO UPDATE`) with **GIN-indexed `JSONB`** payloads.
- **Query & Alerting Layer:** Sub-3ms **FastAPI + Redis** cache-aside reputation lookups and non-blocking `httpx` Discord/Slack SOC webhooks.
