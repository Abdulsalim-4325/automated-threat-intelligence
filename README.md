# 🛡️ Automated Threat Intelligence Aggregator & STIX 2.1 Engine

An industry-grade, asynchronous Threat Intelligence backend designed to aggregate, deduplicate, score, and normalize Indicators of Compromise (IoCs) into the STIX 2.1 standard. Built for scale, resilience, and automated SIEM integration.

## 🚀 Tech Stack

* **Core:** Python 3.14+, FastAPI (Async)
* **Database:** PostgreSQL 16 (asyncpg) + SQLAlchemy 2.0 with Alembic Migrations
* **Caching & Queues:** Redis 7, Celery + Celery Beat
* **Standards & Intel:** OASIS STIX 2.1 (`stix2`), OSINT Data Processing
* **DevOps / Infra:** Docker, Docker Compose, Multi-stage secure builds

## 🧠 Architectural Highlights

1. **Deterministic Identity Generation:** Utilizes STIX 2.1 `UUIDv5` hashing for idempotent, repeatable IoC identity generation across distributed systems.
2. **Atomic Upserts & Deduplication:** Postgres `ON CONFLICT DO UPDATE` handles concurrent ingestion without race conditions or duplicate records.
3. **Time-Decay Confidence Scoring:** Implements mathematical threat scoring based on multi-source corroboration and temporal decay.
4. **Resilient Async Ingestion:** Uses `httpx` and `tenacity` for exponential backoff retries when reaching out to external threat feeds (AlienVault, AbuseIPDB, ThreatFox).
5. **Secure Containerization:** Employs a multi-stage Dockerfile running as a non-root `appuser` for FAANG-compliant security standards.

## 🐳 Quickstart (Local Deployment)

The entire application stack (API, PostgreSQL, Redis) is orchestrated via Docker Compose.

```bash
# 1. Clone the repository
git clone [https://github.com/Abdulsalim-4325/automated-threat-intelligence.git](https://github.com/Abdulsalim-4325/automated-threat-intelligence.git)
cd automated-threat-intelligence

# 2. Build and launch the stack in the background
docker compose up --build -d

# 3. View API logs to confirm startup
docker compose logs -f api