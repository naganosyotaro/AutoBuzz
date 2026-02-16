from celery import Celery
from app.config import settings

celery_app = Celery(
    "autobuzz",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Tokyo",
    enable_utc=True,
    beat_schedule={
        "collect-buzz-every-hour": {
            "task": "app.workers.tasks.collect_buzz_task",
            "schedule": 3600.0,
        },
        "auto-post-check-every-minute": {
            "task": "app.workers.tasks.auto_post_task",
            "schedule": 60.0,
        },
    },
)
