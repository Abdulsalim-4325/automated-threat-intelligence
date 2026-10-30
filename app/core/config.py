from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Automated Threat Intelligence & STIX 2.1 Engine"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str
    CACHE_TTL_SECONDS: int = 900

    # API Keys
    OTX_API_KEY: str
    ABUSEIPDB_API_KEY: str
    THREATFOX_API_KEY: str

    # Alerting
    DISCORD_WEBHOOK_URL: str
    CRITICAL_CONFIDENCE_THRESHOLD: int = 85

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()