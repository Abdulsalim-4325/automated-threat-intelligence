from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Initialize Celery using your local Redis container
celery_app = Celery(
    "cti_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"]
)

# Configure Celery serialization and timezone
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Celery Beat Schedule: Automates polling tasks
celery_app.conf.beat_schedule = {
    "poll-abuseipdb-every-60-mins": {
        "task": "app.worker.tasks.task_poll_abuseipdb",
        "schedule": crontab(minute="0"),  # Runs at the top of every hour
    },
    "poll-threatfox-every-30-mins": {
        "task": "app.worker.tasks.task_poll_threatfox",
        "schedule": crontab(minute="*/30"),  # Runs every 30 minutes
    },
}